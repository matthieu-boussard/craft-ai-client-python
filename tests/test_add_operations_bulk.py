import unittest
import six

from nose.tools import nottest
from craftai import Client, errors as craft_err

from . import settings
from .data import valid_data
from .data import invalid_data

class TestAddOperationsBulkSuccess(unittest.TestCase):
  """Checks that the client succeeds when adding operations to
  multiple agent(s) with OK input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID_TWO  + "_" + settings.RUN_ID

  def setUp(self):
    self.client.delete_agent(self.agent_id1)
    self.client.delete_agent(self.agent_id2)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id1)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id2)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_add_operations_bulk_with_correct_input(self):
    """add_operations_bulk should succeed when given correct input data

    It should give a proper JSON response with a list containing dicts with
    a 'message' fields being a string and no 'error' field.
    """
    payload = [{"id": self.agent_id1, "operations": valid_data.VALID_OPERATIONS_SET},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[0].keys())
    self.assertTrue("message" in resp[1].keys())
    self.assertFalse("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_with_many_operations(self):
    """add_operations_bulk should succeed when given correct input data

    It should give a proper JSON response with a list containing dicts with
    a `message` fields being a string and no 'error' field.
    """
    operations = valid_data.VALID_OPERATIONS_SET[:]
    operation = operations[-1]
    timestamp = operation["timestamp"]
    length = len(operations)

    while length < 2000:
      operation["timestamp"] = timestamp + length
      operations.append(operation.copy())
      length = length + 1

    payload = [{"id": self.agent_id1,
                "operations": sorted(operations, key=lambda operation: operation["timestamp"])},
              {"id": self.agent_id2,
                "operations": sorted(operations, key=lambda operation: operation["timestamp"])}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[0].keys())
    self.assertTrue("message" in resp[1].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

class TestAddOperationsBulkFailure(unittest.TestCase):
  """Checks that the client fail when adding operations to
  multiple agent(s) with incorrect input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID_TWO  + "_" + settings.RUN_ID

  def setUp(self):
    self.client.delete_agent(self.agent_id1)
    self.client.delete_agent(self.agent_id2)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id1)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id2)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  @nottest
  def test_add_operations_bulk_with_invalid_agent_id(self):
    """add_operations_bulk should fail when given non-string/empty strings ID

    It should raise an error upon request for operations posting
    for all agents with an ID that is not of type string, since agent IDs
    should always be strings.
    """
    for empty_id in invalid_data.UNDEFINED_KEY:
      payload = [{"id": invalid_data.UNDEFINED_KEY[empty_id], "operations": valid_data.VALID_OPERATIONS_SET},
                 {"id": invalid_data.UNDEFINED_KEY[empty_id], "operations": valid_data.VALID_OPERATIONS_SET}]
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.add_operations_bulk,
        payload)
      
      self.addCleanup(self.clean_up_agents,
                      [self.agent_id1, self.agent_id2])

  @nottest
  def test_add_operations_bulk_empty_operations_set(self):
    """add_operations_bulk should fail when given empty sets of operations

    It should raise an error upon request for posting an empty set of
    operations to all agent's configuration.
    """
    for ops_set in invalid_data.UNDEFINED_KEY:
      payload = [{"id": self.agent_id1, "operations": invalid_data.UNDEFINED_KEY[ops_set]},
                 {"id": self.agent_id2, "operations": invalid_data.UNDEFINED_KEY[ops_set]}]
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.add_operations_bulk,
        payload)
      self.addCleanup(self.clean_up_agents,
                      [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_invalid_operations(self):
    """add_operations_bulk should fail when given invalid sets of operations

    It should raise an error upon request for posting an invalid set of
    operations to all agent's configuration.
    """
    for ops_set in invalid_data.INVALID_OPS_SET:
      payload = [{"id": self.agent_id1, "operations": invalid_data.INVALID_OPS_SET[ops_set]},
                 {"id": self.agent_id2, "operations": invalid_data.INVALID_OPS_SET[ops_set]}]
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.add_operations_bulk,
        payload)
      self.addCleanup(self.clean_up_agents,
                      [self.agent_id1, self.agent_id2])


class TestAddOperationsBulkSomeFailure(unittest.TestCase):
  """Checks that the client succeed when adding operations to
  an/multiple agent(s) with bad input and an/multiple agent(s)
  with valid input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID_TWO  + "_" + settings.RUN_ID

  def setUp(self):
    self.client.delete_agent(self.agent_id1)
    self.client.delete_agent(self.agent_id2)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id1)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id2)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_add_operations_bulk_some_none_agent_id(self):
    """add_operations_bulk should succeed when given some invalid agent id and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    empty_id = invalid_data.UNDEFINED_KEY["none"]
    payload = [{"id": empty_id, "operations": valid_data.VALID_OPERATIONS_SET},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_empty_string_id(self):
    """add_operations_bulk should succeed when given some invalid agent id and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    empty_id = invalid_data.UNDEFINED_KEY["empty_string"]
    payload = [{"id": empty_id, "operations": valid_data.VALID_OPERATIONS_SET},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_empty_dict_id(self):
    """add_operations_bulk should succeed when given some invalid agent id and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    empty_id = invalid_data.UNDEFINED_KEY["empty_dict"]
    payload = [{"id": empty_id, "operations": valid_data.VALID_OPERATIONS_SET},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_empty_list_id(self):
    """add_operations_bulk should succeed when given some invalid agent id and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    empty_id = invalid_data.UNDEFINED_KEY["empty_list"]
    payload = [{"id": empty_id, "operations": valid_data.VALID_OPERATIONS_SET},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_none_operations(self):
    """add_operations_bulk should succeed when given some non operations set
    and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    ops_set = invalid_data.UNDEFINED_KEY["none"]
    payload = [{"id": self.agent_id1, "operations": ops_set},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_empty_string_operations(self):
    """add_operations_bulk should succeed when given some empty string operations set
    and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    ops_set = invalid_data.UNDEFINED_KEY["empty_string"]
    payload = [{"id": self.agent_id1, "operations": ops_set},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_empty_dict_operations(self):
    """add_operations_bulk should succeed when given some empty dict operations set
    and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    ops_set = invalid_data.UNDEFINED_KEY["empty_dict"]
    payload = [{"id": self.agent_id1, "operations": ops_set},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_empty_list_operations(self):
    """add_operations_bulk should succeed when given some empty list operations set
    and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    ops_set = invalid_data.UNDEFINED_KEY["empty_list"]
    payload = [{"id": self.agent_id1, "operations": ops_set},
              {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_incomplete_operations(self):
    """add_operations_bulk should succeed when given some incomplete operations set
    and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    ops_set = invalid_data.INVALID_OPS_SET["incomplete_first_op"]
    payload = [{"id": self.agent_id1, "operations": ops_set},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_invalid_operations(self):
    """add_operations_bulk should succeed when given some invalid operations set
    and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    ops_set = invalid_data.INVALID_OPS_SET["invalid_operation"]
    payload = [{"id": self.agent_id1, "operations": ops_set},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_unexpected_time_operations(self):
    """add_operations_bulk should succeed when given some unexpected time operations set
    and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    ops_set = invalid_data.INVALID_OPS_SET["unexpected_time_property"]
    payload = [{"id": self.agent_id1, "operations": ops_set},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_some_dict_operations(self):
    """add_operations_bulk should succeed when given some dict operations set
    and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have an 'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `message` fields being strings and no
    'error' field.
    """
    ops_set = invalid_data.INVALID_OPS_SET["dict_operations"]
    payload = [{"id": self.agent_id1, "operations": ops_set},
               {"id": self.agent_id2, "operations": valid_data.VALID_OPERATIONS_SET}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("message" in resp[1].keys())
    self.assertTrue("error" in resp[0].keys())
    self.assertFalse("error" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])
