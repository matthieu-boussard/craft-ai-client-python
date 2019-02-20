import unittest
import six

from craftai import Client, errors as craft_err

from . import settings
from .data import valid_data
from .data import invalid_data

class TestCreateAgentsSuccess(unittest.TestCase):
  """Checks that the client succeeds when creating
  an/multiple agent(s) with OK input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID_TWO  + "_" + settings.RUN_ID

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    resp1 = self.client.delete_agent(self.agent_id1)
    resp2 = self.client.delete_agent(self.agent_id2)

    self.assertIsInstance(resp1, dict)
    self.assertIsInstance(resp2, dict)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_create_one_agent_generated_agent_id(self):
    """create_agents should succeed when given an empty `id` field.

    It should give a proper JSON response with a list containing a dict
    with `id` and `configuration` fields being strings.
    """
    payload = [{"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertIsInstance(resp[0].get("id"), six.string_types)

    self.addCleanup(self.clean_up_agent, resp[0].get("id"))

  def test_create_multiple_agents_generated_agent_id(self):
    """create_agents should succeed when given agents to create with empty `id` field.

    It should give a proper JSON response with a list containing two dicts
    with `id` and `configuration` fields being strings.
    """
    payload = [{"configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertIsInstance(resp[0].get("id"), six.string_types)
    self.assertIsInstance(resp[1].get("id"), six.string_types)
    self.addCleanup(self.clean_up_agents, [resp[0].get("id"), resp[1].get("id")])

  def test_create_one_agent_given_agent_id(self):
    """create_agents should succeed when given a string ID

    It should give a proper JSON response with a list containing a dict
    with `id` and `configuration` fields being strings and `id` being
    the same as the one given as a parameter.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.addCleanup(self.clean_up_agent, self.agent_id1)

  def test_create_multiple_agents_given_agent_id(self):
    """create_agents should succeed to create agents when given their string ID.

    It should give a proper JSON response with a list containing two dicts
    with `id` and `configuration` fields being strings and the `id`s being
    the same as the one given as parameters.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"id": self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.addCleanup(self.clean_up_agents, [resp[0].get("id"), resp[1].get("id")])

  def test_create_agents_one_id_given_one_generated(self):
    """create_agents should succeed when given some agents with string ID and some
    with empty `id` field.

    It should give a proper JSON response with a list containing two dicts
    with `id` and `configuration` fields being strings and the first `id` being the
    same as the one given as a parameter.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[1].get("id"), six.string_types)
    self.addCleanup(self.clean_up_agents, [resp[0].get("id"), resp[1].get("id")])


class TestCreateAgentsFailure(unittest.TestCase):
  """Checks that the client fails when creating
  an/multiple agent(s) with bad input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID_TWO  + "_" + settings.RUN_ID

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    resp1 = self.client.delete_agent(self.agent_id1)
    resp2 = self.client.delete_agent(self.agent_id2)

    self.assertIsInstance(resp1, dict)
    self.assertIsInstance(resp2, dict)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_create_agents_with_existing_agent_id(self):
    """create_agent should fail when given only IDs that already exist.

    It should raise an error upon request for creation of a bulk of agents
    with IDs that already exist, since agent IDs should always be unique.
    """
    # Calling create_agents a first time
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"id": self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION}]
    self.client.create_agents(payload)

    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.create_agents,
      payload
    )
    self.addCleanup(self.clean_up_agents, [self.agent_id1, self.agent_id2])

  def test_create_agents_with_invalid_agent_id(self):
    """create_agents should fail with all agents id are invalid.

    It should raise an error upon request for creation of all agents with invalid id.
    """
    payload = [{"id": "toto/tutu", "configuration": valid_data.VALID_CONFIGURATION},
               {"id": "toto@tata", "configuration": valid_data.VALID_CONFIGURATION}]
    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.create_agents,
      payload
    )

  def test_create_agents_with_invalid_context(self):
    """create_agents should fail with all agents context invalid.

    It should raise an error upon request for creation of all agents with invalid context.
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
        self.client.create_agents,
        payload
      )

  def test_create_agents_undefined_configuration(self):
    """create_agents should fail when no configuration key is given for all
    agents.

    It should raise an error upon request for creation of all agents with
    no configuration key in the request body, since it is a mandatory field to
    create an agent.
    """
    # Testing all non dict configuration cases
    for empty_configuration in invalid_data.UNDEFINED_KEY:
      payload = [{"id": self.agent_id1,
                  "configuration": invalid_data.UNDEFINED_KEY[empty_configuration]},
                 {"id": self.agent_id2,
                  "configuration": invalid_data.UNDEFINED_KEY[empty_configuration]}]
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.create_agents,
        payload)
      self.addCleanup(
        self.clean_up_agents,
        [self.agent_id1, self.agent_id2]
      )

  def test_create_agents_invalid_time_quantum(self):
    """create_agents should fail when given invalid time quantums

    It should raise an error upon request for creation of all agent with
    incorrect time quantum in the configuration, since it is essential to
    perform any action with craft ai.
    """
    for inv_tq in invalid_data.INVALID_TIME_QUANTA:
      configuration = {
        "context": valid_data.VALID_CONTEXT,
        "output": valid_data.VALID_OUTPUT,
        "time_quantum": invalid_data.INVALID_TIME_QUANTA[inv_tq]
      }
      payload = [{"id": self.agent_id1, "configuration": configuration},
                 {"id": self.agent_id2, "configuration": configuration}]
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.create_agents,
        payload)
      self.addCleanup(
        self.clean_up_agents,
        [self.agent_id1, self.agent_id2])


