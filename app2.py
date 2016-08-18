# coding: utf-8
import logging
import os
from datetime import datetime

import inflection
from flask import Flask, request, jsonify, g, render_template
from flask_cors import CORS
import requests_cache
from auth import auth

from config import CONFIG
from gps import GPS
from weather import Weather

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
    e.config = CONFIG.get(event_name, {})
    e.post_init()
    e.register(app)
    events[event_name] = e

register(GPS)
register(Weather)

print events

@app.route('/')
@auth.login_required
def index():
    cards = []
    for event in events.values():
        if event.HAS_CARDS:
            print event.cards()
            cards.extend(event.cards())
    print cards

    return render_template('index.html', cards=cards)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8060, threaded=False)
