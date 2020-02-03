import unittest

from craftai import Client, errors as craft_err

from . import settings
from .data import valid_data
from .data import invalid_data

class TestCreateGeneratorSuccess(unittest.TestCase):
  """Checks that the client succeeds when creating an agent with OK input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id = valid_data.VALID_ID
    cls.generator_id = valid_data.VALID_GENERATOR_ID + "_" + settings.RUN_ID
    cls.filter = valid_data.VALID_GENERATOR_FILTER

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    # resp = self.client.create_agent(
    #   valid_data.VALID_CONFIGURATION,
    #   self.agent_id
    # )
    self.client.delete_agent(self.agent_id)
    self.client.delete_generator(self.generator_id)
    self.client.create_agent(
      valid_data.VALID_CONFIGURATION,
      self.agent_id
    )


  def clean_up_generator(self, generator_id):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_generator(generator_id)

  def test_create_generator_given_generator_id(self):
    """create_generator should succeed when given a string ID

    It should give a proper JSON response with `id` and
    `configuration` fields being strings and `id` being the same as the one
    given as a parameter.
    """
    GENERATOR_CONFIGURATION = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
    GENERATOR_CONFIGURATION["filter"] = self.filter
    resp = self.client.create_generator(
      GENERATOR_CONFIGURATION,
      self.generator_id
    )
    self.assertEqual(resp.get("id"), self.generator_id)
    self.addCleanup(self.clean_up_generator, self.generator_id)


class TestCreateGeneratorFailure(unittest.TestCase):
  """Checks that the client fails when creating an generator with bad input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id = valid_data.VALID_ID
    cls.generator_id = valid_data.VALID_GENERATOR_ID + "_" + settings.RUN_ID
    cls.filter = valid_data.VALID_GENERATOR_FILTER


  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    self.client.delete_agent(self.agent_id)
    self.client.create_agent(
      valid_data.VALID_CONFIGURATION,
      self.agent_id
    )

  def clean_up_generator(self, generator_id):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(generator_id)

  def test_create_generator_with_existing_generator_id(self):
    """create_generator should fail when given an ID that already exists

    It should raise an error upon request for creation of
    an generator with an ID that already exists, since generator IDs
    should always be unique.
    """
    # Calling create_generator a first time
    GENERATOR_CONFIGURATION = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
    GENERATOR_CONFIGURATION["filter"] = self.filter
    self.client.create_generator(
      GENERATOR_CONFIGURATION,
      self.generator_id
    )
    # Asserting that an error is risen the second time
    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.create_generator,
      GENERATOR_CONFIGURATION,
      self.generator_id)
    self.addCleanup(
      self.clean_up_generator,
      self.generator_id)

  def test_create_generator_with_invalid_generator_id(self):
    """create_generator should fail whith an invalid generator id

    It should raise an error upon request for creation of
    an generator with an invalid id.
    """
    # Asserting that an error is risen the second time
    GENERATOR_CONFIGURATION = valid_data.VALID_GENERATOR_CONFIGURATION.copy()
    GENERATOR_CONFIGURATION["filter"] = self.filter
    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.create_generator,
      GENERATOR_CONFIGURATION,
      "toto/tutu")

  def test_create_generator_with_invalid_context(self):
    """create_generator should fail when given an invalid or no context

    It should raise an error upon request for creation of
    an generator with no context or a context that is invalid.
    """
    for inv_context in invalid_data.INVALID_CONTEXTS:
      configuration = {
        "context": invalid_data.INVALID_CONTEXTS[inv_context],
        "output": ["lightbulbColor"],
        "time_quantum": 100,
        "filter": self.filter
      }
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.create_generator,
        configuration,
        self.generator_id)
      self.addCleanup(
        self.clean_up_generator,
        self.generator_id)

  def test_create_generator_with_undefined_configuration(self):
    """create_generator should fail when given no configuration key in the request body

    It should raise an error upon request for creation of an generator with
    no configuration key in the request body, since it is a mandatory field to
    create an generator.
    """
    # Testing all non dict configuration cases
    for empty_configuration in invalid_data.UNDEFINED_KEY:
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.create_generator,
        invalid_data.UNDEFINED_KEY[empty_configuration],
        self.generator_id,
        )
      self.addCleanup(
        self.clean_up_generator,
        self.generator_id)

  def test_create_generator_with_invalid_time_quantum(self):
    """create_generator should fail when given an invalid time quantum

    It should raise an error upon request for creation of an generator with
    an incorrect time quantum in the configuration, since it is essential to
    perform any action with craft ai.
    """
    for inv_tq in invalid_data.INVALID_TIME_QUANTA:
      configuration = {
        "context": valid_data.VALID_CONTEXT,
        "output": valid_data.VALID_OUTPUT,
        "time_quantum": invalid_data.INVALID_TIME_QUANTA[inv_tq],
        "filter": self.filter
      }
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.create_generator,
        configuration,
        self.generator_id
      )
      self.addCleanup(
        self.clean_up_generator,
        self.generator_id)

  def test_create_generator_with_invalid_agent_name_in_filter(self):
    """create_generator should fail when given an invalid filter

    It should raise an error upon request for creation of an generator with
    incorrect filter, since it is essential to
    the creation of generator.
    """
    CONFIGURATION_INVALID_FILTER = valid_data.VALID_GENERATOR_CONFIGURATION
    for inv_filter in invalid_data.INVALID_FILTER:
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.create_generator,
        valid_data.VALID_GENERATOR_CONFIGURATION,
        self.generator_id
      )
      self.addCleanup(
        self.clean_up_generator,
        self.generator_id)
