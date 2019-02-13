import random
import semver

from nose.tools import assert_equal, assert_is_instance, assert_not_equal, assert_raises, with_setup
import craftai

from . import settings
from .data import valid_data
from .data import invalid_data

CLIENT = craftai.Client(settings.CRAFT_CFG)
AGENT_ID = "test_get_decision_tree_" + settings.RUN_ID

VALID_L_CFG = valid_data.VALID_LARGE_CONFIGURATION
VALID_L_BATCH_DURATION = VALID_L_CFG["learning_period"] * 4
VALID_L_ENUM_VALUES = ["CYAN", "MAGENTA", "YELLOW", "BLACK"]

def random_enum_value():
  return random.choice(VALID_L_ENUM_VALUES)

def random_continuous_value():
  return random.uniform(-12, 12)

VALID_L_OPERATIONS = [
  [
    {
      "timestamp": batch_offset * VALID_L_BATCH_DURATION + operation_offset,
      "context": {
        "e1": random_enum_value(),
        "e2": random_enum_value(),
        "e3": random_enum_value(),
        "e4": random_enum_value(),
        "c1": random_continuous_value(),
        "c2": random_continuous_value(),
        "c3": random_continuous_value(),
        "c4": random_continuous_value(),
        "tz": "CET"
      }
    }
    for operation_offset in range(0, VALID_L_BATCH_DURATION, 1000)
  ]
  for batch_offset in range(0, 60)
]

def setup_agent_w_operations():
  CLIENT.delete_agent(AGENT_ID)
  CLIENT.create_agent(valid_data.VALID_CONFIGURATION, AGENT_ID)
  CLIENT.add_operations(AGENT_ID, valid_data.VALID_OPERATIONS_SET)

def setup_agent_w_operations_l():
  CLIENT.delete_agent(AGENT_ID)
  CLIENT.create_agent(VALID_L_CFG, AGENT_ID)
  for batch in VALID_L_OPERATIONS:
    CLIENT.add_operations(AGENT_ID, batch)

def teardown():
  CLIENT.delete_agent(AGENT_ID)

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_with_correct_input():
  decision_tree = CLIENT.get_decision_tree(
    AGENT_ID,
    valid_data.VALID_TIMESTAMP)

  assert_is_instance(decision_tree, dict)
  assert_not_equal(decision_tree.get("_version"), None)
  assert_not_equal(decision_tree.get("configuration"), None)
  assert_not_equal(decision_tree.get("trees"), None)

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_with_specific_version():
  version = 1
  decision_tree = CLIENT.get_decision_tree(
    AGENT_ID,
    valid_data.VALID_TIMESTAMP,
    version)

  assert_is_instance(decision_tree, dict)
  assert_not_equal(decision_tree.get("_version"), None)
  tree_version = semver.parse(decision_tree.get("_version"))
  assert_equal(tree_version["major"], version)
  assert_not_equal(decision_tree.get("configuration"), None)
  assert_not_equal(decision_tree.get("trees"), None)

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_without_timestamp():
  # test if we get the latest decision tree
  decision_tree = CLIENT.get_decision_tree(AGENT_ID)
  ground_truth_decision_tree = decision_tree = CLIENT.get_decision_tree(AGENT_ID, 1458741262)
  assert_is_instance(decision_tree, dict)
  assert_not_equal(decision_tree.get("_version"), None)
  assert_not_equal(decision_tree.get("configuration"), None)
  assert_not_equal(decision_tree.get("trees"), None)
  assert_equal(decision_tree, ground_truth_decision_tree)

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_with_invalid_id():
  """get_decision_tree should fail when given a non-string/empty string ID

  It should raise an error upon request for retrieval of an agent's
  decision tree with an ID that is not of type string, since agent IDs
  should always be strings.
  """
  for empty_id in invalid_data.UNDEFINED_KEY:
    assert_raises(
      craftai.errors.CraftAiBadRequestError,
      CLIENT.get_decision_tree,
      invalid_data.UNDEFINED_KEY[empty_id],
      valid_data.VALID_TIMESTAMP)

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_with_unknown_id():
  """get_decision_tree should fail when given an unknown agent ID

  It should raise an error upon request for the retrieval of an agent
  that doesn't exist.
  """
  assert_raises(
    craftai.errors.CraftAiNotFoundError,
    CLIENT.get_decision_tree,
    invalid_data.UNKNOWN_ID,
    valid_data.VALID_TIMESTAMP)

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_with_negative_timestamp():
  assert_raises(
    craftai.errors.CraftAiBadRequestError,
    CLIENT.get_decision_tree,
    AGENT_ID,
    invalid_data.INVALID_TIMESTAMPS["negative_ts"])

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_with_float_timestamp():
  assert_raises(
    craftai.errors.CraftAiBadRequestError,
    CLIENT.get_decision_tree,
    AGENT_ID,
    invalid_data.INVALID_TIMESTAMPS["float_ts"])

###
### The following tests are quite long, they are disabled atm.
###

# @with_setup(setup_agent_w_operations_l, teardown)
# def test_get_decision_tree_from_operations():
#   last_operation = VALID_L_OPERATIONS[-1][-1]
#   decision_tree = CLIENT.get_decision_tree(AGENT_ID, last_operation["timestamp"])

#   assert_is_instance(decision_tree, dict)
#   assert_not_equal(decision_tree.get("_version"), None)
#   assert_not_equal(decision_tree.get("configuration"), None)
#   assert_not_equal(decision_tree.get("trees"), None)

# @with_setup(setup_agent_w_operations_l, teardown)
# def test_get_decision_tree_w_serverside_timeout():
#   other_client_cfg = settings.CRAFT_CFG.copy()
#   other_client_cfg["decisionTreeRetrievalTimeout"] = False
#   other_client = craftai.Client(other_client_cfg)
#   last_operation = VALID_L_OPERATIONS[-1][-1]
#   assert_raises(
#     craftai.errors.CraftAiLongRequestTimeOutError,
#     other_client.get_decision_tree,
#     AGENT_ID,
#     last_operation["timestamp"])

# @with_setup(setup_agent_w_operations_l, teardown)
# def test_get_decision_tree_w_smallish_timeout():
#   other_client_cfg = settings.CRAFT_CFG.copy()
#   other_client_cfg["decisionTreeRetrievalTimeout"] = 500
#   other_client = craftai.Client(other_client_cfg)
#   last_operation = VALID_L_OPERATIONS[-1][-1]
#   assert_raises(
#     craftai.errors.CraftAiLongRequestTimeOutError,
#     other_client.get_decision_tree,
#     AGENT_ID,
#     last_operation["timestamp"])
