#
# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import unittest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import fuzzy_match
from lingua_franca.parse import get_gender
from lingua_franca.parse import match_one
from lingua_franca.parse import normalize
from lingua_franca.time import DAYS_IN_1_YEAR, DAYS_IN_1_MONTH
from lingua_franca.parse import DurationResolution


class TestFuzzyMatch(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(fuzzy_match("you and me", "you and me") >= 1.0)
        self.assertTrue(fuzzy_match("you and me", "you") < 0.5)
        self.assertTrue(fuzzy_match("You", "you") > 0.5)
        self.assertTrue(fuzzy_match("you and me", "you") ==
                        fuzzy_match("you", "you and me"))
        self.assertTrue(fuzzy_match("you and me", "he or they") < 0.2)

    def test_match_one(self):
        # test list of choices
        choices = ['frank', 'kate', 'harry', 'henry']
        self.assertEqual(match_one('frank', choices)[0], 'frank')
        self.assertEqual(match_one('fran', choices)[0], 'frank')
        self.assertEqual(match_one('enry', choices)[0], 'henry')
        self.assertEqual(match_one('katt', choices)[0], 'kate')
        # test dictionary of choices
        choices = {'frank': 1, 'kate': 2, 'harry': 3, 'henry': 4}
        self.assertEqual(match_one('frank', choices)[0], 1)
        self.assertEqual(match_one('enry', choices)[0], 4)


class TestNormalize(unittest.TestCase):
    def test_articles(self):
        self.assertEqual(normalize("this is a test", remove_articles=True),
                         "this is test")
        self.assertEqual(normalize("this is the test", remove_articles=True),
                         "this is test")
        self.assertEqual(normalize("and another test", remove_articles=True),
                         "and another test")
        self.assertEqual(normalize("this is an extra test",
                                   remove_articles=False),
                         "this is an extra test")

    def test_extract_number(self):
        self.assertEqual(extract_number("this is the first test",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("this is 2 test"), 2)
        self.assertEqual(extract_number("this is second test",
                                        ordinals=True), 2)
        self.assertEqual(extract_number("this is the third test"), 1.0 / 3.0)
        self.assertEqual(extract_number("this is the third test",
                                        ordinals=True), 3.0)
        self.assertEqual(extract_number("the fourth one", ordinals=True), 4.0)
        self.assertEqual(extract_number("the thirty sixth one",
                                        ordinals=True), 36.0)
        self.assertEqual(extract_number("this is test number 4"), 4)
        self.assertEqual(extract_number("one third of a cup"), 1.0 / 3.0)
        self.assertEqual(extract_number("three cups"), 3)
        self.assertEqual(extract_number("1/3 cups"), 1.0 / 3.0)
        self.assertEqual(extract_number("quarter cup"), 0.25)
        self.assertEqual(extract_number("1/4 cup"), 0.25)
        self.assertEqual(extract_number("one fourth cup"), 0.25)
        self.assertEqual(extract_number("2/3 cups"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 cups"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 and 3/4 cups"), 1.75)
        self.assertEqual(extract_number("1 cup and a half"), 1.5)
        self.assertEqual(extract_number("one cup and a half"), 1.5)
        self.assertEqual(extract_number("one and a half cups"), 1.5)
        self.assertEqual(extract_number("one and one half cups"), 1.5)
        self.assertEqual(extract_number("three quarter cups"), 3.0 / 4.0)
        self.assertEqual(extract_number("three quarters cups"), 3.0 / 4.0)
        self.assertEqual(extract_number("twenty two"), 22)
        self.assertEqual(extract_number(
            "Twenty two with a leading capital letter"), 22)
        self.assertEqual(extract_number(
            "twenty Two with Two capital letters"), 22)
        self.assertEqual(extract_number(
            "twenty Two with mixed capital letters"), 22)
        self.assertEqual(extract_number("Twenty two and Three Fifths"), 22.6)
        self.assertEqual(extract_number("two hundred"), 200)
        self.assertEqual(extract_number("nine thousand"), 9000)
        self.assertEqual(extract_number("six hundred sixty six"), 666)
        self.assertEqual(extract_number("two million"), 2000000)
        self.assertEqual(extract_number("two million five hundred thousand "
                                        "tons of spinning metal"), 2500000)
        self.assertEqual(extract_number("six trillion"), 6000000000000.0)
        self.assertEqual(extract_number("six trillion", short_scale=False),
                         6e+18)
        self.assertEqual(extract_number("one point five"), 1.5)
        self.assertEqual(extract_number("three dot fourteen"), 3.14)
        self.assertEqual(extract_number("zero point two"), 0.2)
        self.assertEqual(extract_number("billions of years older"),
                         1000000000.0)
        self.assertEqual(extract_number("billions of years older",
                                        short_scale=False),
                         1000000000000.0)
        self.assertEqual(extract_number("one hundred thousand"), 100000)
        self.assertEqual(extract_number("minus 2"), -2)
        self.assertEqual(extract_number("negative seventy"), -70)
        self.assertEqual(extract_number("thousand million"), 1000000000)
        self.assertEqual(extract_number("sixth third"),
                         1 / 6 / 3)
        self.assertEqual(extract_number("sixth third", ordinals=True),
                         3)
        self.assertEqual(extract_number("thirty second"), 30)
        self.assertEqual(extract_number("thirty second", ordinals=True), 32)
        self.assertEqual(extract_number("this is the billionth test",
                                        ordinals=True), 1e09)
        self.assertEqual(extract_number("this is the billionth test"), 1e-9)
        self.assertEqual(extract_number("this is the billionth test",
                                        ordinals=True,
                                        short_scale=False), 1e12)
        self.assertEqual(extract_number("this is the billionth test",
                                        short_scale=False), 1e-12)

        # Verify non-power multiples of ten no longer discard
        # adjacent multipliers
        self.assertEqual(extract_number("twenty thousand"), 20000)
        self.assertEqual(extract_number("fifty million"), 50000000)

        # Verify smaller powers of ten no longer cause miscalculation of larger
        # powers of ten (see MycroftAI#86)
        self.assertEqual(extract_number("twenty billion three hundred million \
                                        nine hundred fifty thousand six hundred \
                                        seventy five point eight"),
                         20300950675.8)
        self.assertEqual(extract_number("nine hundred ninety nine million nine \
                                        hundred ninety nine thousand nine \
                                        hundred ninety nine point nine"),
                         999999999.9)

        # TODO why does "trillion" result in xxxx.0?
        self.assertEqual(extract_number("eight hundred trillion two hundred \
                                        fifty seven"), 800000000000257.0)

        # TODO handle this case
        # self.assertEqual(
        #    extract_number("6 dot six six six"),
        #    6.666)
        self.assertTrue(extract_number("The tennis player is fast") is False)
        self.assertTrue(extract_number("fraggle") is False)

        self.assertTrue(extract_number("fraggle zero") is not False)
        self.assertEqual(extract_number("fraggle zero"), 0)

        self.assertTrue(extract_number("grobo 0") is not False)
        self.assertEqual(extract_number("grobo 0"), 0)

        self.assertEqual(extract_number("a couple of beers"), 2)
        self.assertEqual(extract_number("a couple hundred beers"), 200)
        self.assertEqual(extract_number("a couple thousand beers"), 2000)

        self.assertEqual(extract_number(
            "this is the 7th test", ordinals=True), 7)
        self.assertEqual(extract_number(
            "this is the 7th test", ordinals=False), 7)
        self.assertTrue(extract_number("this is the nth test") is False)
        self.assertEqual(extract_number("this is the 1st test"), 1)
        self.assertEqual(extract_number("this is the 2nd test"), 2)
        self.assertEqual(extract_number("this is the 3rd test"), 3)
        self.assertEqual(extract_number("this is the 31st test"), 31)
        self.assertEqual(extract_number("this is the 32nd test"), 32)
        self.assertEqual(extract_number("this is the 33rd test"), 33)
        self.assertEqual(extract_number("this is the 34th test"), 34)

        self.assertEqual(extract_number(
            "you are the second one", ordinals=False), 1)
        self.assertEqual(extract_number(
            "you are the second one", ordinals=True), 2)
        self.assertEqual(extract_number("you are the 1st one"), 1)
        self.assertEqual(extract_number("you are the 2nd one"), 2)
        self.assertEqual(extract_number("you are the 3rd one"), 3)
        self.assertEqual(extract_number("you are the 8th one"), 8)
        self.assertEqual(extract_number("totally 100%"), 100)

    def test_extract_duration_en(self):
        self.assertEqual(extract_duration("10 seconds"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minutes"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 hours"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 days"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 weeks"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("seven hours"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 seconds"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("eight and a half days thirty"
                                          " nine seconds"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("Set a timer for 30 minutes"),
                         (timedelta(minutes=30), "set a timer for"))
        self.assertEqual(extract_duration("Four and a half minutes until"
                                          " sunset"),
                         (timedelta(minutes=4.5), "until sunset"))
        self.assertEqual(extract_duration("Nineteen minutes past the hour"),
                         (timedelta(minutes=19), "past the hour"))
        self.assertEqual(extract_duration("wake me up in three weeks, four"
                                          " hundred ninety seven days, and"
                                          " three hundred 91.6 seconds"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "wake me up in , , and"))
        self.assertEqual(extract_duration("The movie is one hour, fifty seven"
                                          " and a half minutes long"),
                         (timedelta(hours=1, minutes=57.5),
                          "the movie is ,  long"))
        self.assertEqual(extract_duration("10-seconds"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minutes"),
                         (timedelta(minutes=5), ""))

        self.assertEqual(extract_duration("1 month"),
                         (timedelta(days=DAYS_IN_1_MONTH), ""))
        self.assertEqual(
            extract_duration("1 month",
                             resolution=DurationResolution.TIMEDELTA),
            (timedelta(days=DAYS_IN_1_MONTH), ""))

        self.assertEqual(extract_duration("3 months"),
                         (timedelta(days=DAYS_IN_1_MONTH * 3), ""))
        self.assertEqual(extract_duration("a year"),
                         (timedelta(days=DAYS_IN_1_YEAR), ""))
        self.assertEqual(extract_duration("1 year"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1), ""))
        self.assertEqual(extract_duration("5 years"),
                         (timedelta(days=DAYS_IN_1_YEAR * 5), ""))
        self.assertEqual(extract_duration("a decade"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("1 decade"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("5 decades"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10 * 5), ""))
        self.assertEqual(extract_duration("1 century"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("a century"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("5 centuries"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100 * 5), ""))
        self.assertEqual(extract_duration("1 millennium"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000), ""))
        self.assertEqual(extract_duration("5 millenniums"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000 * 5), ""))

    def test_extract_duration_delta_en(self):
        self.assertEqual(
            extract_duration("10 seconds",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(seconds=10.0), ""))
        self.assertEqual(

            extract_duration("5 minutes",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(minutes=5), ""))
        self.assertEqual(
            extract_duration("2 hours",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(hours=2), ""))
        self.assertEqual(
            extract_duration("3 days",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(days=3), ""))
        self.assertEqual(
            extract_duration("25 weeks",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(weeks=25), ""))
        self.assertEqual(
            extract_duration("seven hours",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(hours=7), ""))
        self.assertEqual(
            extract_duration("7.5 seconds",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(seconds=7.5), ""))
        self.assertEqual(
            extract_duration("eight and a half days thirty nine seconds",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(days=8.5, seconds=39), ""))
        self.assertEqual(
            extract_duration("Set a timer for 30 minutes",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(minutes=30), "set a timer for"))
        self.assertEqual(
            extract_duration("Four and a half minutes until sunset",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(minutes=4.5), "until sunset"))
        self.assertEqual(
            extract_duration("Nineteen minutes past the hour",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(minutes=19), "past the hour"))
        self.assertEqual(
            extract_duration("wake me up in three weeks, four hundred "
                             "ninety seven days, and three hundred 91.6 "
                             "seconds",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(weeks=3, days=497, seconds=391.6),
             "wake me up in , , and"))
        self.assertEqual(
            extract_duration("The movie is one hour, fifty seven"
                             " and a half minutes long",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(hours=1, minutes=57.5),
             "the movie is ,  long"))
        self.assertEqual(
            extract_duration("10-seconds",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(seconds=10.0), ""))
        self.assertEqual(
            extract_duration("5-minutes",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(minutes=5), ""))

        self.assertEqual(
            extract_duration("1 month",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(months=1), ""))
        self.assertEqual(
            extract_duration("3 months",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(months=3), ""))
        self.assertEqual(
            extract_duration("a year",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=1), ""))
        self.assertEqual(
            extract_duration("1 year",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=1), ""))
        self.assertEqual(
            extract_duration("5 years",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=5), ""))
        self.assertEqual(
            extract_duration("a decade",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=10), ""))
        self.assertEqual(
            extract_duration("1 decade",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=10), ""))
        self.assertEqual(
            extract_duration("5 decades",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=10 * 5), ""))
        self.assertEqual(
            extract_duration("1 century",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=100), ""))
        self.assertEqual(
            extract_duration("a century",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=100), ""))
        self.assertEqual(
            extract_duration("5 centuries",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=500), ""))
        self.assertEqual(
            extract_duration("1 millennium",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=1000), ""))
        self.assertEqual(
            extract_duration("5 millenniums",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=1000 * 5), ""))

    def test_extract_duration_seconds_en(self):
        def test_seconds(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_SECONDS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_seconds("10 seconds", 10, "")
        test_seconds("5 minutes", 5 * 60, "")
        test_seconds("2 hours", 2 * 60 * 60, "")
        test_seconds("3 days", 3 * 24 * 60 * 60, "")
        test_seconds("25 weeks", 25 * 7 * 24 * 60 * 60, "")
        test_seconds("seven hours", 7 * 60 * 60, "")
        test_seconds("7.5 seconds", 7.5, "")
        test_seconds("eight and a half days thirty nine seconds",
                     8.5 * 24 * 60 * 60 + 39, "")
        test_seconds("Set a timer for 30 minutes", 30 * 60, "set a timer for")
        test_seconds("Four and a half minutes until sunset", 4.5 * 60,
                     "until sunset")
        test_seconds("Nineteen minutes past the hour", 19 * 60,
                     "past the hour")
        test_seconds("wake me up in three weeks, four hundred ninety seven "
                     "days, and three hundred 91.6 seconds",
                     3 * 7 * 24 * 60 * 60 + 497 * 24 * 60 * 60 + 391.6,
                     "wake me up in , , and")
        test_seconds("The movie is one hour, fifty seven and a half "
                     "minutes long", 60 * 60 + 57.5 * 60,
                     "the movie is ,  long")
        test_seconds("10-seconds", 10, "")
        test_seconds("5-minutes", 5 * 60, "")
        test_seconds("1 month", DAYS_IN_1_MONTH * 24 * 60 * 60, "")
        test_seconds("3 months", 3 * DAYS_IN_1_MONTH * 24 * 60 * 60, "")
        test_seconds("a year", DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 year", DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 years", 5 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("a decade", 10 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 decade", 10 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 decades", 5 * 10 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 century", 100 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("a century", 100 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 centuries", 500 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 millennium", 1000 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 millenniums", 5000 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")

    def test_extract_duration_minutes_en(self):
        def test_minutes(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_MINUTES)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_minutes("10 seconds", 10 / 60, "")
        test_minutes("5 minutes", 5, "")
        test_minutes("2 hours", 2 * 60, "")
        test_minutes("3 days", 3 * 24 * 60, "")
        test_minutes("25 weeks", 25 * 7 * 24 * 60, "")
        test_minutes("seven hours", 7 * 60, "")
        test_minutes("7.5 seconds", 7.5 / 60, "")
        test_minutes("eight and a half days thirty nine seconds",
                     8.5 * 24 * 60 + 39 / 60, "")
        test_minutes("Set a timer for 30 minutes", 30, "set a timer for")
        test_minutes("Four and a half minutes until sunset", 4.5,
                     "until sunset")
        test_minutes("Nineteen minutes past the hour", 19,
                     "past the hour")
        test_minutes("wake me up in three weeks, four hundred ninety seven "
                     "days, and three hundred 91.6 seconds",
                     3 * 7 * 24 * 60 + 497 * 24 * 60 + 391.6 / 60,
                     "wake me up in , , and")
        test_minutes("The movie is one hour, fifty seven and a half "
                     "minutes long", 60 + 57.5,
                     "the movie is ,  long")
        test_minutes("10-seconds", 10 / 60, "")
        test_minutes("5-minutes", 5, "")
        test_minutes("1 month", DAYS_IN_1_MONTH * 24 * 60, "")
        test_minutes("3 months", 3 * DAYS_IN_1_MONTH * 24 * 60, "")
        test_minutes("a year", DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 year", DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 years", 5 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("a decade", 10 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 decade", 10 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 decades", 5 * 10 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 century", 100 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("a century", 100 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 centuries", 500 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 millennium", 1000 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 millenniums", 5000 * DAYS_IN_1_YEAR * 24 * 60, "")

    def test_extract_duration_hours_en(self):
        def test_hours(duration_str, expected_duration,
                       expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_HOURS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_hours("10 seconds", 10 / 60 / 60, "")
        test_hours("5 minutes", 5 / 60, "")
        test_hours("2 hours", 2, "")
        test_hours("3 days", 3 * 24, "")
        test_hours("25 weeks", 25 * 7 * 24, "")
        test_hours("seven hours", 7, "")
        test_hours("7.5 seconds", 7.5 / 60 / 60, "")
        test_hours("eight and a half days thirty nine seconds",
                   8.5 * 24 + 39 / 60 / 60, "")
        test_hours("Set a timer for 30 minutes", 30 / 60, "set a timer for")
        test_hours("Four and a half minutes until sunset", 4.5 / 60,
                   "until sunset")
        test_hours("Nineteen minutes past the hour", 19 / 60,
                   "past the hour")
        test_hours("wake me up in three weeks, four hundred ninety seven "
                   "days, and three hundred 91.6 seconds",
                   3 * 7 * 24 + 497 * 24 + 391.6 / 60 / 60,
                   "wake me up in , , and")
        test_hours("The movie is one hour, fifty seven and a half "
                   "minutes long", 1 + 57.5 / 60,
                   "the movie is ,  long")
        test_hours("10-seconds", 10 / 60 / 60, "")
        test_hours("5-minutes", 5 / 60, "")
        test_hours("1 month", DAYS_IN_1_MONTH * 24, "")
        test_hours("3 months", 3 * DAYS_IN_1_MONTH * 24, "")
        test_hours("a year", DAYS_IN_1_YEAR * 24, "")
        test_hours("1 year", DAYS_IN_1_YEAR * 24, "")
        test_hours("5 years", 5 * DAYS_IN_1_YEAR * 24, "")
        test_hours("a decade", 10 * DAYS_IN_1_YEAR * 24, "")
        test_hours("1 decade", 10 * DAYS_IN_1_YEAR * 24, "")
        test_hours("5 decades", 5 * 10 * DAYS_IN_1_YEAR * 24, "")
        test_hours("1 century", 100 * DAYS_IN_1_YEAR * 24, "")
        test_hours("a century", 100 * DAYS_IN_1_YEAR * 24, "")
        test_hours("5 centuries", 500 * DAYS_IN_1_YEAR * 24, "")
        test_hours("1 millennium", 1000 * DAYS_IN_1_YEAR * 24, "")
        test_hours("5 millenniums", 5000 * DAYS_IN_1_YEAR * 24, "")

    def test_extract_duration_days_en(self):
        def test_days(duration_str, expected_duration,
                      expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_DAYS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_days("10 seconds", 10 / 60 / 60 / 24, "")
        test_days("5 minutes", 5 / 60 / 24, "")
        test_days("2 hours", 2 / 24, "")
        test_days("3 days", 3, "")
        test_days("25 weeks", 25 * 7, "")
        test_days("seven hours", 7 / 24, "")
        test_days("7.5 seconds", 7.5 / 60 / 60 / 24, "")
        test_days("eight and a half days thirty nine seconds",
                  8.5 + 39 / 60 / 60 / 24, "")
        test_days("Set a timer for 30 minutes", 30 / 60 / 24,
                  "set a timer for")
        test_days("Four and a half minutes until sunset", 4.5 / 60 / 24,
                  "until sunset")
        test_days("Nineteen minutes past the hour", 19 / 60 / 24,
                  "past the hour")
        test_days("wake me up in three weeks, four hundred ninety seven "
                  "days, and three hundred 91.6 seconds",
                  3 * 7 + 497 + 391.6 / 60 / 60 / 24,
                  "wake me up in , , and")
        test_days("The movie is one hour, fifty seven and a half "
                  "minutes long", 1 / 24 + 57.5 / 60 / 24,
                  "the movie is ,  long")
        test_days("10-seconds", 10 / 60 / 60 / 24, "")
        test_days("5-minutes", 5 / 60 / 24, "")
        test_days("1 month", DAYS_IN_1_MONTH, "")
        test_days("3 months", 3 * DAYS_IN_1_MONTH, "")
        test_days("a year", DAYS_IN_1_YEAR, "")
        test_days("1 year", DAYS_IN_1_YEAR, "")
        test_days("5 years", 5 * DAYS_IN_1_YEAR, "")
        test_days("a decade", 10 * DAYS_IN_1_YEAR, "")
        test_days("1 decade", 10 * DAYS_IN_1_YEAR, "")
        test_days("5 decades", 5 * 10 * DAYS_IN_1_YEAR, "")
        test_days("1 century", 100 * DAYS_IN_1_YEAR, "")
        test_days("a century", 100 * DAYS_IN_1_YEAR, "")
        test_days("5 centuries", 500 * DAYS_IN_1_YEAR, "")
        test_days("1 millennium", 1000 * DAYS_IN_1_YEAR, "")
        test_days("5 millenniums", 5000 * DAYS_IN_1_YEAR, "")

    def test_extractdatetime_en(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 13, 4)  # Tue June 27, 2017 @ 1:04pm
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("now is the time",
                    "2017-06-27 13:04:00", "is time")
        testExtract("in a second",
                    "2017-06-27 13:04:01", "")
        testExtract("in a minute",
                    "2017-06-27 13:05:00", "")
        testExtract("in a couple minutes",
                    "2017-06-27 13:06:00", "")
        testExtract("in a couple of minutes",
                    "2017-06-27 13:06:00", "")
        testExtract("in a couple hours",
                    "2017-06-27 15:04:00", "")
        testExtract("in a couple of hours",
                    "2017-06-27 15:04:00", "")
        testExtract("in a couple weeks",
                    "2017-07-11 00:00:00", "")
        testExtract("in a couple of weeks",
                    "2017-07-11 00:00:00", "")
        testExtract("in a couple months",
                    "2017-08-27 00:00:00", "")
        testExtract("in a couple years",
                    "2019-06-27 00:00:00", "")
        testExtract("in a couple of months",
                    "2017-08-27 00:00:00", "")
        testExtract("in a couple of years",
                    "2019-06-27 00:00:00", "")
        testExtract("in a decade",
                    "2027-06-27 00:00:00", "")
        testExtract("in a couple of decades",
                    "2037-06-27 00:00:00", "")
        testExtract("next decade",
                    "2027-06-27 00:00:00", "")
        testExtract("in a century",
                    "2117-06-27 00:00:00", "")
        testExtract("in a millennium",
                    "3017-06-27 00:00:00", "")
        testExtract("in a couple decades",
                    "2037-06-27 00:00:00", "")
        testExtract("in 5 decades",
                    "2067-06-27 00:00:00", "")
        testExtract("in a couple centuries",
                    "2217-06-27 00:00:00", "")
        testExtract("in a couple of centuries",
                    "2217-06-27 00:00:00", "")
        testExtract("in 2 centuries",
                    "2217-06-27 00:00:00", "")
        testExtract("in a couple millenniums",
                    "4017-06-27 00:00:00", "")
        testExtract("in a couple of millenniums",
                    "4017-06-27 00:00:00", "")
        testExtract("in an hour",
                    "2017-06-27 14:04:00", "")
        testExtract("i want it within the hour",
                    "2017-06-27 14:04:00", "i want it")
        testExtract("in 1 second",
                    "2017-06-27 13:04:01", "")
        testExtract("in 2 seconds",
                    "2017-06-27 13:04:02", "")
        testExtract("Set the ambush in 1 minute",
                    "2017-06-27 13:05:00", "set ambush")
        testExtract("Set the ambush for half an hour",
                    "2017-06-27 13:34:00", "set ambush")
        testExtract("Set the ambush for 5 days from today",
                    "2017-07-02 00:00:00", "set ambush")
        testExtract("day after tomorrow",
                    "2017-06-29 00:00:00", "")
        testExtract("What is the day after tomorrow's weather?",
                    "2017-06-29 00:00:00", "what is weather")
        testExtract("Remind me at 10:45 pm",
                    "2017-06-27 22:45:00", "remind me")
        testExtract("what is the weather on friday morning",
                    "2017-06-30 08:00:00", "what is weather")
        testExtract("what is tomorrow's weather",
                    "2017-06-28 00:00:00", "what is weather")
        testExtract("what is this afternoon's weather",
                    "2017-06-27 15:00:00", "what is weather")
        testExtract("what is this evening's weather",
                    "2017-06-27 19:00:00", "what is weather")
        testExtract("what was this morning's weather",
                    "2017-06-27 08:00:00", "what was weather")
        testExtract("remind me to call mom in 8 weeks and 2 days",
                    "2017-08-24 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom on august 3rd",
                    "2017-08-03 00:00:00", "remind me to call mom")
        testExtract("remind me tomorrow to call mom at 7am",
                    "2017-06-28 07:00:00", "remind me to call mom")
        testExtract("remind me tomorrow to call mom at 10pm",
                    "2017-06-28 22:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7am",
                    "2017-06-28 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom in an hour",
                    "2017-06-27 14:04:00", "remind me to call mom")
        testExtract("remind me to call mom at 1730",
                    "2017-06-27 17:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 0630",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 06 30 hours",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 06 30",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 06 30 hours",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 7 o'clock",
                    "2017-06-27 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom this evening at 7 o'clock",
                    "2017-06-27 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom  at 7 o'clock tonight",
                    "2017-06-27 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7 o'clock in the morning",
                    "2017-06-28 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom Thursday evening at 7 o'clock",
                    "2017-06-29 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom Thursday morning at 7 o'clock",
                    "2017-06-29 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7 o'clock Thursday morning",
                    "2017-06-29 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7:00 Thursday morning",
                    "2017-06-29 07:00:00", "remind me to call mom")
        # TODO: This test is imperfect due to the "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("remind me to call mom at 7:00 Thursday evening",
                    "2017-06-29 19:00:00", "remind me to call mom at 7:00")
        testExtract("remind me to call mom at 8 Wednesday evening",
                    "2017-06-28 20:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 8 Wednesday in the evening",
                    "2017-06-28 20:00:00", "remind me to call mom")
        testExtract("remind me to call mom Wednesday evening at 8",
                    "2017-06-28 20:00:00", "remind me to call mom")
        testExtract("remind me to call mom in two hours",
                    "2017-06-27 15:04:00", "remind me to call mom")
        testExtract("remind me to call mom in 2 hours",
                    "2017-06-27 15:04:00", "remind me to call mom")
        testExtract("remind me to call mom in 15 minutes",
                    "2017-06-27 13:19:00", "remind me to call mom")
        testExtract("remind me to call mom in fifteen minutes",
                    "2017-06-27 13:19:00", "remind me to call mom")
        testExtract("remind me to call mom in half an hour",
                    "2017-06-27 13:34:00", "remind me to call mom")
        testExtract("remind me to call mom in a half hour",
                    "2017-06-27 13:34:00", "remind me to call mom")
        testExtract("remind me to call mom in a quarter hour",
                    "2017-06-27 13:19:00", "remind me to call mom")
        testExtract("remind me to call mom in a quarter of an hour",
                    "2017-06-27 13:19:00", "remind me to call mom")
        testExtract("remind me to call mom at 10am 2 days after this saturday",
                    "2017-07-03 10:00:00", "remind me to call mom")
        testExtract("Play Rick Astley music 2 days from Friday",
                    "2017-07-02 00:00:00", "play rick astley music")
        testExtract("Begin the invasion at 3:45 pm on Thursday",
                    "2017-06-29 15:45:00", "begin invasion")
        testExtract("On Monday, order pie from the bakery",
                    "2017-07-03 00:00:00", "order pie from bakery")
        testExtract("Play Happy Birthday music 5 years from today",
                    "2022-06-27 00:00:00", "play happy birthday music")
        testExtract("Skype Mom at 12:45 pm next Thursday",
                    "2017-07-06 12:45:00", "skype mom")
        testExtract("What's the weather next Friday?",
                    "2017-06-30 00:00:00", "what weather")
        testExtract("What's the weather next Wednesday?",
                    "2017-07-05 00:00:00", "what weather")
        testExtract("What's the weather next Thursday?",
                    "2017-07-06 00:00:00", "what weather")
        testExtract("what is the weather next friday morning",
                    "2017-06-30 08:00:00", "what is weather")
        testExtract("what is the weather next friday evening",
                    "2017-06-30 19:00:00", "what is weather")
        testExtract("what is the weather next friday afternoon",
                    "2017-06-30 15:00:00", "what is weather")
        testExtract("remind me to call mom on august 3rd",
                    "2017-08-03 00:00:00", "remind me to call mom")
        testExtract("Buy fireworks on the 4th of July",
                    "2017-07-04 00:00:00", "buy fireworks")
        testExtract("what is the weather 2 weeks from next friday",
                    "2017-07-14 00:00:00", "what is weather")
        testExtract("what is the weather wednesday at 0700 hours",
                    "2017-06-28 07:00:00", "what is weather")
        testExtract("set an alarm wednesday at 7 o'clock",
                    "2017-06-28 07:00:00", "set alarm")
        testExtract("Set up an appointment at 12:45 pm next Thursday",
                    "2017-07-06 12:45:00", "set up appointment")
        testExtract("What's the weather this Thursday?",
                    "2017-06-29 00:00:00", "what weather")
        testExtract("set up the visit for 2 weeks and 6 days from Saturday",
                    "2017-07-21 00:00:00", "set up visit")
        testExtract("Begin the invasion at 03 45 on Thursday",
                    "2017-06-29 03:45:00", "begin invasion")
        testExtract("Begin the invasion at o 800 hours on Thursday",
                    "2017-06-29 08:00:00", "begin invasion")
        testExtract("Begin the party at 8 o'clock in the evening on Thursday",
                    "2017-06-29 20:00:00", "begin party")
        testExtract("Begin the invasion at 8 in the evening on Thursday",
                    "2017-06-29 20:00:00", "begin invasion")
        testExtract("Begin the invasion on Thursday at noon",
                    "2017-06-29 12:00:00", "begin invasion")
        testExtract("Begin the invasion on Thursday at midnight",
                    "2017-06-29 00:00:00", "begin invasion")
        testExtract("Begin the invasion on Thursday at 0500",
                    "2017-06-29 05:00:00", "begin invasion")
        testExtract("remind me to wake up in 4 years",
                    "2021-06-27 00:00:00", "remind me to wake up")
        testExtract("remind me to wake up in 4 years and 4 days",
                    "2021-07-01 00:00:00", "remind me to wake up")
        testExtract("What is the weather 3 days after tomorrow?",
                    "2017-07-01 00:00:00", "what is weather")
        testExtract("december 3",
                    "2017-12-03 00:00:00", "")
        testExtract("lets meet at 8:00 tonight",
                    "2017-06-27 20:00:00", "lets meet")
        testExtract("lets meet at 5pm",
                    "2017-06-27 17:00:00", "lets meet")
        testExtract("lets meet at 8 a.m.",
                    "2017-06-28 08:00:00", "lets meet")
        testExtract("remind me to wake up at 8 a.m",
                    "2017-06-28 08:00:00", "remind me to wake up")
        testExtract("what is the weather on tuesday",
                    "2017-06-27 00:00:00", "what is weather")
        testExtract("what is the weather on monday",
                    "2017-07-03 00:00:00", "what is weather")
        testExtract("what is the weather this wednesday",
                    "2017-06-28 00:00:00", "what is weather")
        testExtract("on thursday what is the weather",
                    "2017-06-29 00:00:00", "what is weather")
        testExtract("on this thursday what is the weather",
                    "2017-06-29 00:00:00", "what is weather")
        testExtract("on last monday what was the weather",
                    "2017-06-26 00:00:00", "what was weather")
        testExtract("set an alarm for wednesday evening at 8",
                    "2017-06-28 20:00:00", "set alarm")
        testExtract("set an alarm for wednesday at 3 o'clock in the afternoon",
                    "2017-06-28 15:00:00", "set alarm")
        testExtract("set an alarm for wednesday at 3 o'clock in the morning",
                    "2017-06-28 03:00:00", "set alarm")
        testExtract("set an alarm for wednesday morning at 7 o'clock",
                    "2017-06-28 07:00:00", "set alarm")
        testExtract("set an alarm for today at 7 o'clock",
                    "2017-06-27 19:00:00", "set alarm")
        testExtract("set an alarm for this evening at 7 o'clock",
                    "2017-06-27 19:00:00", "set alarm")
        # TODO: This test is imperfect due to the "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("set an alarm for this evening at 7:00",
                    "2017-06-27 19:00:00", "set alarm at 7:00")
        testExtract("on the evening of june 5th 2017 remind me to" +
                    " call my mother",
                    "2017-06-05 19:00:00", "remind me to call my mother")
        # TODO: This test is imperfect due to the missing "for" in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("update my calendar for a morning meeting with julius" +
                    " on march 4th",
                    "2018-03-04 08:00:00",
                    "update my calendar meeting with julius")
        testExtract("remind me to call mom next tuesday",
                    "2017-07-04 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 3 weeks",
                    "2017-07-18 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 8 weeks",
                    "2017-08-22 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 8 weeks and 2 days",
                    "2017-08-24 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 4 days",
                    "2017-07-01 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 3 months",
                    "2017-09-27 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 2 years and 2 days",
                    "2019-06-29 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom next week",
                    "2017-07-04 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 10am on saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 10am this saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 10 next saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 10am next saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        # test yesterday
        testExtract("what day was yesterday",
                    "2017-06-26 00:00:00", "what day was")
        testExtract("what day was the day before yesterday",
                    "2017-06-25 00:00:00", "what day was")
        testExtract("i had dinner yesterday at 6",
                    "2017-06-26 06:00:00", "i had dinner")
        testExtract("i had dinner yesterday at 6 am",
                    "2017-06-26 06:00:00", "i had dinner")
        testExtract("i had dinner yesterday at 6 pm",
                    "2017-06-26 18:00:00", "i had dinner")

        # Below two tests, ensure that time is picked
        # even if no am/pm is specified
        # in case of weekdays/tonight
        testExtract("set alarm for 9 on weekdays",
                    "2017-06-27 21:00:00", "set alarm weekdays")
        testExtract("for 8 tonight",
                    "2017-06-27 20:00:00", "")
        testExtract("for 8:30pm tonight",
                    "2017-06-27 20:30:00", "")
        # Tests a time with ':' & without am/pm
        testExtract("set an alarm for tonight 9:30",
                    "2017-06-27 21:30:00", "set alarm")
        testExtract("set an alarm at 9:00 for tonight",
                    "2017-06-27 21:00:00", "set alarm")
        # Check if it picks the intent irrespective of correctness
        testExtract("set an alarm at 9 o'clock for tonight",
                    "2017-06-27 21:00:00", "set alarm")
        testExtract("remind me about the game tonight at 11:30",
                    "2017-06-27 23:30:00", "remind me about game")
        testExtract("set alarm at 7:30 on weekdays",
                    "2017-06-27 19:30:00", "set alarm on weekdays")

        #  "# days <from X/after X>"
        testExtract("my birthday is 2 days from today",
                    "2017-06-29 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days after today",
                    "2017-06-29 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days from tomorrow",
                    "2017-06-30 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days after tomorrow",
                    "2017-06-30 00:00:00", "my birthday is")
        testExtract("remind me to call mom at 10am 2 days after next saturday",
                    "2017-07-10 10:00:00", "remind me to call mom")
        testExtract("my birthday is 2 days from yesterday",
                    "2017-06-28 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days after yesterday",
                    "2017-06-28 00:00:00", "my birthday is")

        #  "# days ago>"
        testExtract("my birthday was 1 day ago",
                    "2017-06-26 00:00:00", "my birthday was")
        testExtract("my birthday was 2 days ago",
                    "2017-06-25 00:00:00", "my birthday was")
        testExtract("my birthday was 3 days ago",
                    "2017-06-24 00:00:00", "my birthday was")
        testExtract("my birthday was 4 days ago",
                    "2017-06-23 00:00:00", "my birthday was")
        # TODO this test is imperfect due to "tonight" in the reminder, but let is pass since the date is correct
        testExtract("lets meet tonight",
                    "2017-06-27 22:00:00", "lets meet tonight")
        # TODO this test is imperfect due to "at night" in the reminder, but let is pass since the date is correct
        testExtract("lets meet later at night",
                    "2017-06-27 22:00:00", "lets meet later at night")
        # TODO this test is imperfect due to "night" in the reminder, but let is pass since the date is correct
        testExtract("what's the weather like tomorrow night",
                    "2017-06-28 22:00:00", "what is weather like night")
        # TODO this test is imperfect due to "night" in the reminder, but let is pass since the date is correct
        testExtract("what's the weather like next tuesday night",
                    "2017-07-04 22:00:00", "what is weather like night")

    def test_extract_ambiguous_time_en(self):
        morning = datetime(2017, 6, 27, 8, 1, 2)
        evening = datetime(2017, 6, 27, 20, 1, 2)
        noonish = datetime(2017, 6, 27, 12, 1, 2)
        self.assertEqual(
            extract_datetime('feed the fish'), None)
        self.assertEqual(
            extract_datetime('day'), None)
        self.assertEqual(
            extract_datetime('week'), None)
        self.assertEqual(
            extract_datetime('month'), None)
        self.assertEqual(
            extract_datetime('year'), None)
        self.assertEqual(
            extract_datetime(' '), None)
        self.assertEqual(
            extract_datetime('feed fish at 10 o\'clock', morning)[0],
            datetime(2017, 6, 27, 10, 0, 0))
        self.assertEqual(
            extract_datetime('feed fish at 10 o\'clock', noonish)[0],
            datetime(2017, 6, 27, 22, 0, 0))
        self.assertEqual(
            extract_datetime('feed fish at 10 o\'clock', evening)[0],
            datetime(2017, 6, 27, 22, 0, 0))

    def test_extract_date_with_may_I_en(self):
        now = datetime(2019, 7, 4, 8, 1, 2)
        may_date = datetime(2019, 5, 2, 10, 11, 20)
        self.assertEqual(
            extract_datetime('May I know what time it is tomorrow', now)[0],
            datetime(2019, 7, 5, 0, 0, 0))
        self.assertEqual(
            extract_datetime('May I when 10 o\'clock is', now)[0],
            datetime(2019, 7, 4, 10, 0, 0))
        self.assertEqual(
            extract_datetime('On 24th of may I want a reminder', may_date)[0],
            datetime(2019, 5, 24, 0, 0, 0))

    def test_extract_relativedatetime_en(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2)
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("lets meet in 5 minutes",
                    "2017-06-27 10:06:02", "lets meet")
        testExtract("lets meet in 5minutes",
                    "2017-06-27 10:06:02", "lets meet")
        testExtract("lets meet in 5 seconds",
                    "2017-06-27 10:01:07", "lets meet")
        testExtract("lets meet in 1 hour",
                    "2017-06-27 11:01:02", "lets meet")
        testExtract("lets meet in 2 hours",
                    "2017-06-27 12:01:02", "lets meet")
        testExtract("lets meet in 2hours",
                    "2017-06-27 12:01:02", "lets meet")
        testExtract("lets meet in 1 minute",
                    "2017-06-27 10:02:02", "lets meet")
        testExtract("lets meet in 1 second",
                    "2017-06-27 10:01:03", "lets meet")
        testExtract("lets meet in 5seconds",
                    "2017-06-27 10:01:07", "lets meet")

    def test_spaces(self):
        self.assertEqual(normalize("  this   is  a    test"),
                         "this is test")
        self.assertEqual(normalize("  this   is  a    test  "),
                         "this is test")
        self.assertEqual(normalize("  this   is  one    test"),
                         "this is 1 test")

    def test_numbers(self):
        self.assertEqual(normalize("this is a one two three  test"),
                         "this is 1 2 3 test")
        self.assertEqual(normalize("  it's  a four five six  test"),
                         "it is 4 5 6 test")
        self.assertEqual(normalize("it's  a seven eight nine test"),
                         "it is 7 8 9 test")
        self.assertEqual(normalize("it's a seven eight nine  test"),
                         "it is 7 8 9 test")
        self.assertEqual(normalize("that's a ten eleven twelve test"),
                         "that is 10 11 12 test")
        self.assertEqual(normalize("that's a thirteen fourteen test"),
                         "that is 13 14 test")
        self.assertEqual(normalize("that's fifteen sixteen seventeen"),
                         "that is 15 16 17")
        self.assertEqual(normalize("that's eighteen nineteen twenty"),
                         "that is 18 19 20")
        self.assertEqual(normalize("that's one nineteen twenty two"),
                         "that is 1 19 20 2")
        self.assertEqual(normalize("that's one hundred"),
                         "that is 1 hundred")
        self.assertEqual(normalize("that's one two twenty two"),
                         "that is 1 2 20 2")
        self.assertEqual(normalize("that's one and a half"),
                         "that is 1 and half")
        self.assertEqual(normalize("that's one and a half and five six"),
                         "that is 1 and half and 5 6")

    def test_multiple_numbers(self):
        self.assertEqual(extract_numbers("this is a one two three  test"),
                         [1.0, 2.0, 3.0])
        self.assertEqual(extract_numbers("it's  a four five six  test"),
                         [4.0, 5.0, 6.0])
        self.assertEqual(extract_numbers("this is a ten eleven twelve  test"),
                         [10.0, 11.0, 12.0])
        self.assertEqual(extract_numbers("this is a one twenty one  test"),
                         [1.0, 21.0])
        self.assertEqual(extract_numbers("1 dog, seven pigs, macdonald had a "
                                         "farm, 3 times 5 macarena"),
                         [1, 7, 3, 5])
        self.assertEqual(extract_numbers("two beers for two bears"),
                         [2.0, 2.0])
        self.assertEqual(extract_numbers("twenty 20 twenty"),
                         [20, 20, 20])
        self.assertEqual(extract_numbers("twenty 20 22"),
                         [20.0, 20.0, 22.0])
        self.assertEqual(extract_numbers("twenty twenty two twenty"),
                         [20, 22, 20])
        self.assertEqual(extract_numbers("twenty 2"),
                         [22.0])
        self.assertEqual(extract_numbers("twenty 20 twenty 2"),
                         [20, 20, 22])
        self.assertEqual(extract_numbers("third one"),
                         [1 / 3, 1])
        self.assertEqual(extract_numbers("third one", ordinals=True), [3])
        self.assertEqual(extract_numbers("six trillion", short_scale=True),
                         [6e12])
        self.assertEqual(extract_numbers("six trillion", short_scale=False),
                         [6e18])
        self.assertEqual(extract_numbers("two pigs and six trillion bacteria",
                                         short_scale=True), [2, 6e12])
        self.assertEqual(extract_numbers("two pigs and six trillion bacteria",
                                         short_scale=False), [2, 6e18])
        self.assertEqual(extract_numbers("thirty second or first",
                                         ordinals=True), [32, 1])
        self.assertEqual(extract_numbers("this is a seven eight nine and a"
                                         " half test"),
                         [7.0, 8.0, 9.5])

    def test_contractions(self):
        self.assertEqual(normalize("ain't"), "is not")
        self.assertEqual(normalize("aren't"), "are not")
        self.assertEqual(normalize("can't"), "can not")
        self.assertEqual(normalize("could've"), "could have")
        self.assertEqual(normalize("couldn't"), "could not")
        self.assertEqual(normalize("didn't"), "did not")
        self.assertEqual(normalize("doesn't"), "does not")
        self.assertEqual(normalize("don't"), "do not")
        self.assertEqual(normalize("gonna"), "going to")
        self.assertEqual(normalize("gotta"), "got to")
        self.assertEqual(normalize("hadn't"), "had not")
        self.assertEqual(normalize("hadn't have"), "had not have")
        self.assertEqual(normalize("hasn't"), "has not")
        self.assertEqual(normalize("haven't"), "have not")
        # TODO: Ambiguous with "he had"
        self.assertEqual(normalize("he'd"), "he would")
        self.assertEqual(normalize("he'll"), "he will")
        # TODO: Ambiguous with "he has"
        self.assertEqual(normalize("he's"), "he is")
        # TODO: Ambiguous with "how would"
        self.assertEqual(normalize("how'd"), "how did")
        self.assertEqual(normalize("how'll"), "how will")
        # TODO: Ambiguous with "how has" and "how does"
        self.assertEqual(normalize("how's"), "how is")
        # TODO: Ambiguous with "I had"
        self.assertEqual(normalize("I'd"), "I would")
        self.assertEqual(normalize("I'll"), "I will")
        self.assertEqual(normalize("I'm"), "I am")
        self.assertEqual(normalize("I've"), "I have")
        self.assertEqual(normalize("I haven't"), "I have not")
        self.assertEqual(normalize("isn't"), "is not")
        self.assertEqual(normalize("it'd"), "it would")
        self.assertEqual(normalize("it'll"), "it will")
        # TODO: Ambiguous with "it has"
        self.assertEqual(normalize("it's"), "it is")
        self.assertEqual(normalize("it isn't"), "it is not")
        self.assertEqual(normalize("mightn't"), "might not")
        self.assertEqual(normalize("might've"), "might have")
        self.assertEqual(normalize("mustn't"), "must not")
        self.assertEqual(normalize("mustn't have"), "must not have")
        self.assertEqual(normalize("must've"), "must have")
        self.assertEqual(normalize("needn't"), "need not")
        self.assertEqual(normalize("oughtn't"), "ought not")
        self.assertEqual(normalize("shan't"), "shall not")
        # TODO: Ambiguous wiht "she had"
        self.assertEqual(normalize("she'd"), "she would")
        self.assertEqual(normalize("she hadn't"), "she had not")
        self.assertEqual(normalize("she'll"), "she will")
        self.assertEqual(normalize("she's"), "she is")
        self.assertEqual(normalize("she isn't"), "she is not")
        self.assertEqual(normalize("should've"), "should have")
        self.assertEqual(normalize("shouldn't"), "should not")
        self.assertEqual(normalize("shouldn't have"), "should not have")
        self.assertEqual(normalize("somebody's"), "somebody is")
        # TODO: Ambiguous with "someone had"
        self.assertEqual(normalize("someone'd"), "someone would")
        self.assertEqual(normalize("someone hadn't"), "someone had not")
        self.assertEqual(normalize("someone'll"), "someone will")
        # TODO: Ambiguous with "someone has"
        self.assertEqual(normalize("someone's"), "someone is")
        self.assertEqual(normalize("that'll"), "that will")
        # TODO: Ambiguous with "that has"
        self.assertEqual(normalize("that's"), "that is")
        # TODO: Ambiguous with "that had"
        self.assertEqual(normalize("that'd"), "that would")
        # TODO: Ambiguous with "there had"
        self.assertEqual(normalize("there'd"), "there would")
        self.assertEqual(normalize("there're"), "there are")
        # TODO: Ambiguous with "there has"
        self.assertEqual(normalize("there's"), "there is")
        # TODO: Ambiguous with "they had"
        self.assertEqual(normalize("they'd"), "they would")
        self.assertEqual(normalize("they'll"), "they will")
        self.assertEqual(normalize("they won't have"), "they will not have")
        self.assertEqual(normalize("they're"), "they are")
        self.assertEqual(normalize("they've"), "they have")
        self.assertEqual(normalize("they haven't"), "they have not")
        self.assertEqual(normalize("wasn't"), "was not")
        # TODO: Ambiguous wiht "we had"
        self.assertEqual(normalize("we'd"), "we would")
        self.assertEqual(normalize("we would've"), "we would have")
        self.assertEqual(normalize("we wouldn't"), "we would not")
        self.assertEqual(normalize("we wouldn't have"), "we would not have")
        self.assertEqual(normalize("we'll"), "we will")
        self.assertEqual(normalize("we won't have"), "we will not have")
        self.assertEqual(normalize("we're"), "we are")
        self.assertEqual(normalize("we've"), "we have")
        self.assertEqual(normalize("weren't"), "were not")
        self.assertEqual(normalize("what'd"), "what did")
        self.assertEqual(normalize("what'll"), "what will")
        self.assertEqual(normalize("what're"), "what are")
        # TODO: Ambiguous with "what has" / "what does")
        self.assertEqual(normalize("whats"), "what is")
        self.assertEqual(normalize("what's"), "what is")
        self.assertEqual(normalize("what've"), "what have")
        # TODO: Ambiguous with "when has"
        self.assertEqual(normalize("when's"), "when is")
        self.assertEqual(normalize("where'd"), "where did")
        # TODO: Ambiguous with "where has" / where does"
        self.assertEqual(normalize("where's"), "where is")
        self.assertEqual(normalize("where've"), "where have")
        # TODO: Ambiguous with "who had" "who did")
        self.assertEqual(normalize("who'd"), "who would")
        self.assertEqual(normalize("who'd've"), "who would have")
        self.assertEqual(normalize("who'll"), "who will")
        self.assertEqual(normalize("who're"), "who are")
        # TODO: Ambiguous with "who has" / "who does"
        self.assertEqual(normalize("who's"), "who is")
        self.assertEqual(normalize("who've"), "who have")
        self.assertEqual(normalize("why'd"), "why did")
        self.assertEqual(normalize("why're"), "why are")
        # TODO: Ambiguous with "why has" / "why does"
        self.assertEqual(normalize("why's"), "why is")
        self.assertEqual(normalize("won't"), "will not")
        self.assertEqual(normalize("won't've"), "will not have")
        self.assertEqual(normalize("would've"), "would have")
        self.assertEqual(normalize("wouldn't"), "would not")
        self.assertEqual(normalize("wouldn't've"), "would not have")
        self.assertEqual(normalize("ya'll"), "you all")
        self.assertEqual(normalize("y'all"), "you all")
        self.assertEqual(normalize("y'ain't"), "you are not")
        # TODO: Ambiguous with "you had"
        self.assertEqual(normalize("you'd"), "you would")
        self.assertEqual(normalize("you'd've"), "you would have")
        self.assertEqual(normalize("you'll"), "you will")
        self.assertEqual(normalize("you're"), "you are")
        self.assertEqual(normalize("you aren't"), "you are not")
        self.assertEqual(normalize("you've"), "you have")
        self.assertEqual(normalize("you haven't"), "you have not")

    def test_combinations(self):
        self.assertEqual(normalize("I couldn't have guessed there'd be two"),
                         "I could not have guessed there would be 2")
        self.assertEqual(normalize("I wouldn't have"), "I would not have")
        self.assertEqual(normalize("I hadn't been there"),
                         "I had not been there")
        self.assertEqual(normalize("I would've"), "I would have")
        self.assertEqual(normalize("it hadn't"), "it had not")
        self.assertEqual(normalize("it hadn't have"), "it had not have")
        self.assertEqual(normalize("it would've"), "it would have")
        self.assertEqual(normalize("she wouldn't have"), "she would not have")
        self.assertEqual(normalize("she would've"), "she would have")
        self.assertEqual(normalize("someone wouldn't have"),
                         "someone would not have")
        self.assertEqual(normalize("someone would've"), "someone would have")
        self.assertEqual(normalize("what's the weather like"),
                         "what is weather like")
        self.assertEqual(normalize("that's what I told you"),
                         "that is what I told you")

        self.assertEqual(normalize("whats 8 + 4"), "what is 8 + 4")

    def test_gender(self):
        self.assertEqual(get_gender("person"),
                         None)


if __name__ == "__main__":
    unittest.main()
