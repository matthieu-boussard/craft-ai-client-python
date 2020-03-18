import unittest
import json
import os

import craft_ai

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data

HERE = os.path.abspath(os.path.dirname(__file__))

LARGE_VALID_OPERATIONS_SET = []
with open(
    os.path.join(HERE, "./data/large_operation_list.json")
) as large_operation_list_file:
    LARGE_VALID_OPERATIONS_SET = json.load(large_operation_list_file)


class TestGetOperationsListSuccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("get_generator")

    def setUp(self):
        self.client.delete_agent(self.agent_id)
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)

        self.client.add_agent_operations(self.agent_id, LARGE_VALID_OPERATIONS_SET)

    def tearDown(self):
        self.client.delete_agent(self.agent_id)

    def test_get_agent_operations_with_correct_data(self):
        ops = self.client.get_agent_operations(self.agent_id)
        self.assertIsInstance(ops, list)
        self.assertEqual(ops, LARGE_VALID_OPERATIONS_SET)

    def test_get_agent_operations_with_lower_bound(self):
        lower_bound = 1464356844
        ops = self.client.get_agent_operations(self.agent_id, lower_bound)
        self.assertIsInstance(ops, list)
        expected_ops = [
            op for op in LARGE_VALID_OPERATIONS_SET if op["timestamp"] >= lower_bound
        ]
        self.assertEqual(ops, expected_ops)

    def test_get_agent_operations_with_upper_bound(self):
        upper_bound = 1462824549
        ops = self.client.get_agent_operations(self.agent_id, None, upper_bound)
        self.assertIsInstance(ops, list)
        expected_ops = [
            op for op in LARGE_VALID_OPERATIONS_SET if op["timestamp"] <= upper_bound
        ]
        self.assertEqual(ops, expected_ops)

    def test_get_agent_operations_with_both_bounds(self):
        lower_bound = 1462824549
        upper_bound = 1464356844
        ops = self.client.get_agent_operations(self.agent_id, lower_bound, upper_bound)
        self.assertIsInstance(ops, list)
        expected_ops = [
            op
            for op in LARGE_VALID_OPERATIONS_SET
            if (op["timestamp"] >= lower_bound and op["timestamp"] <= upper_bound)
        ]
        self.assertEqual(ops, expected_ops)

    def test_get_agent_operations_with_inverted_bounds(self):
        lower_bound = 1464356844
        upper_bound = 1462824549
        ops = self.client.get_agent_operations(self.agent_id, lower_bound, upper_bound)
        self.assertIsInstance(ops, list)
        self.assertEqual(ops, [])


class TestGetOperationsListFailure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("get_operations")

    def setUp(self):
        self.client.delete_agent(self.agent_id)
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)
        self.client.add_agent_operations(self.agent_id, valid_data.VALID_OPERATIONS_SET)

    def tearDown(self):
        self.client.delete_agent(self.agent_id)

    def test_get_agent_operations_with_invalid_id(self):
        for empty_id in invalid_data.UNDEFINED_KEY:
            self.assertRaises(
                craft_ai.errors.CraftAiBadRequestError,
                self.client.get_agent_operations,
                invalid_data.UNDEFINED_KEY[empty_id],
            )
