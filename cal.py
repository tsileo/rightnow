# coding: utf-8
from datetime import datetime, timedelta

import caldav

from data_type import EventType
# from auth import auth


class Cal(EventType):
    """Caldav client."""

    def post_init(self):
        self.client = caldav.DAVClient(self.config.get('caldav_api_url'))

    def get_events(self):
        p = self.client.principal()
        cals = p.calendars()
        now = datetime.utcnow()
        res = []
        for cal in cals:
            events = cal.date_search(now, now + timedelta(days=45))
            for event in events:
                vevent = event.instance.vevent
                edict = dict(
                    dtstart=vevent.dtstart.value,
                    dtend=vevent.dtend.value,
                )
                valarm = dict()
                for attr in ['location', 'summary']:
                    try:
                        edict['attr'] = getattr(vevent, attr).value
                    except AttributeError:
                        pass
                try:
                    raw_valarm = vevent.valarm
                    # FIXME(tsileo): handle multiple vevent alarm
                    valarm = dict(
                        trigger=raw_valarm.trigger.value,
                        action=raw_valarm.action.value,
                    )
                    if valarm['action'] == u'DISPLAY':
                        valarm['description'] = raw_valarm.description.value
                except AttributeError:
                    pass
                edict['valarm'] = valarm
                res.append(edict)
        return res
