import unittest

from craft_ai import Client, errors as craft_err

from . import settings
from .utils import generate_entity_id
from .data import valid_data
from .data import invalid_data


class TestCreateAgentSuccess(unittest.TestCase):
    """Checks that the client succeeds when creating an agent with OK input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("test_create_agent")

    def tearDown(self):
        # This ensures that agents are properly deleted every time
        self.client.delete_agent(self.agent_id)

    def setUp(self):
        # Makes sure that no agent with the same ID already exists
        resp = self.client.delete_agent(self.agent_id)
        self.assertIsInstance(resp, dict)
        resp_keys = resp.keys()
        self.assertTrue("message" in resp_keys)

    def clean_up_agent(self, aid):
        # Makes sure that no agent with the standard ID remains
        self.client.delete_agent(aid)

    def test_create_agent_with_generated_agent_id(self):
        """create_agent should succeed when given an empty `id` field

        It should give a proper JSON response with `id` and
        `configuration` fields being strings.
        """
        resp = self.client.create_agent(valid_data.VALID_CONFIGURATION)
        self.assertIsInstance(resp.get("id"), str)
        self.addCleanup(self.clean_up_agent, resp.get("id"))

    def test_create_agent_given_agent_id(self):
        """create_agent should succeed when given a string ID

        It should give a proper JSON response with `id` and
        `configuration` fields being strings and `id` being the same as the one
        given as a parameter.
        """
        resp = self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)
        self.assertEqual(resp.get("id"), self.agent_id)
        self.addCleanup(self.clean_up_agent, self.agent_id)


class TestCreateAgentFailure(unittest.TestCase):
    """Checks that the client fails when creating an agent with bad input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id = generate_entity_id("test_create_agent")

    def tearDown(self):
        # This ensures that agents are properly deleted every time
        self.client.delete_agent(self.agent_id)

    def setUp(self):
        # Makes sure that no agent with the same ID already exists
        resp = self.client.delete_agent(self.agent_id)
        self.assertIsInstance(resp, dict)
        resp_keys = resp.keys()
        self.assertTrue("message" in resp_keys)

    def clean_up_agent(self, aid):
        # Makes sure that no agent with the standard ID remains
        self.client.delete_agent(aid)

    def test_create_agent_with_existing_agent_id(self):
        """create_agent should fail when given an ID that already exists

        It should raise an error upon request for creation of
        an agent with an ID that already exists, since agent IDs
        should always be unique.
        """
        # Calling create_agent a first time
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id)
        # Asserting that an error is risen the second time
        self.assertRaises(
            craft_err.CraftAiBadRequestError,
            self.client.create_agent,
            valid_data.VALID_CONFIGURATION,
            self.agent_id,
        )
        self.addCleanup(self.clean_up_agent, self.agent_id)

    def test_create_agent_with_invalid_agent_id(self):
        """create_agent should fail whith an invalid agent id

        It should raise an error upon request for creation of
        an agent with an invalid id.
        """
        # Asserting that an error is risen the second time
        self.assertRaises(
            craft_err.CraftAiBadRequestError,
            self.client.create_agent,
            valid_data.VALID_CONFIGURATION,
            "toto/tutu",
        )

    def test_create_agent_with_invalid_context(self):
        """create_agent should fail when given an invalid or no context

        It should raise an error upon request for creation of
        an agent with no context or a context that is invalid.
        """
        for inv_context in invalid_data.INVALID_CONTEXTS:
            configuration = {
                "context": invalid_data.INVALID_CONTEXTS[inv_context],
                "output": ["lightbulbColor"],
                "time_quantum": 100,
            }
            self.assertRaises(
                craft_err.CraftAiBadRequestError,
                self.client.create_agent,
                configuration,
                self.agent_id,
            )
            self.addCleanup(self.clean_up_agent, self.agent_id)

    # this test is commented because current agent creation fails with no configuration key.
    def test_should_fail_when_given_no_configuration_key_in_the_request_body(self):
        """create_agent should fail when given no configuration key in the request body

        It should raise an error upon request for creation of an agent with
        no configuration key in the request body, since it is a mandatory field to
        create an agent.
        """
        # Testing all non dict configuration cases
        for empty_configuration in invalid_data.UNDEFINED_KEY:
            self.assertRaises(
                craft_err.CraftAiBadRequestError,
                self.client.create_agent,
                invalid_data.UNDEFINED_KEY[empty_configuration],
                self.agent_id,
            )
            self.addCleanup(self.clean_up_agent, self.agent_id)

    def test_create_agent_with_invalid_time_quantum(self):
        """create_agent should fail when given an invalid time quantum

        It should raise an error upon request for creation of an agent with
        an incorrect time quantum in the configuration, since it is essential to
        perform any action with craft ai.
        """
        for inv_tq in invalid_data.INVALID_TIME_QUANTA:
            configuration = {
                "context": valid_data.VALID_CONTEXT,
                "output": valid_data.VALID_OUTPUT,
                "time_quantum": invalid_data.INVALID_TIME_QUANTA[inv_tq],
            }
            self.assertRaises(
                craft_err.CraftAiBadRequestError,
                self.client.create_agent,
                configuration,
                self.agent_id,
            )
            self.addCleanup(self.clean_up_agent, self.agent_id)
