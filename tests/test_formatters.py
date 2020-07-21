import unittest

import json
import os

from dateutil.parser import isoparse

from craft_ai import format_property, format_decision_rules, errors


class TestFormatter(unittest.TestCase):
    def test_format_property_time_of_day(self):
        formatter = format_property("time_of_day")

        self.assertEqual(formatter(11.5), "11:30")
        self.assertEqual(formatter(11.008), "11:00:28")

        self.assertEqual(formatter(isoparse("2016-10-20T08:20:03")), "08:20:03")
        self.assertEqual(formatter(isoparse("2016-08-12T13:37")), "13:37")

    def test_format_property_enum(self):
        formatter = format_property("enum")

        self.assertEqual(formatter("toto"), "toto")

    def test_format_property_continuous(self):
        formatter = format_property("continuous")

        self.assertEqual(formatter(12.4), "12.4")
        self.assertEqual(formatter(12.4234), "12.42")

    def test_format_property_month_of_year(self):
        formatter = format_property("month_of_year")

        self.assertEqual(formatter(1), "Jan")
        self.assertEqual(formatter(6), "Jun")
        self.assertEqual(formatter(12), "Dec")


class TestFormatDecisionRules(unittest.TestCase):
    def test_format_decision_rule_(self):

        HERE = os.path.abspath(os.path.dirname(__file__))

        # Assuming we are the test folder and the folder hierarchy is correctly
        # constructed
        EXPECTATIONS_DIR = os.path.join(
            HERE, "data", "interpreter", "format_decision_rules"
        )

        expectations_files = os.listdir(EXPECTATIONS_DIR)
        for expectations_file in expectations_files:
            if os.path.splitext(expectations_file)[1] == ".json":
                # Loading the expectations for this tree
                with open(os.path.join(EXPECTATIONS_DIR, expectations_file)) as f:
                    expectations = json.load(f)

                for expectation in expectations:
                    self.assertTrue(
                        "title" in expectation,
                        "Invalid expectation from '{}': missing \"title\".".format(
                            expectations_file
                        ),
                    )
                    self.assertTrue(
                        "rules" in expectation and "expectation" in expectation,
                        'Invalid expectation from \'{}\': missing "rules" or "expectation".'.format(
                            expectations_file
                        ),
                    )

                    for expectation in expectations:
                        with self.subTest():
                            self.check_expectation(
                                expectation["rules"], expectation["expectation"]
                            )

    def check_expectation(self, rules, expectation):
        if "error" in expectation:
            self.assertRaises(errors.CraftAiError, format_decision_rules, rules)
        else:
            self.assertEqual(format_decision_rules(rules), expectation["string"])
