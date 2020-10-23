import unittest

import random
import datetime
import semver

import craft_ai
from craft_ai.constants import DEFAULT_DECISION_TREE_VERSION

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data

VALID_L_CFG = valid_data.VALID_LARGE_CONFIGURATION
VALID_L_BATCH_DURATION = VALID_L_CFG["learning_period"] * 4
VALID_L_ENUM_VALUES = ["CYAN", "MAGENTA", "YELLOW", "BLACK"]


def random_enum_value():
    return random.choice(VALID_L_ENUM_VALUES)


def random_continuous_value():
    return random.uniform(-12, 12)


VALID_L_OPERATIONS = [
    [
        # add 1600680210 (21 septembre 2020) to generate more representative timestamp
        {
            "timestamp": batch_offset * VALID_L_BATCH_DURATION
            + operation_offset
            + 1600680210,
            "context": {
                "e1": random_enum_value(),
                "e2": random_enum_value(),
                "e3": random_enum_value(),
                "e4": random_enum_value(),
                "c1": random_continuous_value(),
                "c2": random_continuous_value(),
                "c3": random_continuous_value(),
                "c4": random_continuous_value(),
                "tz": "CET",
            },
        }
        for operation_offset in range(0, VALID_L_BATCH_DURATION, 1000)
    ]
    for batch_offset in range(0, 6)
]


class TestGetAgentDecisionTreeWithOperation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("test_get_decision_tree")

    def setUp(self):
        self.client.delete_agent(self.agent_id)
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)
        self.client.add_agent_operations(self.agent_id, valid_data.VALID_OPERATIONS_SET)

    def tearDown(self):
        self.client.delete_agent(self.agent_id)

    def test_delete_agent_with_valid_id(self):
        resp = self.client.delete_agent(self.agent_id)
        self.assertIsInstance(resp, dict)
        self.assertTrue("id" in resp.keys())

    def test_get_decision_tree_with_correct_input(self):
        decision_tree = self.client.get_agent_decision_tree(
            self.agent_id, valid_data.VALID_TIMESTAMP
        )

        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)
        tree_version = semver.VersionInfo.parse(decision_tree.get("_version")).to_dict()
        self.assertEqual(tree_version["major"], int(DEFAULT_DECISION_TREE_VERSION))

    def test_get_decision_tree_with_specific_version(self):
        version = 1
        decision_tree = self.client.get_agent_decision_tree(
            self.agent_id, valid_data.VALID_TIMESTAMP, version
        )

        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        tree_version = semver.VersionInfo.parse(decision_tree.get("_version")).to_dict()
        self.assertEqual(tree_version["major"], version)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)

    def test_get_decision_tree_with_specific_version2(self):
        version = 2
        decision_tree = self.client.get_agent_decision_tree(
            self.agent_id, valid_data.VALID_TIMESTAMP, version
        )

        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        tree_version = semver.VersionInfo.parse(decision_tree.get("_version")).to_dict()
        self.assertEqual(tree_version["major"], version)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)

    def test_get_decision_tree_without_timestamp(self):
        # test if we get the latest decision tree
        decision_tree = self.client.get_agent_decision_tree(self.agent_id)
        ground_truth_decision_tree = (
            decision_tree
        ) = self.client.get_agent_decision_tree(self.agent_id, 1458741230 + 505)
        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)
        self.assertEqual(decision_tree, ground_truth_decision_tree)

    def test_get_decision_tree_with_datetimedatetime(self):
        # test if we get the same decision tree
        decision_tree = self.client.get_agent_decision_tree(
            self.agent_id, datetime.datetime.fromtimestamp(valid_data.VALID_TIMESTAMP)
        )
        ground_truth_decision_tree = self.client.get_agent_decision_tree(
            self.agent_id, valid_data.VALID_TIMESTAMP
        )
        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)
        self.assertEqual(decision_tree, ground_truth_decision_tree)

    def test_get_decision_tree_with_invalid_id(self):
        """get_agent_decision_tree should fail when given a non-string/empty string ID

        It should raise an error upon request for retrieval of an agent's
        decision tree with an ID that is not of type string, since agent IDs
        should always be strings.
        """
        for empty_id in invalid_data.UNDEFINED_KEY:
            self.assertRaises(
                craft_ai.errors.CraftAiBadRequestError,
                self.client.get_agent_decision_tree,
                invalid_data.UNDEFINED_KEY[empty_id],
                valid_data.VALID_TIMESTAMP,
            )

    def test_get_decision_tree_with_unknown_id(self):
        """get_agent_decision_tree should fail when given an unknown agent ID

        It should raise an error upon request for the retrieval of an agent
        that doesn't exist.
        """
        self.assertRaises(
            craft_ai.errors.CraftAiNotFoundError,
            self.client.get_agent_decision_tree,
            invalid_data.UNKNOWN_ID,
            valid_data.VALID_TIMESTAMP,
        )

    def test_get_decision_tree_with_negative_timestamp(self):
        self.assertRaises(
            craft_ai.errors.CraftAiBadRequestError,
            self.client.get_agent_decision_tree,
            self.agent_id,
            invalid_data.INVALID_TIMESTAMPS["negative_ts"],
        )

    def test_get_decision_tree_with_float_timestamp(self):
        self.assertRaises(
            craft_ai.errors.CraftAiBadRequestError,
            self.client.get_agent_decision_tree,
            self.agent_id,
            invalid_data.INVALID_TIMESTAMPS["float_ts"],
        )


@unittest.skip(
    "The following tests are quite long, they are disabled atm. (even before timescale)"
)
class TestGetAgentDecisionTreeWithOperationL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("test_get_decision_tree_with_op_l")

    def setUp(self):
        self.client.delete_agent(self.agent_id)
        self.client.create_agent(VALID_L_CFG, self.agent_id)
        for batch in VALID_L_OPERATIONS:
            self.client.add_agent_operations(self.agent_id, batch)

    def tearDown(self):
        self.client.delete_agent(self.agent_id)

    def test_get_decision_tree_from_operations(self):
        last_operation = VALID_L_OPERATIONS[-1][-1]
        decision_tree = self.client.get_agent_decision_tree(
            self.agent_id, last_operation["timestamp"],
        )
        self.assertIsInstance(decision_tree, dict)
        self.assertNotEqual(decision_tree.get("_version"), None)
        self.assertNotEqual(decision_tree.get("configuration"), None)
        self.assertNotEqual(decision_tree.get("trees"), None)

    def test_get_decision_tree_w_serverside_timeout(self):
        other_client_cfg = settings.CRAFT_CFG.copy()
        other_client_cfg["decisionTreeRetrievalTimeout"] = False
        other_client = craft_ai.Client(other_client_cfg)
        last_operation = VALID_L_OPERATIONS[-1][-1]
        self.assertRaises(
            craft_ai.errors.CraftAiLongRequestTimeOutError,
            other_client.get_agent_decision_tree,
            self.agent_id,
            last_operation["timestamp"],
        )

        def test_get_decision_tree_w_smallish_timeout(self):
            other_client_cfg = settings.CRAFT_CFG.copy()
            other_client_cfg["decisionTreeRetrievalTimeout"] = 500
            other_client = craft_ai.Client(other_client_cfg)
            last_operation = VALID_L_OPERATIONS[-1][-1]
            self.assertRaises(
                craft_ai.errors.CraftAiLongRequestTimeOutError,
                other_client.get_agent_decision_tree,
                self.agent_id,
                last_operation["timestamp"],
            )
