import unittest

from craft_ai import Client, errors as craft_err

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data


class TestDeleteGeneratorsBulkSuccess(unittest.TestCase):
    """Checks that the client succeeds when creating
        an/multiple generator(s) with OK input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id1 = generate_entity_id("test_delete_g_bulk_a1")
        cls.agent_id2 = generate_entity_id("test_delete_g_bulk_a2")
        cls.generator_id1 = generate_entity_id("test_delete_g_bulk_g1")
        cls.generator_id2 = generate_entity_id("test_delete_g_bulk_g2")
        cls.filter = [cls.agent_id1, cls.agent_id2]
        cls.generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        cls.generator_configuration["filter"] = cls.filter

    def setUp(self):
        try:
            payload = [
                {"id":self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
                {"id":self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION},
            ]
            self.client.create_agents_bulk(payload)
            self.client.create_generator(self.generator_configuration, self.generator_id1)
            self.client.create_generator(self.generator_configuration, self.generator_id2)

        except craft_err.CraftAiBadRequestError as e:
            if "one already exists" not in e.message:
                raise e

    def tearDown(self):
        self.client.delete_agent(self.agent_id1)
        self.client.delete_agent(self.agent_id2)
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def clean_up_generators(self):
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def test_delete_one_generator(self):
        """delete_generators_bulk should succeed when given a string ID in a set
            It should give a proper JSON response with a list containing the dict
            with the `ids being the same as the one given as parameter."""

        payload = [{"id": self.generator_id1}]

        resp = self.client.delete_generators_bulk(payload)

        self.assertEqual(resp[0].get("id"), self.generator_id1)

        self.addCleanup(self.tearDown)

    def test_delete_multiple_generators(self):
        """delete_generators_bulk should succeed when given a list of string ID in a set
            It should give a proper JSON response with a list containing the dict
            with the `ids being the same as the one given as parameter."""

        payload = [{"id": self.generator_id1}, {"id": self.generator_id2}]

        resp = self.client.delete_generators_bulk(payload)

        self.assertEqual(resp[0].get("id"), self.generator_id1)
        self.assertEqual(resp[1].get("id"), self.generator_id2)

        self.addCleanup(self.tearDown)

class TestDeleteGeneratorsBulkFailure(unittest.TestCase):
    """Checks that the client fails when deleting
        an/multiple generator(s) with bad input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)

    def test_delete_multiple_generators_with_invalid_id(self):
        """delete_generators_bulk should fail when given multiple invalid `id`s
        or the `id` field doesn't exist. It should raise an error upon request for
        the deletion of a bulk of generators with invalid IDs."""

        payload = []

        for empty_id in invalid_data.UNDEFINED_KEY:
            payload.append({"id": invalid_data.UNDEFINED_KEY[empty_id]})

        payload.append({})

        self.assertRaises(
            craft_err.CraftAiBadRequestError, self.client.delete_generators_bulk, payload
        )


class TestDeleteBulkGeneratorsBulkSomeFailure(unittest.TestCase):
    """Checks that the client succeed when deleting
    an/multiple generator(s) with bad input and an/multiple generator(s)
    with valid input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id1 = generate_entity_id("test_delete_g_bulk_a1")
        cls.agent_id2 = generate_entity_id("test_delete_g_bulk_a2")
        cls.generator_id1 = generate_entity_id("test_delete_g_bulk_g1")
        cls.filter = [cls.agent_id1, cls.agent_id2]
        cls.generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        cls.generator_configuration["filter"] = cls.filter

    def setUp(self):
        try:
            payload = [
                {"id":self.agent_id1, "configuration": valid_data.VALID_CONFIGURATION},
                {"id":self.agent_id2, "configuration": valid_data.VALID_CONFIGURATION},
            ]
            self.client.create_agents_bulk(payload)
            self.client.create_generator(self.generator_configuration, self.generator_id1)

        except craft_err.CraftAiBadRequestError as e:
            if "one already exists" not in e.message:
                raise e

    def tearDown(self):
        self.client.delete_agent(self.agent_id1)
        self.client.delete_agent(self.agent_id2)
        self.client.delete_generator(self.generator_id1)

    def clean_up_generators(self):
        self.client.delete_generator(self.generator_id1)

    def test_delete_multiple_generators_with_some_invalid_id(self):
        """delete_generators_bulk should fail when given multiple invalid `id`s
        or the `id` field doesn't exist. It should raise an error upon request for
        the deletion of a bulk of generators with invalid IDs."""

        payload = []

        payload.append({"id": self.generator_id1})
        for empty_id in invalid_data.UNDEFINED_KEY:
            payload.append({"id": invalid_data.UNDEFINED_KEY[empty_id]})

        resp = self.client.delete_generators_bulk(payload)
        self.assertEqual(resp[0].get("id"), self.generator_id1)

        for i in range(1, len(payload)):
            self.assertEqual(craft_err.CraftAiBadRequestError, type(resp[i].get('error')))

        self.addCleanup(self.tearDown)

