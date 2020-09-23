import unittest
import semver

from craft_ai import Client, errors as craft_err

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data

from craft_ai.constants import DEFAULT_DECISION_TREE_VERSION


class TestGetDecisionTreesBulkSuccess(unittest.TestCase):
    """Checks that the client succeeds when getting
    an/multiple decision tree(s) with OK input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id1 = generate_entity_id("test_g_bulk_a1")
        cls.agent_id2 = generate_entity_id("test_g_bulk_a2")
        cls.generator_id1 = generate_entity_id("test_g_bulk_g1")
        cls.generator_id2 = generate_entity_id("test_g_bulk_g2")
        cls.filter = [cls.agent_id1, cls.agent_id2]
        cls.generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        cls.generator_configuration["filter"] = cls.filter

    def setUp(self):
        try:
            self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id1)
            self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id2)
            self.client.add_agent_operations(
                self.agent_id1, valid_data.VALID_OPERATIONS_SET
            )
            self.client.add_agent_operations(
                self.agent_id2, valid_data.VALID_OPERATIONS_SET
            )

            self.client.create_generator(
                self.generator_configuration, self.generator_id1
            )
            self.client.create_generator(
                self.generator_configuration, self.generator_id2
            )

        except craft_err.CraftAiBadRequestError as e:
            if "one already exists" not in e.message:
                raise e

    def tearDown(self):
        self.client.delete_agent(self.agent_id1)
        self.client.delete_agent(self.agent_id2)
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def clean_up_generators(self):
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def test_get_one_decision_tree_with_correct_input(self):
        """get_generarots_decision_trees_bulk should succeed when given a correct input.

        It should give a proper JSON response with a list containing a dict
        with `id` field being string and 'tree' field being a dict. As we don't
        specify the version the field 'tree''_version' should be the one by default.
        """

        payload = [
            {"id": self.generator_id1, "timestamp": valid_data.VALID_LAST_TIMESTAMP}
        ]

        decision_trees = self.client.get_generators_decision_trees_bulk(payload)

        self.assertIsInstance(decision_trees, list)
        self.assertIsInstance(decision_trees[0], dict)
        self.assertIsInstance(decision_trees[0].get("tree"), dict)
        self.assertNotEqual(decision_trees[0].get("tree").get("_version"), None)
        tree_version = semver.VersionInfo.parse(decision_trees[0].get("tree").get("_version")).to_dict()
        self.assertEqual(tree_version["major"], int(DEFAULT_DECISION_TREE_VERSION))
        self.assertNotEqual(decision_trees[0].get("tree").get("configuration"), None)
        self.assertNotEqual(decision_trees[0].get("tree").get("trees"), None)

        self.addCleanup(self.clean_up_generators)

    def test_get_multiple_decision_trees_with_correct_input(self):
        """delete_generators_bulk should succeed when given a list of string ID in a set
            It should give a proper JSON response with a list containing the dict
            with the `ids being the same as the one given as parameter."""

        payload = [
            {"id": self.generator_id1, "timestamp": valid_data.VALID_LAST_TIMESTAMP},
            {"id": self.generator_id2, "timestamp": valid_data.VALID_LAST_TIMESTAMP},
        ]
        decision_trees = self.client.get_generators_decision_trees_bulk(payload)
        self.assertEqual(decision_trees[0].get("id"), self.generator_id1)
        self.assertEqual(decision_trees[1].get("id"), self.generator_id2)
        self.assertIsInstance(decision_trees[0].get("tree").get("_version"), str)
        self.assertIsInstance(decision_trees[1].get("tree").get("_version"), str)

        self.addCleanup(self.tearDown)


class TestGetDecisionTreesBulkFailure(unittest.TestCase):
    """Checks that the client succeeds when getting
    an/multiple decision tree(s) with OK input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)

    def test_get_all_decision_trees_with_invalid_id(self):
        """get_generators_decision_trees_bulk should fail when given non-string/empty string ID
        or unknown ID.

        It should raise an error upon request for retrieval of multiple generators's
        decision tree with an ID that is not of type string, since generator IDs
        should always be strings.
        """
        # Add an unknown id and a dictionary without an id field
        payload = [
            {
                "id": invalid_data.UNKNOWN_ID,
                "timestamp": valid_data.VALID_LAST_TIMESTAMP,
            },
            {"timestamp": valid_data.VALID_TIMESTAMP},
        ]
        # Add all the invalid id to check
        for empty_id in invalid_data.UNDEFINED_KEY:
            payload.append(
                {
                    "id": invalid_data.UNDEFINED_KEY[empty_id],
                    "timestamp": valid_data.VALID_LAST_TIMESTAMP,
                }
            )

        self.assertRaises(
            craft_err.CraftAiBadRequestError,
            self.client.get_generators_decision_trees_bulk,
            payload,
        )


class TestGetDecisionTreesBulkSomeFailure(unittest.TestCase):
    """Checks that the client succeed when getting an/multiple generator(s)
    with bad input and an/multiple generator(s) with valid input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id1 = generate_entity_id("test_delete_g_bulk_a1")
        cls.agent_id2 = generate_entity_id("test_delete_g_bulk_a2")
        cls.generator_id1 = generate_entity_id("test_delete_g_bulk_g1")
        cls.generator_id2 = generate_entity_id("test_delete_g_bulk_g2")
        cls.filter = [cls.agent_id1, cls.agent_id2]
        cls.generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        cls.generator_configuration["filter"] = cls.filter

    def setUp(self):
        try:
            self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id1)
            self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id2)
            self.client.add_agent_operations(
                self.agent_id1, valid_data.VALID_OPERATIONS_SET
            )
            self.client.add_agent_operations(
                self.agent_id2, valid_data.VALID_OPERATIONS_SET
            )

            self.client.create_generator(
                self.generator_configuration, self.generator_id1
            )
            self.client.create_generator(
                self.generator_configuration, self.generator_id2
            )

        except craft_err.CraftAiBadRequestError as e:
            if "one already exists" not in e.message:
                raise e

    def tearDown(self):
        self.client.delete_agent(self.agent_id1)
        self.client.delete_agent(self.agent_id2)
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def clean_up_generators(self):
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def test_get_some_decision_trees_with_invalid_id(self):
        """get_generators_decision_trees_bulk should succeed when given some non-string/empty string IDs
        and some valid IDs.

        It should give a proper JSON response with a list containing dicts.
        The ones having invalid ids have the `error` field being a CraftAiBadRequestError.
        The ones having valid ids have the `id` field being string and 'tree' field being a dict.
        """
        # Add valid id and timestamp
        payload = [
            {"id": self.generator_id1, "timestamp": valid_data.VALID_LAST_TIMESTAMP}
        ]
        # Add an unknown id and a dictionary without an id field
        payload.append(
            [
                {
                    "id": invalid_data.UNKNOWN_ID,
                    "timestamp": valid_data.VALID_LAST_TIMESTAMP,
                },
                {"timestamp": valid_data.VALID_TIMESTAMP},
            ]
        )
        # Add all the invalid id to check
        for empty_id in invalid_data.UNDEFINED_KEY:
            payload.append(
                {
                    "id": invalid_data.UNDEFINED_KEY[empty_id],
                    "timestamp": valid_data.VALID_LAST_TIMESTAMP,
                }
            )

        decision_trees = self.client.get_generators_decision_trees_bulk(payload)

        self.assertEqual(decision_trees[0].get("id"), self.generator_id1)
        self.assertIsInstance(decision_trees[0].get("tree"), dict)
        self.assertNotEqual(decision_trees[0].get("tree").get("_version"), None)
        self.assertNotEqual(decision_trees[0].get("tree").get("configuration"), None)
        self.assertNotEqual(decision_trees[0].get("tree").get("trees"), None)

        for i in range(1, len(decision_trees)):
            self.assertTrue("error" in decision_trees[i])

        self.addCleanup(self.clean_up_generators)
