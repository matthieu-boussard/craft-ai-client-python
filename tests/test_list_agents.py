import unittest

import craft_ai

from . import settings
from .utils import generate_entity_id
from .data import valid_data


class TestListAgents(unittest.TestCase):
    """Checks that the client succeeds when getting an agent with OK input"""

    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.n_agents = 5
        cls.agents_id = [generate_entity_id("list_agents") for i in range(cls.n_agents)]

    def setUp(self):
        for agent_id in self.agents_id:
            self.client.delete_agent(agent_id)
            self.client.create_agent(valid_data.VALID_CONFIGURATION, agent_id)

    def tearDown(self):
        # Makes sure that no agent with the standard ID remains
        for agent_id in self.agents_id:
            self.client.delete_agent(agent_id)

    def test_list_agents(self):
        """list_agents should returns the list of agents in the current project."""
        agents_list = self.client.list_agents()
        self.assertIsInstance(agents_list, list)
        for agent_id in self.agents_id:
            self.assertTrue(agent_id in agents_list)
