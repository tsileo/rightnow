# coding: utf-8
import logging

import requests
from flask import request

from auth import auth
from data_type import EventType
from published import published


def reverse_geocoding(lat, lon):
    resp = requests.get('http://192.168.3.108:8088/?lat={}&lon={}'.format(lat, lon)).json()
    return resp


class GPS(EventType):
    WITH_DATASTORE = True
    PUBLISHER = True

    def post_init(self):
        self.publish('last', self.db.latest())

    def before_register(self):
        self.blueprint.add_url_rule('/', 'index', self.hello)
        self.blueprint.add_url_rule('/append/'+self.config.get('append_path'), 'append', self.append)

    def latest(self):
        data = self.db.latest()
        rgeo = reverse_geocoding(data['lat'], data['lon'])
        data['rgeo'] = rgeo
        return data

    @auth.login_required
    def hello(self):
        print published
        data = self.latest()
        return self.jsonify(**data)

    # @auth.login_required
    def append(self):
        if 'tracker' in request.args:
            print 'tracker', request.args.get('tracker')
            return ''

        data = dict(
            lat=float(request.args.get('lat')),
            lon=float(request.args.get('lon')),
        )
        logging.info('received GPS data')
        self.db.insert(data)
        self.publish('last', data)
        return ''
