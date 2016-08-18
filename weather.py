# coding: utf-8
import requests
from flask import Markup

from datetime import datetime
from data_type import EventType
from auth import auth
from published import published
from gps import reverse_geocoding


class Weather(EventType):
    HAS_CARDS = True

    def before_register(self):
        self.blueprint.add_url_rule('/', 'index', self.hello)

    @auth.login_required
    def hello(self):
        data = self.fetch()
        return self.jsonify(**data)

    def fetch(self):
        gps = published.get('gps', {}).get('last', {})
        if not gps:
            return

        # Use the reverse geocoding for "anonymizing" our GPS coordinates
        agps = reverse_geocoding(gps['lat'], gps['lon'])

        w = requests.get('https://api.forecast.io/forecast/{}/{},{}?units=si'.format(
            self.config.get('forecast_api_key'),
            agps.get('lat'),
            agps.get('lon'),
        )).json()

        w['reverse_geo'] = agps

        return w

    def cards(self):
        data = self.fetch()
        w = data.get('currently')
        raw_daily = data.get('daily', {}).get('data', [])
        daily = []
        for d in raw_daily:
            dt = datetime.fromtimestamp(float(d['time']))
            daily.append(dict(
                day=dt.strftime('%a'),
                icon=d['icon'],
                tempMax=int(d['temperatureMax']),
                tempMin=int(d['temperatureMin']),
            ))

        html = self.render_card_html(
        """<h1 style="margin:0">{{place}}</h1>
        <h2 style="margin:0 0 20px 0">{{summary}}</h2>
        <div style="display:flex;">
        <div style="flex: 2;">
        <i style="font-size:5em;" class="wi wi-forecast-io-{{icon}}"></i>
        </div>
            <div style="flex: 1;font-size:2.5em;padding-top:20px;">{{temperature}}</div>
            <div style="flex: 1;font-size:1.2em;padding-top:25px;"><span style="padding:10px">&deg;C</span></div>
        </div>
        <div style="display:flex;">
        {{#daily}}
        <div style="flex: 1;margin-top:30px;">
        <div style="font-size:0.8em;color:#ccc;padding-bottom:10px;">{{day}}</div>
        <i class="wi wi-forecast-io-{{icon}}"></i>
        <div style="font-size:0.5em;color:#ccc;margin-top:10px;"><span style="color:#888;">{{tempMax}}</span> {{tempMin}}</div>
        </div>
        {{/daily}}
        </div>
        """,
        dict(
            place=data.get('reverse_geo', {}).get('reverse_geocoding'),
            icon=w.get('icon'),
            summary=w.get('summary'),
            temperature=w.get('temperature'),
            daily=daily,
        ))
        return [dict(
            icon='fa-sun-o',
            title='Weather',
            html=html,
        )]
