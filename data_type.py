# coding: utf-8
import json
from datetime import datetime

from flask import Blueprint, current_app
import pystache
import inflection

from published import published
from datastore import DataStore

# TODO(tsileo): handle a local state stored in a JSON object


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")


class EventType(object):
    WITH_DATASTORE = False
    PUBLISHER = False
    HAS_CARDS = False
    CONDITIONS = []
    SHARED_CONF = []

    def __init__(self):
        # Init default values
        self.db = None
        self.config = {}
        # Get the snake case version of the current class
        self._klass = inflection.underscore(self.__class__.__name__)

        # Check if the class requested a datastore
        if self.WITH_DATASTORE:
            self.db = DataStore(self._klass)

        if self.PUBLISHER:
            self._published = {}
            published[self._klass] = self._published

        # Init the Flask Blueprint
        self.blueprint = Blueprint(self._klass, self._klass)

    def check_conditions(self, dt, data):
        """Will check the for dynamic condition `should_display` and the embedded `CONDITIONS`."""
        out = self.should_display(dt, data)
        for cond in conditions:
            out = out and cond.check(dt, data)
        return out

    def post_init(self):
        """Will be executed right afte the configuration is loaded in `self.config` as a dict,
        from the YAML case (e.g. GPS module will get root_config.get('gps', {}).
        Module will be converted from camel case to snake case."""
        return

    def publish(self, k, v):
        """Shortcut for publishing data in the Event namespace."""
        self._published[k] = v

    def jsonify(self, *args, **kwargs):
        """Flask jsonify version that encode `datetime.datetime` as isoformat string."""
        return current_app.response_class(json.dumps(dict(*args, **kwargs), default=json_serial),
                                          mimetype='application/json')

    def should_display(self, dt, data):
        """Dynamic condition meant to be subclassed, used by `check_conditions`."""
        return True

    def priority(self, dt, data):
        """Dynamic priority weight meant to be suclassed to change the display order of cards."""
        return int(dt.strftime('%s'))

    def close(self):
        if self.db:
            return self.db.close()

    def before_register(self):
        """Meant to be subclassed for registering API endpoint via `self.blueprint`.

        >>>  self.blueprint.add_url_rule('/', 'index', self.hello)

        """
        return

    def register(self, app):
        """Register the app endpoint. only used internally."""
        self.before_register()
        app.register_blueprint(self.blueprint, url_prefix='/'+self._klass)

    def render_card_html(self, tpl, ctx):
        "Shortcut for rendering a Mustache template."""
        return pystache.render(tpl, ctx)
