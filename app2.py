# coding: utf-8
import os
from datetime import datetime

import inflection
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from config import CONFIG
from gps import GPS

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
    e = event(CONFIG.get(event_name, {}))
    e.register(app)
    events[event_name] = e

register(GPS)

print events

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8060, threaded=False)
