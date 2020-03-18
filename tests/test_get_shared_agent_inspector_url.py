import unittest

from craft_ai import Client

from . import settings
from .utils import generate_entity_id
from .data import valid_data


class TestGetSharedAgentsInspectorUrlSuccess(unittest.TestCase):
    """Checks that the client succeeds when getting the agents list"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("get_inspector_url")

    def setUp(self):
        self.client.delete_agent(self.agent_id)
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)

    def tearDown(self):
        # Makes sure that no agent with the standard ID remains
        self.client.delete_agent(self.agent_id)

    def test_get_sharable_url(self):
        """get_shared_agent_inspector_url should create a new shareable url for the given agent"""
        timestamp = 1234567890987
        url = self.client.get_shared_agent_inspector_url(self.agent_id, timestamp)
        self.assertTrue(url != "")
        url_split = url.split("?")
        self.assertTrue(len(url_split) == 2)
        self.assertTrue(url_split[1] == "t=" + str(timestamp))
        url2 = self.client.get_shared_agent_inspector_url(self.agent_id)
        self.assertTrue(url_split[0] == url2)

    def test_get_sharable_url_with_no_timestamp(self):
        """
        shared_agent_inspector_url should create a new shareable url for the given
        agent with a timestamp in the query string
        """
        url = self.client.get_shared_agent_inspector_url(self.agent_id)
        self.assertTrue(url != "")
        url_split = url.split("?")
        self.assertTrue(len(url_split) == 1)
        url2 = self.client.get_shared_agent_inspector_url(self.agent_id)
        self.assertTrue(url == url2)

    def test_delete_sharable_url(self):
        """
        delete_shared_agent_inspector_url should delete the sharable url so the
        new sharable_url wouldn't be like the previous one
        """
        url = self.client.get_shared_agent_inspector_url(self.agent_id)
        self.assertTrue(url != "")
        url_split = url.split("?")
        self.assertTrue(len(url_split) == 1)
        url2 = self.client.get_shared_agent_inspector_url(self.agent_id)
        self.assertTrue(url == url2)
        self.client.delete_shared_agent_inspector_url(self.agent_id)
        url3 = self.client.get_shared_agent_inspector_url(self.agent_id)
        self.assertTrue(url != url3)
