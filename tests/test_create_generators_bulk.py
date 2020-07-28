import unittest

from craft_ai import Client, errors as craft_err

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data


class TestCreateGeneratorsBulkSuccess(unittest.TestCase):
    """Checks that the client succeeds when creating
        an/multiple generator(s) with OK input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id1 = generate_entity_id("bulk_agent")
        cls.agent_id2 = generate_entity_id("bulk_agent")
        cls.generator_id1 = generate_entity_id("bulk_generator")
        cls.generator_id2 = generate_entity_id("bulk_generator")
        cls.filter = [cls.agent_id1, cls.agent_id2]

    def setUp(self):
        self.client.delete_agent(self.agent_id1)
        self.client.delete_agent(self.agent_id2)
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)
        payload = [
            {"configuration": valid_data.VALID_CONFIGURATION, "id": self.agent_id1},
            {"configuration": valid_data.VALID_CONFIGURATION, "id": self.agent_id2},
        ]
        self.client.create_agents_bulk(payload)

    def tearDown(self):
        self.client.delete_agent(self.agent_id1)
        self.client.delete_agent(self.agent_id2)
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def clean_up_generators(self):
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def test_create_one_generator(self):
        """create_generators_bulk should succeed when given a string ID in a set
            It should give a proper JSON response with `id` and
            `configuration` fields being strings and `id` being the same as the one
            given as a parameter."""
        generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        generator_configuration["filter"] = self.filter
        payload = [{"id": self.generator_id1, "configuration": generator_configuration}]

        resp = self.client.create_generators_bulk(payload)

        self.assertEqual(resp[0].get("id"), self.generator_id1)
        self.addCleanup(self.clean_up_generators)

    def test_create_multiple_generators(self):
        """create_generators_bulk should succeed when given a set of string IDs
            It should give a proper JSON response with `id` and
            `configuration` fields being strings and `id` being the same as the one
            given as a parameter."""
        generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        generator_configuration["filter"] = self.filter
        payload = [
            {"id": self.generator_id1, "configuration": generator_configuration},
            {"id": self.generator_id2, "configuration": generator_configuration}
        ]

        resp = self.client.create_generators_bulk(payload)

        self.assertEqual(resp[0].get("id"), self.generator_id1)
        self.assertEqual(resp[1].get("id"), self.generator_id2)
        self.addCleanup(self.clean_up_generators)


class TestCreateGeneratorsBulkFailure(unittest.TestCase):
    """Checks that the client fails when creating
        an/multiple generator(s) with bad input"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id1 = generate_entity_id("test_create_generators_bulk_agent")
        cls.agent_id2 = generate_entity_id("test_create_generators_bulk_agent")
        cls.generator_id1 = generate_entity_id("test_create_generators_bulk_generator")
        cls.generator_id2 = generate_entity_id("test_create_generators_bulk_generator")
        cls.filter = [cls.agent_id1, cls.agent_id2]

    def setUp(self):
        self.client.delete_agent(self.agent_id1)
        self.client.delete_agent(self.agent_id2)
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)
        payload = [
            {"configuration": valid_data.VALID_CONFIGURATION},
            {"configuration": valid_data.VALID_CONFIGURATION},
        ]
        self.client.create_agents_bulk(payload)

    def tearDown(self):
        self.client.delete_agent(self.agent_id1)
        self.client.delete_agent(self.agent_id2)
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def clean_up_generators(self):
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def test_create_multiple_generators_with_invalid_ids(self):
        """create_generators_bulk should fail when given a set of invalid IDs
            It should raise an error upon request for creation of all generators with
            invalid id."""
        generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        generator_configuration["filter"] = self.filter
        payload = [
            {"id": 123, "configuration": generator_configuration},
            {"id": 345, "configuration": generator_configuration}
        ]

        self.assertRaises(
            craft_err.CraftAiBadRequestError, self.client.create_generators_bulk, payload
        )

    def test_create_multiple_generators_with_undefined_configurations(self):
        """create_generators_bulk should fail when given no configurations
            It should raise an error upon request for creation of all generators with
            undefined configurations."""

        payload = [
            {"id": self.generator_id1},
            {"id": self.generator_id2}
        ]

        self.assertRaises(
            craft_err.CraftAiBadRequestError, self.client.create_generators_bulk, payload
        )

    def test_create_multiple_generators_with_no_filter(self):
        """create_generators_bulk should fail when given no filter
            It should raise an error upon request for creation of all generators with
            no filter."""

        generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        generator_configuration.pop("filter", None)

        payload = [
            {"id": self.generator_id1, "configuration": generator_configuration},
            {"id": self.generator_id2, "configuration": generator_configuration}
        ]

        self.assertRaises(
            craft_err.CraftAiBadRequestError, self.client.create_generators_bulk, payload
        )

