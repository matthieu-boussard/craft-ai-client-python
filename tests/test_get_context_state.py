import unittest

# Preserving the 'old' way to do the imports here to ensure retrocompatibility
from craft_ai.client import CraftAIClient
from craft_ai import errors as craft_err

from . import settings
from .data import valid_data, invalid_data

class TestGetContextStateSuccess(unittest.TestCase):
  """Checks that the client succeeds when retrieving an agent's current state
  with OK input.
  """
  @classmethod
  def setUpClass(cls):
    cls.client = CraftAIClient(settings.CRAFT_CFG)
    cls.agent_id = valid_data.VALID_ID  + "_" + settings.RUN_ID

  def setUp(self):
    self.client.delete_agent(self.agent_id)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)
    self.client.add_operations(
      self.agent_id,
      valid_data.VALID_OPERATIONS_SET)

  def tearDown(self):
    self.client.delete_agent(self.agent_id)

  def test_get_context_state_with_correct_input(self):
    """get_context_state should succeed when given proper ID and timestamp.

    It should give a proper JSON response with `timestamp` field being an
    integer and equal to the requested one, and a `diff` field containing
    a dict.
    """
    context_state = self.client.get_context_state(
      self.agent_id,
      valid_data.VALID_TIMESTAMP)
    self.assertIsInstance(context_state, dict)
    context_state_keys = context_state.keys()
    self.assertTrue("timestamp" in context_state_keys)
    self.assertIsInstance(context_state["timestamp"], int)
    self.assertEqual(
      context_state["timestamp"],
      valid_data.VALID_TIMESTAMP)


class TestGetContextStateFailure(unittest.TestCase):
  """Checks that the client fails properly when getting an agent's context
  with bad input"""
  @classmethod
  def setUpClass(cls):
    cls.client = CraftAIClient(settings.CRAFT_CFG)
    cls.agent_id = valid_data.VALID_ID  + "_" + settings.RUN_ID

  def setUp(self):
    self.client.delete_agent(self.agent_id)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)
    self.client.add_operations(
      self.agent_id,
      valid_data.VALID_OPERATIONS_SET)

  def tearDown(self):
    self.client.delete_agent(self.agent_id)

  def test_get_context_state_with_invalid_id(self):
    """get_context_state should fail when given a non-string/empty string ID

    It should raise an error upon request for retrieval of
    an agent with an ID that is not of type string, since agent IDs
    should always be strings.
    """
    for empty_id in invalid_data.UNDEFINED_KEY:
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.get_context_state,
        invalid_data.UNDEFINED_KEY[empty_id],
        valid_data.VALID_TIMESTAMP)

  def test_get_context_state_with_unknown_id(self):
    """get_context_state should fail when given an unknown agent ID

    It should raise an error upon request for the retrieval of an agent
    that doesn't exist.
    """
    self.assertRaises(
      craft_err.CraftAiNotFoundError,
      self.client.get_context_state,
      invalid_data.UNKNOWN_ID,
      valid_data.VALID_TIMESTAMP)

  def test_get_context_state_with_invalid_timestamp(self):
    for inv_ts in invalid_data.INVALID_TIMESTAMPS:
      if not inv_ts is None:
        self.assertRaises(
          craft_err.CraftAiBadRequestError,
          self.client.get_context_state,
          self.agent_id,
          invalid_data.INVALID_TIMESTAMPS[inv_ts])
