
from datetime import datetime
import re

from dateutil import parser
import pytz
import six

UTC_EPOCH = datetime(1970, 1, 1).replace(tzinfo=pytz.utc)
MAX_POSIX_TIMESTAMP = pow(2, 32) - 1


class timestamp_ms(object):
    """Build UTC timestamp in milliseconds
    """

    @classmethod
    def feeling_lucky(cls, obj):
        """Tries to convert given object to an UTC timestamp is ms, based
        on its type.
        """
        if isinstance(obj, six.string_types):
            return cls.from_str(obj)
        elif isinstance(obj, six.integer_types) and obj <= MAX_POSIX_TIMESTAMP:
            return cls.from_posix_timestamp(obj)
        elif isinstance(obj, datetime):
            return cls.from_datetime(obj)
        else:
            raise ValueError("Don't know how to get timestamp")

    @classmethod
    def from_str(cls, timestr):
        """Use `dateutil` module to parse the give string
        """
        return cls.from_datetime(parser.parse(timestr))

    @classmethod
    def from_ymd(cls, year, month=1, day=1):
        return cls.from_datetime(datetime(
            year=year, month=month, day=day
        ))

    @classmethod
    def from_posix_timestamp(cls, ts):
        return cls.from_datetime(datetime.utcfromtimestamp(ts))

    @classmethod
    def from_datetime(cls, date):
        if date.tzinfo is None:
            date = date.replace(tzinfo=pytz.utc)
        seconds = (date - UTC_EPOCH).total_seconds() * 1e3
        micro_seconds = date.microsecond / 1e3
        return int(seconds + micro_seconds)

    @classmethod
    def from_imap_header(cls, date_header_value):
        if re.match(r".*\d{4}.*\d{4}", date_header_value):
            # replace '-0000' timezone information to '-00:00'
            value = re.sub(
                r"(.*)(\s+[\+-]?\d\d)(\d\d).*$",
                r"\1 \2:\3",
                date_header_value
            )
        else:
            value = date_header_value
        try:
            return cls.from_str(value)
        except ValueError:
            if re.match(r".*[\-+]?\d{2}:\d{2}$", value):
                value = re.sub(
                    r"(.*)(\s[\+-]?\d\d:\d\d)$",
                    r"\1",
                    value
                )
            return cls.from_str(value)

    @classmethod
    def now(cls):
        return cls.from_datetime(datetime.utcnow())
