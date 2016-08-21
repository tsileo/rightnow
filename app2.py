# coding: utf-8
import logging
import os
from datetime import datetime, timedelta

import inflection
from flask import Flask, request, jsonify, g, render_template
from flask_cors import CORS
import requests_cache
from auth import auth

from config import CONFIG
from gps import GPS
from weather import Weather
from navitia import Navitia
from condition import DayRange, DayEnum, HourRange

logging.basicConfig(level=logging.INFO)

requests_cache.install_cache('requests.db', backend='sqlite', expire_after=300)

app = Flask(__name__)
CORS(app)

events = {}

def json_error(message):
    """Util func to returns an error 500 with a JSON Object."""
    res = jsonify(message=message)
    res.status_code = 500
    return res

def register(event):
    event_name = inflection.underscore(event.__name__)
    e = event()
    e.config = {}
    for conf in e.SHARED_CONF:
        e.config.update(CONFIG.get(conf, {}))
        logging.info('%s/%s', conf, e.config)
    e.config.update(CONFIG.get(event_name, {}))
    e.post_init()
    e.register(app)
    events[event_name] = e

class MyNavitia(Navitia):
    STOP_AREA = 'OCE:SA:87118000'
    DEPARTURE_TIME = '092000'
    SHARED_CONF = ['navitia']
    CONDITIONS = [
        DayRange(DayEnum.MONDAY, DayEnum.THURSDAY),
        HourRange('070000', '100000'),
    ]

class MyNavitia2(Navitia):
    STOP_AREA = 'OCE:SA:87113001'
    DEPARTURE_TIME = '194200'
    SHARED_CONF = ['navitia']
    CONDITIONS = [
        DayRange(DayEnum.MONDAY, DayEnum.THURSDAY),
        HourRange('110000', '210000'),
    ]

# class MyWeather(Weather):
#     def get_location(self):
#         return published.get('gps').get('last')

# TODO(tsileo): get the current calendar event published

register(MyNavitia)
register(MyNavitia2)
register(GPS)
register(Weather)

print events

@app.route('/')
@auth.login_required
def index():
    dt = datetime.now()
    cards = []
    for event in events.values():
        if event.HAS_CARDS and event.check_conditions(dt, {}):
            cards.extend(event.cards(dt))
    print cards

    return render_template('index.html', cards=cards)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8060, threaded=False)
