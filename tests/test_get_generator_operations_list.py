import unittest
import json
import os

import craft_ai

from . import settings
from .data import valid_data, invalid_data

HERE = os.path.abspath(os.path.dirname(__file__))

LARGE_VALID_OPERATIONS_SET = []
with open(
    os.path.join(HERE, "./data/large_operation_list.json")
) as large_operation_list_file:
    LARGE_VALID_OPERATIONS_SET = json.load(large_operation_list_file)

SMALL_VALID_OPERATIONS_SET = []
with open(
    os.path.join(HERE, "./data/small_operation_list.json")
) as small_operation_list_file:
    SMALL_VALID_OPERATIONS_SET = json.load(small_operation_list_file)
# Add a context property so both sets of operations match the same configuration
SMALL_VALID_OPERATIONS_SET[0]["context"]["tz"] = "+02:00"


def merge_sorted_operation_arrays_by_timestamp(operations_a, operations_b):
    merged_operations = []
    cursor_a = 0
    cursor_b = 0

    while cursor_a < len(operations_a) and cursor_b < len(operations_b):
        if operations_a[cursor_a]["timestamp"] <= operations_b[cursor_b]["timestamp"]:
            merged_operations.append(operations_a[cursor_a])
            cursor_a = cursor_a + 1
        else:
            merged_operations.append(operations_b[cursor_b])
            cursor_b = cursor_b + 1

    (array_to_add_from, cursor_to_add_from) = (
        (operations_a, cursor_a)
        if cursor_a < len(operations_a)
        else (operations_b, cursor_b)
    )
    while cursor_to_add_from < len(array_to_add_from):
        merged_operations.append(array_to_add_from[cursor_to_add_from])
        cursor_to_add_from = cursor_to_add_from + 1

    return merged_operations


class TestGetGeneratorOperationsListSuccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.generator_id = valid_data.VALID_GENERATOR_ID + "_" + settings.RUN_ID[-4:]
        cls.agent_id_1 = valid_data.VALID_ID + "_" + settings.RUN_ID[-4:]
        cls.agent_id_2 = valid_data.VALID_ID_TWO + "_" + settings.RUN_ID[-4:]
        cls.filter = [cls.agent_id_1, cls.agent_id_2]

    def setUp(self):
        self.client.delete_generator(self.generator_id)
        self.client.delete_agent(self.agent_id_1)
        self.client.delete_agent(self.agent_id_2)
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id_1)
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id_2)
        self.client.add_operations(self.agent_id_1, LARGE_VALID_OPERATIONS_SET)
        self.client.add_operations(self.agent_id_2, SMALL_VALID_OPERATIONS_SET)

        def add_agent_name_1_to_operation(operation):
            return {
                "agent_id": self.agent_id_1,
                "context": operation["context"],
                "timestamp": operation["timestamp"],
            }

        expected_operations_1 = list(
            map(add_agent_name_1_to_operation, LARGE_VALID_OPERATIONS_SET)
        )

        def add_agent_name_2_to_operation(operation):
            return {
                "agent_id": self.agent_id_2,
                "context": operation["context"],
                "timestamp": operation["timestamp"],
            }

        expected_operations_2 = list(
            map(add_agent_name_2_to_operation, SMALL_VALID_OPERATIONS_SET)
        )
        self.expected_operations = merge_sorted_operation_arrays_by_timestamp(
            expected_operations_1, expected_operations_2
        )

        generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        generator_configuration["filter"] = self.filter
        self.client.create_generator(generator_configuration, self.generator_id)

    def tearDown(self):
        self.client.delete_generator(self.generator_id)
        self.client.delete_agent(self.agent_id_1)
        self.client.delete_agent(self.agent_id_2)

    def test_get_generator_operations_list_with_correct_data(self):
        ops = self.client.get_generator_operations_list(self.generator_id)
        self.assertIsInstance(ops, list)
        self.assertEqual(len(ops), len(self.expected_operations))
        self.assertEqual(ops, self.expected_operations)

    def test_get_generator_operations_list_with_lower_bound(self):
        lower_bound = 1464600406
        ops = self.client.get_generator_operations_list(self.generator_id, lower_bound)
        self.assertIsInstance(ops, list)
        expected_ops = [
            op for op in self.expected_operations if op["timestamp"] >= lower_bound
        ]
        self.assertEqual(ops, expected_ops)

    def test_get_generator_operations_list_with_upper_bound(self):
        upper_bound = 1462824549
        ops = self.client.get_generator_operations_list(
            self.generator_id, None, upper_bound
        )
        self.assertIsInstance(ops, list)
        expected_ops = [
            op for op in self.expected_operations if op["timestamp"] <= upper_bound
        ]
        self.assertEqual(ops, expected_ops)

    def test_get_generator_operations_list_with_both_bounds(self):
        lower_bound = 1462824549
        upper_bound = 1464356844
        ops = self.client.get_generator_operations_list(
            self.generator_id, lower_bound, upper_bound
        )
        self.assertIsInstance(ops, list)
        expected_ops = [
            op
            for op in self.expected_operations
            if (op["timestamp"] >= lower_bound and op["timestamp"] <= upper_bound)
        ]
        self.assertEqual(ops, expected_ops)

    def test_get_generator_operations_list_with_inverted_bounds(self):
        lower_bound = 1464356844
        upper_bound = 1462824549
        ops = self.client.get_generator_operations_list(
            self.generator_id, lower_bound, upper_bound
        )
        self.assertIsInstance(ops, list)
        self.assertEqual(ops, [])


class TestGetOperationsListFailure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.agent_id = valid_data.VALID_ID + "_" + settings.RUN_ID[-4:]
        cls.generator_id = valid_data.VALID_GENERATOR_ID + "_" + settings.RUN_ID[-4:]

    def setUp(self):
        self.client.delete_agent(self.agent_id)
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)
        self.client.add_operations(self.agent_id, valid_data.VALID_OPERATIONS_SET)
        self.client.delete_generator(self.generator_id)
        generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        generator_configuration["filter"] = [self.agent_id]
        self.client.create_generator(generator_configuration, self.generator_id)

    def tearDown(self):
        self.client.delete_agent(self.agent_id)
        self.client.delete_generator(self.generator_id)

    def test_get_generator_operations_list_with_invalid_id(self):
        for empty_id in invalid_data.UNDEFINED_KEY:
            self.assertRaises(
                craft_ai.errors.CraftAiBadRequestError,
                self.client.get_generator_operations_list,
                invalid_data.UNDEFINED_KEY[empty_id],
            )
