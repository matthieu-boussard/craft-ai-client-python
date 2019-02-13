import unittest
import six

from nose.tools import nottest
from craftai import Client, errors as craft_err

from . import settings
from .data import valid_data
from .data import invalid_data

class TestCreateBulkAgentsSuccess(unittest.TestCase):
  """Checks that the client succeeds when creating an agent with OK input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID  + "_" + settings.RUN_ID

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    resp1 = self.client.delete_agent(self.agent_id1)
    resp2 = self.client.delete_agent(self.agent_id2)

    self.assertIsInstance(resp1, dict)
    self.assertIsInstance(resp2, dict)

    resp_keys1 = resp1.keys()
    resp_keys2 = resp2.keys()

    self.assertTrue("message" in resp_keys1)
    self.assertTrue("message" in resp_keys2)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_create_one_agent_generated_agent_id(self):
    """create_bulk_agents should succeed when given an empty `id` field.

    It should give a proper JSON response with a list containing a dict
    with `id` and `configuration` fields being strings.
    """
    payload = [{"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_bulk_agents(payload)

    self.assertIsInstance(resp[0].get("id"), six.string_types)
    self.addCleanup(self.clean_up_agent, resp[0].get("id"))

  def test_create_multiple_agents_generated_agent_id(self):
    """create_bulk_agents should succeed when given two agents to
    create with empty `id` field.

    It should give a proper JSON response with a list containing two dicts
    with `id` and `configuration` fields being strings.
    """
    payload = [{"configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_bulk_agents(payload)

    self.assertIsInstance(resp[0].get("id"), six.string_types)
    self.assertIsInstance(resp[1].get("id"), six.string_types)
    self.addCleanup(self.clean_up_agents, [resp[0].get("id"), resp[1].get("id")])

  def test_create_one_agent_given_agent_id(self):
    """create_bulk_agents should succeed when given a string ID

    It should give a proper JSON response with a list containing a dict
    with `id` and `configuration` fields being strings and `id` being
    the same as the one given as a parameter.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_bulk_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.addCleanup(self.clean_up_agent, self.agent_id1)

  def test_create_multiple_agents_given_agent_id(self):
    """create_bulk_agents should succeed to create two agents when
    given two string ID.

    It should give a proper JSON response with a list containing two dicts
    with `id` and `configuration` fields being strings and the `id`s being
    the same as the one given as parameters.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"id": self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_bulk_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.addCleanup(self.clean_up_agents, [resp[0].get("id"), resp[1].get("id")])

  def test_create_agent_one_id_given_one_generated(self):
    """create_bulk_agents should succeed when given a string ID.

    It should give a proper JSON response with a list containing two dicts
    with `id` and `configuration` fields being strings and the first `id` being the
    same as the one given as a parameter.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_bulk_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[1].get("id"), six.string_types)
    self.addCleanup(self.clean_up_agents, [resp[0].get("id"), resp[1].get("id")])


class TestCreateBulkAgentsFailure(unittest.TestCase):
  """Checks that the client fails when creating an agent with bad input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID  + "_" + settings.RUN_ID

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    resp1 = self.client.delete_agent(self.agent_id1)
    resp2 = self.client.delete_agent(self.agent_id2)

    self.assertIsInstance(resp1, dict)
    self.assertIsInstance(resp2, dict)

    resp_keys1 = resp1.keys()
    resp_keys2 = resp2.keys()

    self.assertTrue("message" in resp_keys1)
    self.assertTrue("message" in resp_keys2)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_create_all_agent_with_existing_agent_id(self):
    """create_bulk_agent should fail when given only IDs that already exist.

    It should raise an error upon request for creation of a bulk of agents
    with IDs that already exist, since agent IDs should always be unique.
    """
    # Calling create_bulk_agents a first time
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"id": self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION}]
    self.client.create_bulk_agents(payload)

    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.create_bulk_agents,
      payload
    )
    self.addCleanup(self.clean_up_agents, [self.agent_id1, self.agent_id2])

  def test_create_all_agents_with_invalid_agent_id(self):
    """create_bulk_agents should fail whith all agent id invalid.

    It should raise an error upon request for creation of
    multiple agents with invalid id.
    """
    payload = [{"id": "toto/tutu", "configuration": valid_data.VALID_CONFIGURATION},
               {"id": "toto@tata", "configuration": valid_data.VALID_CONFIGURATION}]
    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.create_bulk_agents,
      payload
    )

  @nottest
  def test_create_all_agents_with_invalid_context(self):
    """create_bulk_agents should fail whith all agent context invalid.

    It should raise an error upon request for creation of
    multiple agents with invalid context.
    """
    for inv_context in invalid_data.INVALID_CONTEXTS:
      configuration = {
        "context": invalid_data.INVALID_CONTEXTS[inv_context],
        "output": ["lightbulbColor"],
        "time_quantum": 100
      }
      payload = [{"id": self.agent_id1, "configuration": configuration},
                 {"id": self.agent_id2, "configuration": configuration}]

      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.create_bulk_agents,
        payload
      )


class TestCreateBulkAgentsSomeFailure(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID  + "_" + settings.RUN_ID

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    resp1 = self.client.delete_agent(self.agent_id1)
    resp2 = self.client.delete_agent(self.agent_id2)

    self.assertIsInstance(resp1, dict)
    self.assertIsInstance(resp2, dict)

    resp_keys1 = resp1.keys()
    resp_keys2 = resp2.keys()

    self.assertTrue("message" in resp_keys1)
    self.assertTrue("message" in resp_keys2)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_create_some_agents_with_existing_agent_id(self):
    """create_bulk_agent should succeed when some of
    the ID given already exist and the others doesn't.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiCredentialsError (error 401).
    The second one should have `id` and `configuration` fields being strings.
    """
    # Calling create_bulk_agents a first time
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp1 = self.client.create_bulk_agents(payload)
    resp2 = self.client.create_bulk_agents(payload)

    self.assertEqual(resp2[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp2[0].get("error"), craft_err.CraftAiCredentialsError)
    self.assertFalse("configuration" in resp2[0])
    self.assertIsInstance(resp1[1].get("id"), six.string_types)
    self.assertTrue("configuration" in resp1[1])
    self.assertIsInstance(resp2[1].get("id"), six.string_types)
    self.assertTrue("configuration" in resp2[1])

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, resp1[1].get("id"), resp2[1].get("id")])

  def test_create_some_agents_with_invalid_agent_id(self):
    """create_bulk_agent should succeed when some of
    the ID given are invalid and the others doesn't.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiBadRequestError.
    The second one with `id` and `configuration` fields being strings.
    """
    payload = [{"id": "toto/tutu", "configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_bulk_agents(payload)

    self.assertEqual(resp[0].get("id"), "toto/tutu")
    self.assertIsInstance(resp[0].get("error"), craft_err.CraftAiBadRequestError)
    self.assertFalse("configuration" in resp[0])
    self.assertIsInstance(resp[1].get("id"), six.string_types)
    self.assertTrue("configuration" in resp[1])

    self.addCleanup(self.clean_up_agent, resp[1].get("id"))
