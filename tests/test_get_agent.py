import unittest

import craftai

from . import settings
from .data import valid_data
from .data import invalid_data

class TestGetAgentSuccess(unittest.TestCase):
  """Checks that the client succeeds when getting an agent with OK input"""
  @classmethod
  def setUpClass(cls):
    cls.client = craftai.Client(settings.CRAFT_CFG)
    cls.agent_id = valid_data.VALID_ID  + "_" + settings.RUN_ID[-4:]

  def setUp(self):
    self.client.delete_agent(self.agent_id)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)

  def tearDown(self):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(self.agent_id)

  def test_get_agent_with_correct_id(self):
    """get_agent should succeed when given a correct agent ID

    It should give a proper JSON response with `configuration` field being a
    string.
    """
    agent = self.client.get_agent(self.agent_id)
    self.assertIsInstance(agent, dict)
    agent_keys = agent.keys()
    self.assertTrue("configuration" in agent_keys)


class TestGetAgentFailure(unittest.TestCase):
  """Checks that the client fails properly when getting an agent with bad input"""
  @classmethod
  def setUpClass(cls):
    cls.client = craftai.Client(settings.CRAFT_CFG)
    cls.agent_id = valid_data.VALID_ID  + "_" + settings.RUN_ID[-4:]

  def setUp(self):
    # Makes sure that no agent exists with the test id
    # (especially for test_get_agent_with_unknown_id)
    self.client.delete_agent(self.agent_id)

  def tearDown(self):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(self.agent_id)

  def test_get_agent_with_invalid_id(self):
    """get_agent should fail when given a non-string/empty string ID

    It should raise an error upon request for retrieval of
    an agent with an ID that is not of type string, since agent IDs
    should always be strings.
    """
    for empty_id in invalid_data.UNDEFINED_KEY:
      self.assertRaises(
        craftai.errors.CraftAiBadRequestError,
        self.client.get_agent,
        invalid_data.UNDEFINED_KEY[empty_id])

  def test_get_agent_with_unknown_id(self):
    """get_agent should fail when given an unknown agent ID

    It should raise an error upon request for the retrieval of an agent
    that doesn't exist.
    """
    self.assertRaises(
      craftai.errors.CraftAiNotFoundError,
      self.client.get_agent,
      invalid_data.UNKNOWN_ID)
