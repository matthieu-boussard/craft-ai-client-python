import json
import os

from nose.tools import assert_raises, assert_equal
from craft_ai import Client, Interpreter, Time, errors as craft_err

from . import settings

#pylint: disable=E1101
assert_equal.__self__.maxDiff = None
#pylint: enable=E1101

HERE = os.path.abspath(os.path.dirname(__file__))

# Assuming we are the test folder and the folder hierarchy is correctly
# constructed
EXPECS_DIR = os.path.join(HERE, "data", "interpreter", "decide", "expectations")
TREES_DIR = os.path.join(HERE, "data", "interpreter", "decide", "trees")

CLIENT = Client(settings.CRAFT_CFG)

def interpreter_tests_generator():
  versions = os.listdir(TREES_DIR)
  for version in versions:
    tree_files = os.listdir(os.path.join(TREES_DIR, version))
    for tree_file in tree_files:
      if os.path.splitext(tree_file)[1] == ".json":
        # Loading the json tree
        with open(os.path.join(TREES_DIR, version, tree_file)) as f:
          tree = json.load(f)
        # Loading the expectations for this tree
        with open(os.path.join(EXPECS_DIR, version, tree_file)) as f:
          expectations = json.load(f)

        for expectation in expectations:
#pylint: disable=W0108
          test_fn = lambda t, e: check_expectation(t, e)
#pylint: enable=W0108

          test_fn.description = tree_file + " - " + expectation["title"]
          interpreter_tests_generator.compat_func_name = test_fn.description

          yield test_fn, tree, expectation

def check_expectation(tree, expectation):
  exp_context = expectation["context"]
  timestamp = None
  exp_time = expectation.get("time")
  time = Time(exp_time["t"], exp_time["tz"]) if exp_time else {}
  configuration = expectation.get("configuration")
  if configuration:
    tree["configuration"].update(configuration)

  if expectation.get("error"):
    with assert_raises(craft_err.CraftAiDecisionError) as context_manager:
      CLIENT.decide(tree, exp_context, timestamp)

    exception = context_manager.exception
    expected_message = ""
    if isinstance(expectation["error"]["message"], str):
      expected_message = expectation["error"]["message"]
    else:
      expected_message = expectation["error"]["message"].encode("utf8")
    assert_equal(exception.message, expected_message)
    assert_equal(exception.metadata, expectation["error"].get("metadata", None))
  else:
    expected_decision = expectation["output"]
    decision = CLIENT.decide(tree, exp_context, time)
    assert_equal(decision, expected_decision)

def test_rebuild_context():
  configuration = {
    "context": {
      "car": {
        "type": "enum"
      },
      "speed": {
        "type": "continuous"
      },
      "day_of_week": {
        "type": "day_of_week",
        "is_generated": False
      },
      "month_of_year": {
        "type": "month_of_year"
      },
      "timezone": {
        "type": "timezone"
      }
    },
    "output": ["speed"],
    "time_quantum": 500
  }

#pylint: disable=W0212

  # Case 2:
  # - provide none of the properties that should be generated
  state = {"car": "Renault", "day_of_week": 2, "timezone": "+01:00"}
  time = Time(1489998174, "+01:00")
  rebuilt_context = Interpreter._rebuild_context(configuration, state, time)["context"]
  expected_context = {
    "car": "Renault",
    "day_of_week": 2,
    "month_of_year": 3,
    "timezone": "+01:00"
  }

#pylint: enable=W0212

  for output in expected_context:
    assert_equal(rebuilt_context[output], expected_context[output])
