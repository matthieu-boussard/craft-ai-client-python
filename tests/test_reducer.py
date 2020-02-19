import json
import os

from nose.tools import assert_raises, assert_equal, assert_true
from craft_ai import reduce_decision_rules, errors

HERE = os.path.abspath(os.path.dirname(__file__))

# Assuming we are the test folder and the folder hierarchy is correctly
# constructed
EXPECTATIONS_DIR = os.path.join(HERE, "data", "interpreter", "reduce_decision_rules")


def reduce_decision_rules_tests_generator():
    expectations_files = os.listdir(EXPECTATIONS_DIR)
    for expectations_file in expectations_files:
        if os.path.splitext(expectations_file)[1] == ".json":
            with open(os.path.join(EXPECTATIONS_DIR, expectations_file)) as f:
                expectations = json.load(f)

            for expectation in expectations:
                assert_true(
                    "title" in expectation,
                    "Invalid expectation from '{}': missing \"title\".".format(
                        expectations_file
                    ),
                )
                assert_true(
                    "rules" in expectation and "expectation" in expectation,
                    'Invalid expectation from \'{}\': missing "rules" or "expectation".'.format(
                        expectations_file
                    ),
                )

                # pylint: disable=W0108
                test_fn = lambda r, e: check_expectation(r, e)
                # pylint: enable=W0108

                test_fn.description = expectation["title"]
                reduce_decision_rules_tests_generator.compat_func_name = (
                    test_fn.description
                )

                yield test_fn, expectation["rules"], expectation["expectation"]


def check_expectation(rules, expectation):

    if "error" in expectation:
        assert_raises(errors.CraftAiError, reduce_decision_rules, rules)
    else:
        assert_equal(reduce_decision_rules(rules), expectation["rules"])
