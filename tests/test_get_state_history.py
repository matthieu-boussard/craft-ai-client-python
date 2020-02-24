import unittest
import json
import os

import craft_ai

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data

HERE = os.path.abspath(os.path.dirname(__file__))

SMALL_VALID_OPERATIONS_SET = []
with open(
    os.path.join(HERE, "./data/small_operation_list.json")
) as small_operation_list_file:
    SMALL_VALID_OPERATIONS_SET = json.load(small_operation_list_file)


class TestGetStateHistorySuccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("get_state_history")

    def setUp(self):
        self.client.delete_agent(self.agent_id)
        self.client.create_agent(
            {
                "context": {
                    "presence": {"type": "enum"},
                    "lightIntensity": {"type": "continuous"},
                    "lightbulbColor": {"type": "enum"},
                },
                "output": valid_data.VALID_OUTPUT,
                "time_quantum": valid_data.VALID_TQ,
            },
            self.agent_id,
        )

        self.client.add_operations(self.agent_id, SMALL_VALID_OPERATIONS_SET)

    def tearDown(self):
        self.client.delete_agent(self.agent_id)

    def test_get_state_history_with_correct_data(self):
        states = self.client.get_state_history(self.agent_id)
        self.assertIsInstance(states, list)
        self.assertEqual(
            states,
            [
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464600000,
                },
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464600100,
                },
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464600200,
                },
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464600300,
                },
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464600400,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600500,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600600,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600700,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600800,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600900,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601000,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601100,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601200,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601300,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601400,
                },
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.6,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464601500,
                },
            ],
        )

    def test_get_state_history_with_lower_bound(self):
        lower_bound = 1464600867
        states = self.client.get_state_history(self.agent_id, lower_bound)
        self.assertIsInstance(states, list)
        self.assertEqual(
            states,
            [
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600900,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601000,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601100,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601200,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601300,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601400,
                },
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.6,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464601500,
                },
            ],
        )

    def test_get_state_history_with_upper_bound(self):
        upper_bound = 1464601439
        states = self.client.get_state_history(self.agent_id, None, upper_bound)
        self.assertIsInstance(states, list)
        self.assertEqual(
            states,
            [
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464600000,
                },
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464600100,
                },
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464600200,
                },
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464600300,
                },
                {
                    "sample": {
                        "presence": "robert",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "green",
                    },
                    "timestamp": 1464600400,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600500,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600600,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600700,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600800,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600900,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601000,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601100,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601200,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601300,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601400,
                },
            ],
        )

    def test_get_state_history_with_both_bounds(self):
        lower_bound = 1464600449
        upper_bound = 1464601124
        states = self.client.get_state_history(self.agent_id, lower_bound, upper_bound)
        self.assertIsInstance(states, list)
        self.assertEqual(
            states,
            [
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600500,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600600,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600700,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600800,
                },
                {
                    "sample": {
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "black",
                    },
                    "timestamp": 1464600900,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601000,
                },
                {
                    "sample": {
                        "presence": "gisele",
                        "lightIntensity": 0.4,
                        "lightbulbColor": "blue",
                    },
                    "timestamp": 1464601100,
                },
            ],
        )


class TestGetOperationsListFailure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("get_operations")

        def setUp(self):
            self.client.delete_agent(self.agent_id)
            self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)
            self.client.add_operations(self.agent_id, valid_data.VALID_OPERATIONS_SET)

        def tearDown(self):
            self.client.delete_agent(self.agent_id)

        def test_get_state_history_with_invalid_id(self):
            for empty_id in invalid_data.UNDEFINED_KEY:
                self.assertRaises(
                    craft_ai.errors.CraftAiBadRequestError,
                    self.client.get_state_history,
                    invalid_data.UNDEFINED_KEY[empty_id],
                )
