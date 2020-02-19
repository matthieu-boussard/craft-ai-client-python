import unittest
from datetime import datetime
import pytz

from craft_ai import Time
from craft_ai.errors import CraftAiTimeError


class TestTime(unittest.TestCase):
    def test_init(self):
        try:
            time = Time(timezone="+05:00")
            self.assertEqual(time.timezone, "+05:00")
        except CraftAiTimeError as e:
            self.fail(e)
        try:
            Time()
        except CraftAiTimeError as e:
            self.fail(e)

    def test_timezone_format(self):
        self.assertEqual(Time(timezone="+01:00").timezone, "+01:00")
        self.assertEqual(Time(timezone="CET").timezone, "+01:00")
        self.assertEqual(Time(1356998400, timezone="+0100").timezone, "+01:00")
        self.assertEqual(Time(1356998400, timezone="+01").timezone, "+01:00")
        self.assertEqual(Time(1356998400, timezone="-0600").timezone, "-06:00")
        self.assertEqual(Time(1356998400, timezone="CST").timezone, "-06:00")
        self.assertEqual(Time("1977-04-22T01:00:00-0300").timezone, "-03:00")
        self.assertEqual(Time("1977-04-22T01:00:00+1000").timezone, "+10:00")
        self.assertEqual(Time("2011-04-22 01:00:00+0900").timezone, "+09:00")
        self.assertEqual(
            Time(t="2017-01-01 00:00:00", timezone="-03:00").timezone, "-03:00"
        )
        self.assertEqual(
            Time(t="2017-01-01 03:00:00", timezone="+02:00").timezone, "+02:00"
        )
        self.assertEqual(
            Time(t=datetime(2011, 1, 1, 0, 0), timezone="+02:00").timezone, "+02:00"
        )
        self.assertEqual(Time(t="2017-01-01 03:00:00", timezone=120).timezone, "+02:00")
        self.assertEqual(
            Time(t="2017-01-01 03:00:00", timezone=-120).timezone, "-02:00"
        )
        self.assertEqual(Time(t="2017-01-01 03:00:00", timezone=-2).timezone, "-02:00")
        self.assertEqual(
            Time(t=datetime(2012, 9, 12, 6, 0, 0, tzinfo=pytz.utc)).timezone, "+00:00"
        )
        self.assertEqual(Time().timezone, Time().timezone)

    def test_parser_format(self):
        # No timezone
        self.assertRaises(CraftAiTimeError, Time, "2010-01-01T07:30:30")
        self.assertRaises(CraftAiTimeError, Time, datetime(2011, 1, 1, 0, 0))
        # Not ISO format
        self.assertRaises(CraftAiTimeError, Time, "22-04-1977T01:00:00+0100")
        # Two timezones
        self.assertRaises(CraftAiTimeError, Time, "2011-04-22 01:00:00+0900", "-03:00")
        self.assertRaises(
            CraftAiTimeError,
            Time,
            datetime(2002, 10, 27, 6, 0, 0, tzinfo=pytz.utc),
            pytz.utc,
        )
        # Invalid UTC offset
        self.assertRaises(CraftAiTimeError, Time, "2011-04-22 01:00:00+0900", -950)
        self.assertRaises(CraftAiTimeError, Time, "2011-04-22 01:00:00+0900", 950)
