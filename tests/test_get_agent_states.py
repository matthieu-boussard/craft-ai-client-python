import unittest
import craft_ai

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data


class TestGetAgentStatesSuccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("test_get_agent_states")

    def setUp(self):
        self.client.delete_agent(self.agent_id)
        self.client.create_agent(
            {
                "context": {
                    "tz": {"type": "timezone"},
                    "presence": {"type": "enum"},
                    "lightIntensity": {"type": "continuous"},
                    "lightbulbColor": {"type": "enum"},
                },
                "output": valid_data.VALID_OUTPUT,
                "time_quantum": valid_data.VALID_TQ,
            },
            self.agent_id,
        )

        self.client.add_agent_operations(self.agent_id, valid_data.VALID_OPERATIONS_SET)

    def tearDown(self):
        self.client.delete_agent(self.agent_id)

    def test_get_agent_states_with_correct_data(self):
        states = self.client.get_agent_states(self.agent_id)
        self.assertIsInstance(states, list)
        self.assertEqual(
            states,
            [
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "occupant",
                        "lightIntensity": 1,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741230,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "occupant",
                        "lightIntensity": 1,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741330,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "player",
                        "lightIntensity": 0.5,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741430,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741530,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "occupant+player",
                        "lightIntensity": 0,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741630,
                },
                {
                    "sample": {
                        "tz": "+01:00",
                        "presence": "occupant",
                        "lightIntensity": 0.8,
                        "lightbulbColor": "#f56fff",
                    },
                    "timestamp": 1458741730,
                },
            ],
        )

    def test_get_agent_states_with_lower_bound(self):
        lower_bound = valid_data.VALID_TIMESTAMP + valid_data.VALID_TQ
        states = self.client.get_agent_states(self.agent_id, lower_bound)
        self.assertIsInstance(states, list)
        self.assertEqual(
            states,
            [
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "occupant",
                        "lightIntensity": 1,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741330,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "player",
                        "lightIntensity": 0.5,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741430,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741530,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "occupant+player",
                        "lightIntensity": 0,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741630,
                },
                {
                    "sample": {
                        "tz": "+01:00",
                        "presence": "occupant",
                        "lightIntensity": 0.8,
                        "lightbulbColor": "#f56fff",
                    },
                    "timestamp": 1458741730,
                },
            ],
        )

    def test_get_agent_states_with_upper_bound(self):
        upper_bound = valid_data.VALID_LAST_TIMESTAMP - valid_data.VALID_TQ
        states = self.client.get_agent_states(self.agent_id, None, upper_bound)
        self.assertIsInstance(states, list)
        self.assertEqual(
            states,
            [
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "occupant",
                        "lightIntensity": 1,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741230,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "occupant",
                        "lightIntensity": 1,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741330,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "player",
                        "lightIntensity": 0.5,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741430,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741530,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "occupant+player",
                        "lightIntensity": 0,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741630,
                },
            ],
        )

    def test_get_agent_states_with_both_bounds(self):
        lower_bound = valid_data.VALID_TIMESTAMP + valid_data.VALID_TQ
        upper_bound = valid_data.VALID_LAST_TIMESTAMP - valid_data.VALID_TQ
        states = self.client.get_agent_states(self.agent_id, lower_bound, upper_bound)
        self.assertIsInstance(states, list)
        self.assertEqual(
            states,
            [
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "occupant",
                        "lightIntensity": 1,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741330,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "player",
                        "lightIntensity": 0.5,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741430,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "none",
                        "lightIntensity": 0,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741530,
                },
                {
                    "sample": {
                        "tz": "+02:00",
                        "presence": "occupant+player",
                        "lightIntensity": 0,
                        "lightbulbColor": "#ffffff",
                    },
                    "timestamp": 1458741630,
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
        self.client.add_agent_operations(self.agent_id, valid_data.VALID_OPERATIONS_SET)

    def tearDown(self):
        self.client.delete_agent(self.agent_id)

    def test_get_agent_states_with_invalid_id(self):
        for empty_id in invalid_data.UNDEFINED_KEY:
            self.assertRaises(
                craft_ai.errors.CraftAiBadRequestError,
                self.client.get_agent_states,
                invalid_data.UNDEFINED_KEY[empty_id],
            )
