import unittest

import craft_ai

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data


class TestGetGeneratorSuccess(unittest.TestCase):
    """Checks that the client succeeds when getting a generator with OK input"""

    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.generator_id = generate_entity_id("get_generator")

    def setUp(self):
        self.client.delete_generator(self.generator_id)
        self.client.create_generator(
            valid_data.VALID_GENERATOR_CONFIGURATION, self.generator_id
        )

    def tearDown(self):
        # Makes sure that no generator with the standard ID remains
        self.client.delete_generator(self.generator_id)

    def test_get_generator_with_correct_id(self):
        """get_generator should succeed when given a correct generator ID

    It should give a proper JSON response with `configuration` field being a
    string.
    """
        generator = self.client.get_generator(self.generator_id)
        self.assertIsInstance(generator, dict)
        generator_keys = generator.keys()
        self.assertTrue("configuration" in generator_keys)
        self.assertTrue("agents" in generator_keys)


class TestGetGeneratorFailure(unittest.TestCase):
    """Checks that the client fails properly when getting a generator with bad input"""

    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.generator_id = generate_entity_id("get_generator")

    def setUp(self):
        # Makes sure that no generator exists with the test id
        # (especially for test_get_generator_with_unknown_id)
        self.client.delete_generator(self.generator_id)

    def tearDown(self):
        # Makes sure that no generator with the standard ID remains
        self.client.delete_generator(self.generator_id)

    def test_get_generator_with_invalid_id(self):
        """get_generator should fail when given a non-string/empty string ID

    It should raise an error upon request for retrieval of
    a generator with an ID that is not of type string, since generator IDs
    should always be strings.
    """
        for empty_id in invalid_data.UNDEFINED_KEY:
            self.assertRaises(
                craft_ai.errors.CraftAiBadRequestError,
                self.client.get_generator,
                invalid_data.UNDEFINED_KEY[empty_id],
            )

    def test_get_generator_with_unknown_id(self):
        """get_generator should fail when given an unknown generator ID

    It should raise an error upon request for the retrieval of a generator
    that doesn't exist.
    """
        self.assertRaises(
            craft_ai.errors.CraftAiNotFoundError,
            self.client.get_generator,
            invalid_data.UNKNOWN_ID,
        )