class TestCreateAgentsSomeFailure(unittest.TestCase):
  """Checks that the client succeed when creating an/multiple agent(s)
  with bad input and an/multiple agent(s) with valid input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID_TWO  + "_" + settings.RUN_ID

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    resp1 = self.client.delete_agent(self.agent_id1)
    resp2 = self.client.delete_agent(self.agent_id2)

    self.assertIsInstance(resp1, dict)
    self.assertIsInstance(resp2, dict)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_create_some_agents_with_existing_agent_id(self):
    """create_agent should succeed when some of the ID given already exist
    and the others doesn't.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiBadRequestError.
    The second one should have `id` and `configuration` fields being strings.
    """
    # Calling create_agents a first time
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp1 = self.client.create_agents(payload)
    resp2 = self.client.create_agents(payload)

    self.assertEqual(resp2[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp2[0].get("error"), craft_err.CraftAiBadRequestError)
    self.assertFalse("configuration" in resp2[0])
    self.assertIsInstance(resp1[1].get("id"), six.string_types)
    self.assertTrue("configuration" in resp1[1])
    self.assertIsInstance(resp2[1].get("id"), six.string_types)
    self.assertTrue("configuration" in resp2[1])

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, resp1[1].get("id"), resp2[1].get("id")])

  def test_create_some_agents_with_invalid_agent_id(self):
    """create_agent should succeed when some of the ID given are invalid
    and the others doesn't.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiBadRequestError.
    The second one with `id` and `configuration` fields being strings.
    """
    payload = [{"id": "toto/tutu", "configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), "toto/tutu")
    self.assertIsInstance(resp[0].get("error"), craft_err.CraftAiBadRequestError)
    self.assertFalse("configuration" in resp[0])
    self.assertIsInstance(resp[1].get("id"), six.string_types)
    self.assertTrue("configuration" in resp[1])

    self.addCleanup(self.clean_up_agent, resp[1].get("id"))

  def test_create_same_agents_in_bulk(self):
    """create_agent should succeed when agents in a bulk have the same id given.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    and the `configuration` field being strings.
    The second one should have `id` being the same as the one given as a parameter
    'error' field being a CraftAiBadRequestError.
    """
    # Calling create_agents a first time
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id1)
    self.assertTrue("configuration" in resp[0])
    self.assertIsInstance(resp[1].get("error"), craft_err.CraftAiBadRequestError)

    self.addCleanup(self.clean_up_agent,
                    self.agent_id1)

  def test_create_some_agents_unserialisable_context(self):
    """create_agents should succeed with some agents with unserialisable context
    and some with valid context.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a TypeError.
    The second one with `id` and `configuration` fields being strings.
    """
    configuration = {
      "context": invalid_data.INVALID_CONTEXTS["invalid_context_nonjsonserializable"],
      "output": ["lightbulbColor"],
      "time_quantum": 100
    }
    payload = [{"id": self.agent_id1,
                "configuration": configuration},
               {"id": self.agent_id2,
                "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[0].get("error"), TypeError)
    self.assertFalse("configuration" in resp[0])
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("configuration" in resp[1])
    self.assertFalse("error" in resp[1])
    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_create_some_agents_with_missing_context(self):
    """create_agents should succeed with some agents with missing context
    and some with valid context.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiBadRequestError.
    The second one with `id` and `configuration` fields being strings.
    """
    configuration = {
      "context": invalid_data.INVALID_CONTEXTS["invalid_context_missing_type_key"],
      "output": ["lightbulbColor"],
      "time_quantum": 100
    }
    payload = [{"id": self.agent_id1,
                "configuration": configuration},
               {"id": self.agent_id2,
                "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[0].get("error"), craft_err.CraftAiBadRequestError)
    self.assertFalse("configuration" in resp[0])
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("configuration" in resp[1])
    self.assertFalse("error" in resp[1])
    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_create_some_agents_config_none(self):
    """create_agents should succed when given some agents with no configuration key
    and some agent with valid configuration.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiBadRequestError.
    The second one with `id` and `configuration` fields being strings.
    """
    payload = [{"id": self.agent_id1, "configuration": invalid_data.UNDEFINED_KEY["none"]},
               {"id": self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[0].get("error"), craft_err.CraftAiBadRequestError)
    self.assertFalse("configuration" in resp[0])
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("configuration" in resp[1])
    self.assertFalse("error" in resp[1])

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_create_some_agents_config_empty_string(self):
    """create_agents should succed when given some agents with no configuration key
    and some agent with valid configuration in the request body.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiBadRequestError.
    The second one with `id` and `configuration` fields being strings.
    """
    payload = [{"id": self.agent_id1, "configuration": invalid_data.UNDEFINED_KEY["empty_string"]},
               {"id": self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[0].get("error"), craft_err.CraftAiBadRequestError)
    self.assertFalse("configuration" in resp[0])
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("configuration" in resp[1])
    self.assertFalse("error" in resp[1])

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_create_some_agents_config_empty_dict(self):
    """create_agents should succed when given some agents with no configuration key
    and some agent with valid configuration in the request body.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiBadRequestError.
    The second one with `id` and `configuration` fields being strings.
    """
    payload = [{"id": self.agent_id1, "configuration": invalid_data.UNDEFINED_KEY["empty_dict"]},
               {"id": self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[0].get("error"), craft_err.CraftAiBadRequestError)
    self.assertFalse("configuration" in resp[0])
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("configuration" in resp[1])
    self.assertFalse("error" in resp[1])

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_create_some_agents_config_empty_list(self):
    """create_agents should succed when given some agents with no configuration key
    and some agent with valid configuration in the request body.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiBadRequestError.
    The second one with `id` and `configuration` fields being strings.
    """
    payload = [{"id": self.agent_id1, "configuration": invalid_data.UNDEFINED_KEY["empty_list"]},
               {"id": self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[0].get("error"), craft_err.CraftAiBadRequestError)
    self.assertFalse("configuration" in resp[0])
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("configuration" in resp[1])
    self.assertFalse("error" in resp[1])

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_create_some_agents_negative_time_quantum(self):
    """create_agents should succed when given some negative time quantum and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiBadRequestError.
    The second one with `id` and `configuration` fields being strings.
    """
    configuration = {
      "context": valid_data.VALID_CONTEXT,
      "output": valid_data.VALID_OUTPUT,
      "time_quantum": invalid_data.INVALID_TIME_QUANTA["negative_tq"]
    }
    payload = [{"id": self.agent_id1,
                "configuration": configuration},
               {"id": self.agent_id2,
                "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[0].get("error"), craft_err.CraftAiBadRequestError)
    self.assertFalse("configuration" in resp[0])
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("configuration" in resp[1])
    self.assertFalse("error" in resp[1])

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_create_some_agents_null_time_quantum(self):
    """create_agents should succed when given some null time quantum and some valid.

    It should give a proper JSON response with a list containing two dicts.
    The first one should have 'id' being the same as the one given as a parameter,
    'error' field being a CraftAiBadRequestError.
    The second one with `id` and `configuration` fields being strings.
    """
    configuration = {
      "context": valid_data.VALID_CONTEXT,
      "output": valid_data.VALID_OUTPUT,
      "time_quantum": invalid_data.INVALID_TIME_QUANTA["null_tq"]
    }
    payload = [{"id": self.agent_id1,
                "configuration": configuration},
               {"id": self.agent_id2,
                "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[0].get("error"), craft_err.CraftAiBadRequestError)
    self.assertFalse("configuration" in resp[0])
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertTrue("configuration" in resp[1])
    self.assertFalse("error" in resp[1])

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])
