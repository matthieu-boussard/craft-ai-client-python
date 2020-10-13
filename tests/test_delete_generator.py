import unittest

import craft_ai

from . import settings
from .utils import generate_entity_id
from .data import valid_data, invalid_data


class TestDeleteGeneratorWithValidID(unittest.TestCase):
    """Checks that the client succeeds when deleting a generator with OK input"""

    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.generator_id = generate_entity_id("test_delete_generator")

    @classmethod
    def tearDownClass(cls):
        cls.client.delete_generator(cls.generator_id)

    def setUp(self):
        # Creating a generator may raise an error if one with the same ID
        # already exists. Although it shouldn't matter for the deletion test,
        # it is necessary to catch this kind of errors.
        try:
            self.client.create_generator(
                valid_data.VALID_GENERATOR_CONFIGURATION, self.generator_id
            )
        except craft_ai.errors.CraftAiBadRequestError as e:
            if "one already exists" not in e.message:
                raise e

    def test_delete_generator_with_valid_id(self):
        resp = self.client.delete_generator(self.generator_id)
        self.assertIsInstance(resp, dict)
        self.assertTrue("id" in resp.keys())


class TestDeleteGeneratorWithUnknownID(unittest.TestCase):
    """Checks that the client succeeds when deleting a generator which
    doesn't exist"""

    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)
        cls.generator_id = generate_entity_id("test_delete_generator")

    @classmethod
    def tearDownClass(cls):
        cls.client.delete_generator(cls.generator_id)


    def test_delete_generator_with_unknown_id(self):
        """delete_generator should succeed when given a non-string/empty string ID

        It should return a json with just a message upon request for
        deletion of a generator with an ID that is not of type string,
        since generator IDs should always be strings.
        """

        # Calling delete twice to make sure the ID doesn't exist
        # Since it's the function we are testing, it wouldn't be clean
        # to do this in the setUp phase.
        self.client.delete_generator(self.generator_id)
        resp = self.client.delete_generator(self.generator_id)
        self.assertIsInstance(resp, dict)
        self.assertTrue("message" in resp.keys())


class TestDeleteGeneratorWithInvalidID(unittest.TestCase):
    """Checks that the client fails when trying to delete an invalid generator"""

    @classmethod
    def setUpClass(cls):
        cls.client = craft_ai.Client(settings.CRAFT_CFG)

    def setUp(self):
        self.client = craft_ai.Client(settings.CRAFT_CFG)

    def test_delete_generator_with_invalid_id(self):
        """delete_generator should fail when given a non-string/empty string ID

        It should raise an error upon request for deletion of
        a generator with an ID that is not of type string, since generator IDs
        should always be strings.
        """

        for empty_id in invalid_data.UNDEFINED_KEY:
            self.assertRaises(
                craft_ai.errors.CraftAiBadRequestError,
                self.client.delete_generator,
                invalid_data.UNDEFINED_KEY[empty_id],
            )
