
from datetime import datetime
import re

from dateutil import parser
import pytz

UTC_EPOCH = datetime(1970, 1, 1).replace(tzinfo=pytz.utc)


class timestamp_ms(object):
    """Build UTC timestamp in milliseconds
    """

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
        return (date - UTC_EPOCH).total_seconds() * 1e3 + \
            date.microsecond / 1e3

    @classmethod
    def from_imap_header(cls, date_header_value):
        if re.match(r".*\d{4}.*\d{4}", date_header_value):
            # replace '-0000' timezone information to '-00:00'
            date_header_value = re.sub(
                r"(.*)(\s+[\+-]?\d\d)(\d\d).*$",
                r"\1 \2:\3",
                date_header_value
            )
        return cls.from_str(date_header_value)

    @classmethod
    def now(cls):
        return cls.from_datetime(datetime.utcnow())
