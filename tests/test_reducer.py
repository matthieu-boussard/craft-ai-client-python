import unittest

import json
import os

from craft_ai import reduce_decision_rules, errors

HERE = os.path.abspath(os.path.dirname(__file__))

# Assuming we are the test folder and the folder hierarchy is correctly
# constructed
EXPECTATIONS_DIR = os.path.join(HERE, "data", "interpreter", "reduce_decision_rules")

class TestReducer(unittest.TestCase):

    def test_reduce_decision_rules_tests_generator(self):
        expectations_files = os.listdir(EXPECTATIONS_DIR)
        for expectations_file in expectations_files:
            if os.path.splitext(expectations_file)[1] == ".json":
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
                            self.check_expectation(expectation["rules"], expectation["expectation"])
                        
    def check_expectation(self, rules, expectation):

        if "error" in expectation:
            self.assertRaises(errors.CraftAiError, reduce_decision_rules, rules)
        else:
            self.assertEqual(reduce_decision_rules(rules), expectation["rules"])
