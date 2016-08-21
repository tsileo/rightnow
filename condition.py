# coding: utf-8
import logging
from math import radians, cos, sin, asin, sqrt

from aenum import Enum

from published import published


class DayEnum(Enum):
    MONDAY = 'mon'
    TUESDAY = 'tue'
    WEDNESDAY = 'wed'
    THURSDAY = 'thu'
    FRIDAY = 'fri'
    SATURDAY = 'sat'
    SUNDAY = 'sun'

DAY_VALUE = {
    DayEnum.MONDAY.value: 0,
    DayEnum.TUESDAY.value: 1,
    DayEnum.WEDNESDAY.value: 2,
    DayEnum.THURSDAY.value: 3,
    DayEnum.FRIDAY.value: 4,
    DayEnum.SATURDAY.value: 5,
    DayEnum.SUNDAY.value: 6,
}


class DayRange(object):
    def __init__(self, start, end):
        """Takes two DayEnum as args.

        >>> DayRange(DayEnum.MONDAY, DayEnum.FRIDAY)

        """
        self.start = start.value
        self.end = end.value

    def check(self, dt, _):
        dt_day = DayEnum(dt.strftime('%a').lower()).value
        return DAY_VALUE.get(self.start) <= DAY_VALUE.get(dt_day) <= DAY_VALUE.get(self.end)


class HourRange(object):
    def __init__(self, start, end):
        """Takes two hours at %H%M%S format.

        >>> HourRange('080000', '220000')

        """
        self.start = start
        self.end = end

    def check(self, dt, _):
        return self.start < dt.strftime('%H%M%S') < self.end

# TODO(tsileo): HourRange, MatchCalendar (with reverse, i.e not a specific tag)


class WithinLocation(object):

    def __init__(self, location, distance=10):
        """Distance is in kilometers."""
        self.location = location
        self.distance = distance

    def check(self, dt, _):
        gps_data = published.get('gps')
        if not gps_data:
            logging.warn('no last location for WithinLocation check %s', self)
            return False
        last_location = gps_data.get('last')
        dist = self._haversine(last_location.get('lon'), last_location.get('lat'),
                               self.location.get('lon'), self.location.get('lat'))
        print dist
        return dist < self.distance

    @staticmethod
    def _haversine(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers. Use 3956 for miles
        return c * r
