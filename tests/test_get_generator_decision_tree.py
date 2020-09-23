import unittest

import copy
import datetime
import semver

import craft_ai
from craft_ai.constants import DEFAULT_DECISION_TREE_VERSION

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data

AGENT_ID_1_BASE = "get_gen_dt_1"
AGENT_ID_2_BASE = "get_gen_dt_2"
GENERATOR_BASE = "get_gen_dt_gen"


class TestGeneratorDecisionTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)

    def setUp(self):
        self.agent_id_1 = generate_entity_id(AGENT_ID_1_BASE + "dt")
        self.agent_id_2 = generate_entity_id(AGENT_ID_2_BASE + "dt")
        self.generator_id = generate_entity_id(GENERATOR_BASE + "dt")
        self.filter = [self.agent_id_1, self.agent_id_2]
        self.client.delete_agent(self.agent_id_1)
        self.client.delete_agent(self.agent_id_2)
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id_1)
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id_2)
        self.client.add_agent_operations(
            self.agent_id_1, valid_data.VALID_OPERATIONS_SET
        )
        self.client.add_agent_operations(
            self.agent_id_2, valid_data.VALID_OPERATIONS_SET
        )
        generator_configuration = copy.deepcopy(
            valid_data.VALID_GENERATOR_CONFIGURATION
        )
        generator_configuration["filter"] = self.filter
        self.client.delete_generator(self.generator_id)
        self.client.create_generator(generator_configuration, self.generator_id)

    def tearDown(self):
        self.client.delete_agent(self.agent_id_1)
        self.client.delete_agent(self.agent_id_2)
        self.client.delete_generator(self.generator_id)

    def test_get_generator_decision_tree_with_correct_input(self):
        decision_tree = self.client.get_generator_decision_tree(
            self.generator_id, valid_data.VALID_TIMESTAMP
        )

        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)
        tree_version = semver.VersionInfo.parse(decision_tree.get("_version")).to_dict()
        self.assertEqual(tree_version["major"], int(DEFAULT_DECISION_TREE_VERSION))

    def test_get_generator_decision_tree_with_specific_version(self):
        version = 1
        decision_tree = self.client.get_generator_decision_tree(
            self.generator_id, valid_data.VALID_TIMESTAMP, version
        )

        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        tree_version = semver.VersionInfo.parse(decision_tree.get("_version")).to_dict()
        self.assertEqual(tree_version["major"], version)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)

    def test_get_generator_decision_tree_with_specific_version2(self):
        version = 2
        decision_tree = self.client.get_generator_decision_tree(
            self.generator_id, valid_data.VALID_TIMESTAMP, version
        )

        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        tree_version = semver.VersionInfo.parse(decision_tree.get("_version")).to_dict()
        self.assertEqual(tree_version["major"], version)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)

    def test_get_generator_decision_tree_without_timestamp(self):
        # test if we get the latest decision tree
        decision_tree = self.client.get_generator_decision_tree(self.generator_id)
        ground_truth_decision_tree = (
            decision_tree
        ) = self.client.get_generator_decision_tree(self.generator_id, 1458741230 + 505)
        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)
        self.assertEqual(decision_tree, ground_truth_decision_tree)

    def test_get_generator_decision_tree_with_datetimedatetime(self):
        # test if we get the same decision tree
        decision_tree = self.client.get_generator_decision_tree(
            self.generator_id,
            datetime.datetime.fromtimestamp(valid_data.VALID_TIMESTAMP),
        )
        ground_truth_decision_tree = self.client.get_generator_decision_tree(
            self.generator_id, valid_data.VALID_TIMESTAMP
        )
        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)
        self.assertEqual(decision_tree, ground_truth_decision_tree)

    def test_get_generator_decision_tree_with_invalid_id(self):
        """get_generator_decision_tree should fail when given a non-string/empty string ID
        It should raise an error upon request for retrieval of an generator's
        decision tree with an ID that is not of type string, since generator IDs
        should always be strings.
        """
        for empty_id in invalid_data.UNDEFINED_KEY:
            self.assertRaises(
                craft_ai.errors.CraftAiBadRequestError,
                self.client.get_generator_decision_tree,
                invalid_data.UNDEFINED_KEY[empty_id],
                valid_data.VALID_TIMESTAMP,
            )

    def test_get_generator_decision_tree_with_unknown_id(self):
        """get_generator_decision_tree should fail when given an unknown generator ID
        It should raise an error upon request for the retrieval of an generator
        that doesn't exist.
        """
        self.assertRaises(
            craft_ai.errors.CraftAiNotFoundError,
            self.client.get_generator_decision_tree,
            invalid_data.UNKNOWN_ID,
            valid_data.VALID_TIMESTAMP,
        )

    def test_get_generator_decision_tree_with_negative_timestamp(self):
        self.assertRaises(
            craft_ai.errors.CraftAiBadRequestError,
            self.client.get_generator_decision_tree,
            self.generator_id,
            invalid_data.INVALID_TIMESTAMPS["negative_ts"],
        )

    def test_get_generator_decision_tree_with_float_timestamp(self):
        self.assertRaises(
            craft_ai.errors.CraftAiBadRequestError,
            self.client.get_generator_decision_tree,
            self.generator_id,
            invalid_data.INVALID_TIMESTAMPS["float_ts"],
        )