class TestCreateGeneratorsBulkSomeFailure(unittest.TestCase):
    """Checks that the client succeed when creating an/multiple generator(s)
        with bad input and an/multiple generator(s) with valid input"""

    @classmethod
    def setUpClass(cls):
        add = '3'
        cls.client = Client(settings.CRAFT_CFG)
        cls.agent_id1 = generate_entity_id("test_create_gen_bulk_ag"+add)
        cls.agent_id2 = generate_entity_id("test_create_gen_bulk_ag"+add)
        cls.generator_id1 = generate_entity_id("test_create_gen_bulk_gen"+add)
        cls.generator_id2 = generate_entity_id("test_create_gen_bulk_gen"+add)
        cls.filter = [cls.agent_id1, cls.agent_id2]

    def setUp(self):
        self.client.delete_agent(self.agent_id1)
        self.client.delete_agent(self.agent_id2)
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id1)
        self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id2)

    def tearDown(self):
        self.client.delete_agent(self.agent_id1)
        self.client.delete_agent(self.agent_id2)
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def clean_up_generators(self):
        self.client.delete_generator(self.generator_id1)
        self.client.delete_generator(self.generator_id2)

    def test_create_some_generators_with_invalid_generator_id(self):
        """create_generators_bulk should succeed when some of the ID given are invalid
        and the others are valid.

        It should give a proper JSON response with a list containing dicts.
        The ones having invalid IDs have the `error` field being a CraftAiBadRequestError.
        The ones having valid IDs have `configuration` field being strings.
        In either case they should have 'id' being the same as the one given as a parameter.
        """
        generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        generator_configuration["filter"] = self.filter
        payload = [
            {"id": self.generator_id1, "configuration": generator_configuration},
            {"id": 123, "configuration": generator_configuration}
        ]

        resp = self.client.create_generators_bulk(payload)

        self.assertEqual(resp[0].get("id"), self.generator_id1)
        self.assertTrue("configuration" in resp[0])

        self.assertEqual(resp[1].get("id"), 123)
        self.assertIsInstance(resp[1].get("error"), craft_err.CraftAiBadRequestError)
        self.assertFalse("configuration" in resp[1])

        self.addCleanup(self.tearDown)

    def test_create_repeated_generator_id(self):
        """create_generators_bulk should succeed when generators in a bulk have the same ID given.
        It should give a proper JSON response with a list containing two dicts.
        The first one should have 'id' being the same as the one given as a parameter,
        and the `configuration` field being strings.
        The second one should have `id` being the same as the one given as a parameter
        'error' field being a CraftAiBadRequestError.
        """
        generator_configuration = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
        generator_configuration["filter"] = self.filter
        payload = [
            {"id": self.generator_id1, "configuration": generator_configuration},
            {"id": self.generator_id1, "configuration": generator_configuration}
        ]

        resp = self.client.create_generators_bulk(payload)

        self.assertEqual(resp[0].get("id"), self.generator_id1)
        self.assertTrue("configuration" in resp[0])

        self.assertIsInstance(resp[1].get("error"), craft_err.CraftAiBadRequestError)

        self.addCleanup(self.clean_up_generators)

