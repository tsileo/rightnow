# coding: utf-8
from flask import request
from auth import auth
from data_type import EventType


class GPS(EventType):
    WITH_DATASTORE = True
    PUBLISHER = True

    def __init__(self, config):
        self.config = config
        super(GPS, self).__init__()

    def before_register(self):
        self.blueprint.add_url_rule('/', 'index', self.hello)
        self.blueprint.add_url_rule('/append/'+self.config.get('append_path'), 'append', self.append)
    @auth.login_required
    def hello(self):
        return 'hello'

    # @auth.login_required
    def append(self):
        if 'tracker' in request.args:
            print 'tracker', request.args.get('tracker')

        data = dict(
            lat=float(request.args.get('lat')),
            lon=float(request.args.get('lon')),
        )
        self.db.input(data)
        self.publish('last', data)
        return ''
