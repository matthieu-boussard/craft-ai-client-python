import copy
import datetime
import semver

from nose.tools import (
    assert_equal,
    assert_is_instance,
    assert_not_equal,
    assert_raises,
    with_setup,
)
import craft_ai
from craft_ai.constants import DEFAULT_DECISION_TREE_VERSION

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data

CLIENT = craft_ai.Client(settings.CRAFT_CFG)
AGENT_ID_1 = generate_entity_id("test_get_decision_tree")
AGENT_ID_2 = generate_entity_id("test_get_decision_tree")
GENERATOR_ID = generate_entity_id("test_generator_decision_tree")
FILTER = [AGENT_ID_1, AGENT_ID_2]


def setup_generator_with_agent_with_operations():
    CLIENT.delete_agent(AGENT_ID_1)
    CLIENT.delete_agent(AGENT_ID_2)
    CLIENT.create_agent(valid_data.VALID_CONFIGURATION, AGENT_ID_1)
    CLIENT.create_agent(valid_data.VALID_CONFIGURATION, AGENT_ID_2)
    CLIENT.add_agent_operations(AGENT_ID_1, valid_data.VALID_OPERATIONS_SET)
    CLIENT.add_agent_operations(AGENT_ID_2, valid_data.VALID_OPERATIONS_SET)
    generator_configuration = copy.deepcopy(valid_data.VALID_GENERATOR_CONFIGURATION)
    generator_configuration["filter"] = [AGENT_ID_1, AGENT_ID_2]
    CLIENT.create_generator(generator_configuration, GENERATOR_ID)


def teardown():
    CLIENT.delete_agent(AGENT_ID_1)
    CLIENT.delete_agent(AGENT_ID_2)
    CLIENT.delete_generator(GENERATOR_ID)


@with_setup(setup_generator_with_agent_with_operations, teardown)
def test_get_generator_decision_tree_with_correct_input():
    decision_tree = CLIENT.get_generator_decision_tree(
        GENERATOR_ID, valid_data.VALID_TIMESTAMP
    )

    assert_is_instance(decision_tree, dict)
    assert_not_equal(decision_tree.get("_version"), None)
    assert_not_equal(decision_tree.get("configuration"), None)
    assert_not_equal(decision_tree.get("trees"), None)
    tree_version = semver.parse(decision_tree.get("_version"))
    assert_equal(tree_version["major"], int(DEFAULT_DECISION_TREE_VERSION))


@with_setup(setup_generator_with_agent_with_operations, teardown)
def test_get_generator_decision_tree_with_specific_version():
    version = 1
    decision_tree = CLIENT.get_generator_decision_tree(
        GENERATOR_ID, valid_data.VALID_TIMESTAMP, version
    )

    assert_is_instance(decision_tree, dict)
    assert_not_equal(decision_tree.get("_version"), None)
    tree_version = semver.parse(decision_tree.get("_version"))
    assert_equal(tree_version["major"], version)
    assert_not_equal(decision_tree.get("configuration"), None)
    assert_not_equal(decision_tree.get("trees"), None)


@with_setup(setup_generator_with_agent_with_operations, teardown)
def test_get_generator_decision_tree_with_specific_version2():
    version = 2
    decision_tree = CLIENT.get_generator_decision_tree(
        GENERATOR_ID, valid_data.VALID_TIMESTAMP, version
    )

    assert_is_instance(decision_tree, dict)
    assert_not_equal(decision_tree.get("_version"), None)
    tree_version = semver.parse(decision_tree.get("_version"))
    assert_equal(tree_version["major"], version)
    assert_not_equal(decision_tree.get("configuration"), None)
    assert_not_equal(decision_tree.get("trees"), None)


@with_setup(setup_generator_with_agent_with_operations, teardown)
def test_get_generator_decision_tree_without_timestamp():
    # test if we get the latest decision tree
    decision_tree = CLIENT.get_generator_decision_tree(GENERATOR_ID)
    ground_truth_decision_tree = decision_tree = CLIENT.get_generator_decision_tree(
        GENERATOR_ID, 1458741230 + 505
    )
    assert_is_instance(decision_tree, dict)
    assert_not_equal(decision_tree.get("_version"), None)
    assert_not_equal(decision_tree.get("configuration"), None)
    assert_not_equal(decision_tree.get("trees"), None)
    assert_equal(decision_tree, ground_truth_decision_tree)


@with_setup(setup_generator_with_agent_with_operations, teardown)
def test_get_generator_decision_tree_with_datetimedatetime():
    # test if we get the same decision tree
    decision_tree = CLIENT.get_generator_decision_tree(
        GENERATOR_ID, datetime.datetime.fromtimestamp(valid_data.VALID_TIMESTAMP)
    )
    ground_truth_decision_tree = CLIENT.get_generator_decision_tree(
        GENERATOR_ID, valid_data.VALID_TIMESTAMP
    )
    assert_is_instance(decision_tree, dict)
    assert_not_equal(decision_tree.get("_version"), None)
    assert_not_equal(decision_tree.get("configuration"), None)
    assert_not_equal(decision_tree.get("trees"), None)
    assert_equal(decision_tree, ground_truth_decision_tree)


@with_setup(setup_generator_with_agent_with_operations, teardown)
def test_get_generator_decision_tree_with_invalid_id():
    """get_generator_decision_tree should fail when given a non-string/empty string ID

  It should raise an error upon request for retrieval of an generator's
  decision tree with an ID that is not of type string, since generator IDs
  should always be strings.
  """
    for empty_id in invalid_data.UNDEFINED_KEY:
        assert_raises(
            craft_ai.errors.CraftAiBadRequestError,
            CLIENT.get_generator_decision_tree,
            invalid_data.UNDEFINED_KEY[empty_id],
            valid_data.VALID_TIMESTAMP,
        )


@with_setup(setup_generator_with_agent_with_operations, teardown)
def test_get_generator_decision_tree_with_unknown_id():
    """get_generator_decision_tree should fail when given an unknown generator ID

  It should raise an error upon request for the retrieval of an generator
  that doesn't exist.
  """
    assert_raises(
        craft_ai.errors.CraftAiNotFoundError,
        CLIENT.get_generator_decision_tree,
        invalid_data.UNKNOWN_ID,
        valid_data.VALID_TIMESTAMP,
    )


@with_setup(setup_generator_with_agent_with_operations, teardown)
def test_get_generator_decision_tree_with_negative_timestamp():
    assert_raises(
        craft_ai.errors.CraftAiBadRequestError,
        CLIENT.get_generator_decision_tree,
        GENERATOR_ID,
        invalid_data.INVALID_TIMESTAMPS["negative_ts"],
    )


@with_setup(setup_generator_with_agent_with_operations, teardown)
def test_get_generator_decision_tree_with_float_timestamp():
    assert_raises(
        craft_ai.errors.CraftAiBadRequestError,
        CLIENT.get_generator_decision_tree,
        GENERATOR_ID,
        invalid_data.INVALID_TIMESTAMPS["float_ts"],
    )