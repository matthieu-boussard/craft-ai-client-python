import unittest
import six

from craftai import Client, errors as craft_err

from . import settings
from .data import valid_data
from .data import invalid_data

NB_AGENTS_TO_CREATE = 100

class TestCreateAgentsBulkSuccess(unittest.TestCase):
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
    """create_agents_bulk should succeed when given an empty `id` field.

    It should give a proper JSON response with a list containing a dict
    with `id` and `configuration` fields being strings.
    """
    payload = [{"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents_bulk(payload)

    self.assertIsInstance(resp[0].get("id"), six.string_types)

    self.addCleanup(self.clean_up_agent, resp[0].get("id"))

  def test_create_multiple_agents_generated_agent_id(self):
    """create_agents_bulk should succeed when given agents to create with empty `id` field.

    It should give a proper JSON response with a list containing two dicts
    with `id` and `configuration` fields being strings.
    """
    payload = [{"configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents_bulk(payload)

    self.assertIsInstance(resp[0].get("id"), six.string_types)
    self.assertIsInstance(resp[1].get("id"), six.string_types)
    self.addCleanup(self.clean_up_agents, [resp[0].get("id"), resp[1].get("id")])

  def test_create_one_agent_given_agent_id(self):
    """create_agents_bulk should succeed when given a string ID

    It should give a proper JSON response with a list containing a dict
    with `id` and `configuration` fields being strings and `id` being
    the same as the one given as a parameter.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents_bulk(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.addCleanup(self.clean_up_agent, self.agent_id1)

  def test_create_multiple_agents_given_agent_id(self):
    """create_agents_bulk should succeed to create agents when given their string ID.

    It should give a proper JSON response with a list containing two dicts
    with `id` and `configuration` fields being strings and the `id`s being
    the same as the one given as parameters.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"id": self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents_bulk(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.addCleanup(self.clean_up_agents, [resp[0].get("id"), resp[1].get("id")])

  def test_create_agents_bulk_id_given_and_generated(self):
    """create_agents_bulk should succeed when given some agents with string ID and some
    with empty `id` field.

    It should give a proper JSON response with a list containing two dicts
    with `id` and `configuration` fields being strings and the first `id` being the
    same as the one given as a parameter.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents_bulk(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertIsInstance(resp[1].get("id"), six.string_types)
    self.addCleanup(self.clean_up_agents, [resp[0].get("id"), resp[1].get("id")])


  def test_create_lot_of_agents_bulk(self):
    """create_agents_bulk should succeed when given a lot of agents to create.

    It should give a proper JSON response with a list containing dicts
    with `id` and `configuration` fields being strings and the first `id` being the
    same as the one given as a parameter.
    """
    payload = []
    agents_lst = []
    for i in range(NB_AGENTS_TO_CREATE):
      new_agent_id = valid_data.VALID_ID_TEMPLATE + str(i)  + "_" + settings.RUN_ID
      self.client.delete_agent(new_agent_id)
      payload.append({"id": new_agent_id, "configuration": valid_data.VALID_CONFIGURATION})
      agents_lst.append(new_agent_id)

    resp = self.client.create_agents_bulk(payload)

    for i in range(len(resp)):
      self.assertEqual(resp[i].get("id"), agents_lst[i])
      self.assertFalse("error" in resp[i])

    self.addCleanup(self.clean_up_agents,
                    agents_lst)

class TestCreateAgentsBulkFailure(unittest.TestCase):
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

  def test_create_agents_bulk_with_existing_agent_id(self):
    """create_agent should fail when given only IDs that already exist.

    It should raise an error upon request for creation of a bulk of agents
    with IDs that already exist, since agent IDs should always be unique.
    """
    # Calling create_agents_bulk a first time
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"id": self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION}]
    self.client.create_agents_bulk(payload)

    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.create_agents_bulk,
      payload
    )
    self.addCleanup(self.clean_up_agents, [self.agent_id1, self.agent_id2])

  def test_create_agents_bulk_with_invalid_agent_id(self):
    """create_agents_bulk should fail with all agents id are invalid or if the id field
    doesn't exist.

    It should raise an error upon request for creation of all agents with invalid id.
    """
    payload = [{"id": "toto/tutu", "configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.create_agents_bulk,
      payload
    )

  def test_create_agents_bulk_with_invalid_context(self):
    """create_agents_bulk should fail with all agents context invalid.

    It should raise an error upon request for creation of all agents with invalid context.
    """
    payload = []
    agents_lst = []
    i = 0
    # Add all the invalid context to check
    for invalid_context in invalid_data.INVALID_CONTEXTS:
      new_agent_id = valid_data.VALID_ID_TEMPLATE + str(i)  + "_" + settings.RUN_ID
      invalid_configuration = {
        "context": invalid_data.INVALID_CONTEXTS[invalid_context],
        "output": ["lightbulbColor"],
        "time_quantum": 100
      }
      self.client.delete_agent(new_agent_id)

      payload.append({"id": new_agent_id, "configuration": invalid_configuration})
      agents_lst.append(new_agent_id)
      i += 1

    # Add an agent with no context field
    new_agent_id = valid_data.VALID_ID_TEMPLATE + str(i)  + "_" + settings.RUN_ID
    self.client.delete_agent(new_agent_id)
    invalid_configuration = {
        "output": ["lightbulbColor"],
        "time_quantum": 100
      }
    payload.append({"id": new_agent_id, "configuration": invalid_configuration})
    agents_lst.append(new_agent_id)

    self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.create_agents_bulk,
        payload
      )

    self.addCleanup(self.clean_up_agents,
                    agents_lst)

  def test_create_agents_bulk_undefined_config(self):
    """create_agents_bulk should fail when no configuration key is given for all
    agents.

    It should raise an error upon request for creation of all agents with
    no configuration key in the request body, since it is a mandatory field to
    create an agent.
    """
    payload = []
    agents_lst = []
    i = 0
    # Add all the invalid context to check
    for empty_configuration in invalid_data.UNDEFINED_KEY:
      new_agent_id = valid_data.VALID_ID_TEMPLATE + str(i)  + "_" + settings.RUN_ID
      self.client.delete_agent(new_agent_id)

      payload.append({"id": new_agent_id,
                      "configuration": invalid_data.UNDEFINED_KEY[empty_configuration]})
      agents_lst.append(new_agent_id)
      i += 1

    # Add agent with no configuration
    new_agent_id = valid_data.VALID_ID_TEMPLATE + str(i)  + "_" + settings.RUN_ID
    self.client.delete_agent(new_agent_id)
    payload.append({"id": new_agent_id})
    agents_lst.append(new_agent_id)

    self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.create_agents_bulk,
        payload
      )

    self.addCleanup(self.clean_up_agents,
                    agents_lst)

  def test_create_agents_bulk_invalid_time_quantum(self):
    """create_agents_bulk should fail when given invalid time quantums

    It should raise an error upon request for creation of all agent with
    incorrect time quantum in the configuration, since it is essential to
    perform any action with craft ai.
    """
    payload = []
    agents_lst = []
    i = 0
    for inv_tq in invalid_data.INVALID_TIME_QUANTA:
      new_agent_id = valid_data.VALID_ID_TEMPLATE + str(i)  + "_" + settings.RUN_ID
      invalid_configuration = {
        "context": valid_data.VALID_CONTEXT,
        "output": valid_data.VALID_OUTPUT,
        "time_quantum": invalid_data.INVALID_TIME_QUANTA[inv_tq]
      }
      self.client.delete_agent(new_agent_id)

      payload.append({"id": new_agent_id,
                      "configuration": invalid_configuration})
      agents_lst.append(new_agent_id)
      i += 1

    # Add an agent with no time quantum field
    new_agent_id = valid_data.VALID_ID_TEMPLATE + str(i)  + "_" + settings.RUN_ID
    self.client.delete_agent(new_agent_id)
    invalid_configuration = {
        "context": valid_data.VALID_CONTEXT,
        "output": ["lightbulbColor"]
      }
    payload.append({"id": new_agent_id, "configuration": invalid_configuration})
    agents_lst.append(new_agent_id)

    self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.create_agents_bulk,
        payload
      )

    self.addCleanup(self.clean_up_agents,
                    agents_lst)


class TestCreateAgentsBulkSomeFailure(unittest.TestCase):
  """Checks that the client succeed when creating an/multiple agent(s)
  with bad input and an/multiple agent(s) with valid input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    resp1 = self.client.delete_agent(self.agent_id1)
    self.assertIsInstance(resp1, dict)

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
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"configuration": valid_data.VALID_CONFIGURATION}]
    resp1 = self.client.create_agents_bulk(payload)
    resp2 = self.client.create_agents_bulk(payload)

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
               {"id": "tata@tutu", "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents_bulk(payload)

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
    # Calling create_agents_bulk a first time
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
               {"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION}]
    resp = self.client.create_agents_bulk(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id1)
    self.assertTrue("configuration" in resp[0])
    self.assertIsInstance(resp[1].get("error"), craft_err.CraftAiBadRequestError)

    self.addCleanup(self.clean_up_agent,
                    self.agent_id1)

  def test_create_some_agents_bulk_with_invalid_context(self):
    """create_agents_bulk should succeed with some agents with invalid context
    and some with valid context.

    It should give a proper JSON response with a list containing dicts.
    The valid ones should have `id` and `configuration` fields being strings.
    The invalid ones should have 'id' and 'error' fields.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION}]
    agents_lst = [self.agent_id1]
    i = 0
    for invalid_context in invalid_data.INVALID_CONTEXTS:
      new_agent_id = valid_data.VALID_ID_TEMPLATE + str(i)  + "_" + settings.RUN_ID
      invalid_configuration = {
        "context": invalid_data.INVALID_CONTEXTS[invalid_context],
        "output": ["lightbulbColor"],
        "time_quantum": 100
      }
      self.client.delete_agent(new_agent_id)

      payload.append({"id": new_agent_id, "configuration": invalid_configuration})
      agents_lst.append(new_agent_id)
      i += 1

    resp = self.client.create_agents_bulk(payload)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertTrue("configuration" in resp[0])
    self.assertFalse("error" in resp[0])

    for i in range(1, len(resp)):
      self.assertEqual(resp[i].get("id"), agents_lst[i])
      self.assertTrue("error" in resp[i])
      self.assertFalse("configuration" in resp[i])

    self.addCleanup(self.clean_up_agents,
                    agents_lst)

  def test_create_some_agents_bulk_with_undefined_configuration(self):
    """create_agents_bulk should succeed with some agents with invalid configuration
    and some with valid configuration.

    It should give a proper JSON response with a list containing dicts.
    The valid ones should have `id` and `configuration` fields being strings.
    The invalid ones should have 'id' and 'error' fields.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION}]
    agents_lst = [self.agent_id1]
    i = 0
    for empty_configuration in invalid_data.UNDEFINED_KEY:
      new_agent_id = valid_data.VALID_ID_TEMPLATE + str(i)  + "_" + settings.RUN_ID
      self.client.delete_agent(new_agent_id)

      payload.append({"id": new_agent_id,
                      "configuration": invalid_data.UNDEFINED_KEY[empty_configuration]})
      agents_lst.append(new_agent_id)
      i += 1

    resp = self.client.create_agents_bulk(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertTrue("configuration" in resp[0])
    self.assertFalse("error" in resp[0])

    for i in range(1, len(resp)):
      self.assertEqual(resp[i].get("id"), agents_lst[i])
      self.assertTrue("error" in resp[i])
      self.assertFalse("configuration" in resp[i])

    self.addCleanup(self.clean_up_agents,
                    agents_lst)

  def test_create_some_agents_bulk_with_invalid_time_quantum(self):
    """create_agents_bulk should succeed with some agents with invalid time quantum
    in the configuration and some with valid configuration.

    It should give a proper JSON response with a list containing dicts.
    The valid ones should have `id` and `configuration` fields being strings.
    The invalid ones should have 'id' and 'error' fields.
    """
    payload = [{"id": self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION}]
    agents_lst = [self.agent_id1]
    i = 0
    for inv_tq in invalid_data.INVALID_TIME_QUANTA:
      new_agent_id = valid_data.VALID_ID_TEMPLATE + str(i)  + "_" + settings.RUN_ID
      invalid_configuration = {
        "context": valid_data.VALID_CONTEXT,
        "output": valid_data.VALID_OUTPUT,
        "time_quantum": invalid_data.INVALID_TIME_QUANTA[inv_tq]
      }
      self.client.delete_agent(new_agent_id)

      payload.append({"id": new_agent_id,
                      "configuration": invalid_configuration})
      agents_lst.append(new_agent_id)
      i += 1

    resp = self.client.create_agents_bulk(payload)

    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertTrue("configuration" in resp[0])
    self.assertFalse("error" in resp[0])

    for i in range(1, len(resp)):
      self.assertEqual(resp[i].get("id"), agents_lst[i])
      self.assertTrue("error" in resp[i])
      self.assertIsInstance(resp[i].get("error"), craft_err.CraftAiBadRequestError)
      self.assertFalse("configuration" in resp[i])

    self.addCleanup(self.clean_up_agents,
                    agents_lst)
