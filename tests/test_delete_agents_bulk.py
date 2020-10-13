import unittest

from craft_ai import Client, errors as craft_err

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data

NB_AGENTS_TO_DELETE = 200


class TestDeleteAgentsBulkSuccess(unittest.TestCase):
    """Checks that the client succeeds when deleting
    an/multiple agent(s) with OK input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id1 = generate_entity_id("test_delete_agents_bulk")
        cls.agent_id2 = generate_entity_id("test_delete_agents_bulk")

    @classmethod
    def tearDownClass(cls):
        cls.client.delete_agent(cls.agent_id1)
        cls.client.delete_agent(cls.agent_id2)

    def setUp(self):
        try:
            self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id1)
            self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id2)
        except craft_err.CraftAiBadRequestError as e:
            if "one already exists" not in e.message:
                raise e

    def test_delete_multiple_agents_with_valid_id(self):
        """delete_agents_bulk should succeed when given valid `id`s.

        It should give a proper JSON response with a list containing two dicts
        with the `id`s being the same as the ones given as parameters.
        """
        payload = [{"id": self.agent_id1}, {"id": self.agent_id2}]
        resp = self.client.delete_agents_bulk(payload)

        self.assertEqual(resp[0].get("id"), self.agent_id1)
        self.assertEqual(resp[1].get("id"), self.agent_id2)


class TestDeleteGroupAgentsBulkSuccess(unittest.TestCase):
    """Checks that the client succeeds when deleting
    an/multiple agent(s) with OK input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agents = [
            generate_entity_id("test_delete_agents_bulk")
            for i in range(NB_AGENTS_TO_DELETE)
        ]

    @classmethod
    def tearDownClass(cls):
        for agent_id in cls.agents:
            cls.client.delete_agent(agent_id)

    def setUp(self):
        for agent in self.agents:
            self.client.delete_agent(agent)
            self.client.create_agent(valid_data.VALID_CONFIGURATION, agent)

    # This test is commented because there are currently some problems in the bulk.
    # def test_delete_a_lot_of_agents_with_valid_id(self):
    #   """delete_agents_bulk should succeed when given a lot of agent id.

    #   It should give a proper JSON response with a list containing dicts
    #   with `id` being the same as the one given as a parameter.
    #   """
    #   payload = [{"id": agent_id} for agent_id in self.agents]
    #   response = self.client.delete_agents_bulk(payload)

    #   for i, resp in enumerate(response):
    #     self.assertEqual(resp.get("id"), self.agents[i])


class TestDeleteAgentsBulkFailure(unittest.TestCase):
    """Checks that the client fails when deleting
    an/multiple agent(s) with invalid input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)

    def test_delete_multiple_agents_with_invalid_id(self):
        """delete_agents_bulk should fail when given multiple invalid `id`s
        or the `id` field doesn't exist.

        It should raise an error upon request for the deletion of a bulk of
        agents with invalid IDs.
        """
        payload = []
        # Add all the invalid ids to check
        for empty_id in invalid_data.UNDEFINED_KEY:
            payload.append({"id": invalid_data.UNDEFINED_KEY[empty_id]})
        # Add an agent that don't have any id field
        payload.append({})

        self.assertRaises(
            craft_err.CraftAiBadRequestError, self.client.delete_agents_bulk, payload
        )


class TestDeleteBulkAgentsBulkSomeFailure(unittest.TestCase):
    """Checks that the client succeed when deleting
    an/multiple agent(s) with bad input and an/multiple agent(s)
    with valid input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("test_delete_agents_bulk")

    @classmethod
    def tearDownClass(cls):
        cls.client.delete_agent(cls.agent_id)

    def setUp(self):
        try:
            self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)
        except craft_err.CraftAiBadRequestError as e:
            if "one already exists" not in e.message:
                raise e


# This test is commented because there are currently some problems in the bulk.
# def test_delete_some_agents_with_invalid_id(self):
#   """delete_agents_bulk should succeed when given some invalid `id`s and some valid.

#   It should give a proper JSON response with a list containing dicts.
#   The ones having invalid id have the `error` field being a CraftAiBadRequestError.
#   The ones having valid ids have the `id` field being the same as the one given
#   as a parameter.
#   """
#   payload = [{"id" : self.agent_id}]
#   # Add all the invalid ids to check
#   for empty_id in invalid_data.UNDEFINED_KEY:
#     payload.append({"id": invalid_data.UNDEFINED_KEY[empty_id]})
#   # Add an agent that don't have any id field
#   payload.append({})

#   resp = self.client.delete_agents_bulk(payload)

#   self.assertEqual(resp[0].get("id"), self.agent_id)
#   self.assertFalse("error" in resp[0])

#   for i in range(1, len(resp)):
#     self.assertTrue("error" in resp[i])
#     self.assertIsInstance(resp[i].get("error"), craft_err.CraftAiBadRequestError)
