import json
import os

from dateutil.parser import isoparse
from nose.tools import assert_equal, assert_true, assert_raises

from craft_ai import format_property, format_decision_rules, errors

def test_format_property_time_of_day():
  formatter = format_property("time_of_day")

  assert_equal(formatter(11.5), "11:30")
  assert_equal(formatter(11.008), "11:00:28")

  assert_equal(formatter(isoparse("2016-10-20T08:20:03")), "08:20:03")
  assert_equal(formatter(isoparse("2016-08-12T13:37")), "13:37")


def test_format_property_enum():
  formatter = format_property("enum")

  assert_equal(formatter("toto"), "toto")

def test_format_property_continuous():
  formatter = format_property("continuous")

  assert_equal(formatter(12.4), "12.4")
  assert_equal(formatter(12.4234), "12.42")

def test_format_property_month_of_year():
  formatter = format_property("month_of_year")

  assert_equal(formatter(1), "Jan")
  assert_equal(formatter(6), "Jun")
  assert_equal(formatter(12), "Dec")

HERE = os.path.abspath(os.path.dirname(__file__))

# Assuming we are the test folder and the folder hierarchy is correctly
# constructed
EXPECTATIONS_DIR = os.path.join(HERE, "data", "interpreter", "format_decision_rules")

def format_decision_rule_tests_generator():
  expectations_files = os.listdir(EXPECTATIONS_DIR)
  for expectations_file in expectations_files:
    if os.path.splitext(expectations_file)[1] == ".json":
      # Loading the expectations for this tree
      with open(os.path.join(EXPECTATIONS_DIR, expectations_file)) as f:
        expectations = json.load(f)

      for expectation in expectations:
        assert_true("title" in expectation,
                    "Invalid expectation from '{}': missing \"title\".".format(expectations_file))
        assert_true("rules" in expectation and "expectation" in expectation,
                    "Invalid expectation from '{}': missing \"rules\" or \"expectation\"."
                    .format(expectations_file))

#pylint: disable=W0108
        test_fn = lambda r, e: check_expectation(r, e)
#pylint: enable=W0108

        test_fn.description = expectation["title"]
        format_decision_rule_tests_generator.compat_func_name = test_fn.description

        yield test_fn, expectation["rules"], expectation["expectation"]

def check_expectation(rules, expectation):
  if "error" in expectation:
    assert_raises(errors.CraftAiError,
                  format_decision_rules,
                  rules)
  else:
    assert_equal(format_decision_rules(rules), expectation["string"])
