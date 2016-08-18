# coding: utf-8
import requests
from flask import Markup

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

        return w

    def cards(self):
        data = self.fetch()
        w = data.get('currently')
        html = self.render_card_html("""<h1>{{summary}}</h1>
         <i style="font-size:3em;" class="wi wi-forecast-io-{{icon}}"></i> """, dict(
            icon=w.get('icon'),
            summary=w.get('summary'),
        ))
        return [dict(
            icon='fa-sun-o',
            title='Weather',
            html=html,
        )]
