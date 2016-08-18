# coding: utf-8
from flask import Blueprint
import inflection

from published import published
from datastore import DataStore

# TODO(tsileo): handle a local state stored in a JSON object


class EventType(object):
    WITH_DATASTORE = False
    PUBLISHER = False
    HAS_CARDS = False

    def __init__(self):
        # Init default values
        self.db = None
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

    def publish(self, k, v):
        self._published[k] = v

    def close(self):
        if self.db:
            return self.db.close()

    def before_register(self):
        return

    def register(self, app):
        self.before_register()
        app.register_blueprint(self.blueprint, url_prefix='/'+self._klass)
