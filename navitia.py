# coding: utf-8
import logging
from datetime import datetime, timedelta

import requests

from data_type import EventType
from auth import auth

# XXX(tsileo): filter by headsign?

class Navitia(EventType):
    HAS_CARDS = True
    STOP_AREA = None
    DEPARTURE_TIME = None  # departure time must in %H%M%S format, and before the actual departure.

    def before_register(self):
        self.blueprint.add_url_rule('/', 'index', self.hello)

    @auth.login_required
    def hello(self):
        data = self._parse_data(self.get_data(datetime.now()))
        return self.jsonify(**data)

    def _do_req(self, endpoint):
        logging.info('%s/%s', self.config, endpoint)
        resp = requests.get('{}/{}{}'.format(
            self.config.get('navitia_api_url'),
            self.config.get('navitia_coverage'),
            endpoint
        ), auth=(self.config.get('navitia_api_key'), ''))
        resp.raise_for_status()
        return resp.json()

    def get_data(self, dt):
        return self._do_req('/stop_areas/stop_area:{}/departures?from_datetime={}T{}&duration=3600'.format(
            self.STOP_AREA,
            dt.strftime('%Y%m%d'),
            self.DEPARTURE_TIME,
        ))

    @staticmethod
    def _parse_data(data):
        departure = data['departures'][0]
        name = u'{physical_mode} {network} {commercial_mode}'.format(**departure['display_informations'])
        headsign = departure['display_informations']['headsign']
        direction = departure['display_informations']['direction']
        stop_date_time =  departure['stop_date_time']
        base_departure_datetime = datetime.strptime(stop_date_time['base_departure_date_time'], '%Y%m%dT%H%M%S')
        departure_datetime = datetime.strptime(stop_date_time['departure_date_time'], '%Y%m%dT%H%M%S')
        delayed = stop_date_time['base_departure_date_time'] != stop_date_time['departure_date_time']
        return dict(
            name=name,
            headsign=headsign,
            direction=direction,
            base_departure_datetime=base_departure_datetime,
            departure_datetime=departure_datetime,
            delayed=delayed,
            delay=(departure_datetime - base_departure_datetime).seconds / 60,
        )

    def cards(self):
        data = self._parse_data(self.get_data(datetime.now() + timedelta(seconds=3600*8)))
        data['departure_datetime'] = data['departure_datetime'].strftime('%H:%M')
        data['base_departure_datetime'] = data['base_departure_datetime'].strftime('%H:%M')
        html = self.render_card_html(
        """<h1 style="margin:0">{{name}} <small style="color:#ccc;">{{headsign}}</small></h1>
        <h2 style="margin:0 0 20px 0">{{direction}}</h2>
        {{#delayed}}
        <div>Delayed (initially {{base_departure_datetime}}).<br>
        {{/delayed}}
        <div style="font-size:3em;text-align:center;margin:20px 0;{{#delayed}}color:#FF4136;{{/delayed}}">{{departure_datetime}}</div>
        {{#delayed}}
        <div><i class="fa fa-clock-o" aria-hidden="true"></i> <strong>{{delay}}</strong> minutes late.</div>
        {{/delayed}}
        """,
        dict(
            **data
        ))
        return [dict(
            icon='fa-train',
            title='Trains',
            html=html,
        )]

