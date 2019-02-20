import unittest
import semver

from craftai import Client, errors as craft_err

from . import settings
from .data import valid_data
from .data import invalid_data

VALID_L_CFG = valid_data.VALID_LARGE_CONFIGURATION
VALID_L_BATCH_DURATION = VALID_L_CFG["learning_period"] * 4
VALID_L_ENUM_VALUES = ["CYAN", "MAGENTA", "YELLOW", "BLACK"]

class TestGetDecisionTreesSuccess(unittest.TestCase):
  """Checks that the client succeeds when getting
  an/multiple decision tree(s) with OK input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID_TWO  + "_" + settings.RUN_ID

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    self.client.delete_agent(self.agent_id1)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id1)
    self.client.add_operations(self.agent_id1, valid_data.VALID_OPERATIONS_SET)

    self.client.delete_agent(self.agent_id2)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id2)
    self.client.add_operations(self.agent_id2, valid_data.VALID_OPERATIONS_SET)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_get_one_decision_trees_with_correct_input(self):
    """get_decision_trees should succeed when given an correct input
    (correct id and correct timestamp).

    It should give a proper JSON response with a list containing a dict
    with `id` field being string and 'tree' field being a dict.
    """
    payload = [{"id": self.agent_id1, "timestamp": valid_data.VALID_TIMESTAMP}]

    decision_trees = self.client.get_decision_trees(payload)

    self.assertIsInstance(decision_trees, list)
    self.assertIsInstance(decision_trees[0], dict)
    self.assertIsInstance(decision_trees[0].get("tree"), dict)
    self.assertNotEqual(decision_trees[0].get("tree").get("_version"), None)
    self.assertNotEqual(decision_trees[0].get("tree").get("configuration"), None)
    self.assertNotEqual(decision_trees[0].get("tree").get("trees"), None)

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_get_all_decision_trees_with_correct_input(self):
    """get_decision_trees should succeed when given an correct input
    (correct id and correct timestamp).

    It should give a proper JSON response with a list containing two dicts
    with `id` field being string and 'tree' field being a dict.
    """
    payload = [{"id": self.agent_id1, "timestamp": valid_data.VALID_TIMESTAMP},
               {"id": self.agent_id2, "timestamp": valid_data.VALID_TIMESTAMP}]

    decision_trees = self.client.get_decision_trees(payload)

    self.assertIsInstance(decision_trees, list)
    self.assertIsInstance(decision_trees[0], dict)
    self.assertEqual(decision_trees[0].get("id"),self.agent_id1)
    self.assertIsInstance(decision_trees[0].get("tree"), dict)
    self.assertNotEqual(decision_trees[0].get("tree").get("_version"), None)
    self.assertNotEqual(decision_trees[0].get("tree").get("configuration"), None)
    self.assertNotEqual(decision_trees[0].get("tree").get("trees"), None)
    self.assertIsInstance(decision_trees[1], dict)
    self.assertEqual(decision_trees[1].get("id"),self.agent_id2)
    self.assertIsInstance(decision_trees[1].get("tree"), dict)
    self.assertNotEqual(decision_trees[1].get("tree").get("_version"), None)
    self.assertNotEqual(decision_trees[1].get("tree").get("configuration"), None)
    self.assertNotEqual(decision_trees[1].get("tree").get("trees"), None)

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_get_decision_trees_specific_version(self):
    """get_decision_trees should succeed when given a specific version.

    It should give a proper JSON response with a list containing a dict
    with `id` field being string and 'tree' field being a dict with the
    field 'version''major' being the version given as a parameter.
    """
    payload = [{"id": self.agent_id1, "timestamp": valid_data.VALID_TIMESTAMP},
               {"id": self.agent_id2, "timestamp": valid_data.VALID_TIMESTAMP}]
    version = 1
    decision_trees = self.client.get_decision_trees(payload, version)

    self.assertNotEqual(decision_trees[0].get("tree").get("_version"), None)
    tree_version = semver.parse(decision_trees[0].get("tree").get("_version"))
    self.assertEqual(tree_version["major"], version)
    self.assertNotEqual(decision_trees[1].get("tree").get("_version"), None)
    tree_version = semver.parse(decision_trees[1].get("tree").get("_version"))
    self.assertEqual(tree_version["major"], version)

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_get_decision_trees_without_timestamp(self):
    """get_decision_trees should succeed when given no timestamp.

    It should give a proper JSON response with a list containing a dict
    with `id` field being string and 'tree' field being a dict and the
    timestamp should be the same as the one of the last operation.
    """
    payload = [{"id": self.agent_id1},
               {"id": self.agent_id2}]
    decision_trees = self.client.get_decision_trees(payload)
    ground_truth_decision_tree1 = self.client.get_decision_tree(self.agent_id1, 1458741262)
    ground_truth_decision_tree2 = self.client.get_decision_tree(self.agent_id2, 1458741262)

    self.assertEqual(decision_trees[0].get("tree"), ground_truth_decision_tree1)
    self.assertEqual(decision_trees[1].get("tree"), ground_truth_decision_tree2)

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])


class TestGetDecisionTreesFailure(unittest.TestCase):
  """Checks that the client succeeds when getting
  an/multiple decision tree(s) with OK input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID_TWO  + "_" + settings.RUN_ID

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    self.client.delete_agent(self.agent_id1)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id1)
    self.client.add_operations(self.agent_id1, valid_data.VALID_OPERATIONS_SET)

    self.client.delete_agent(self.agent_id2)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id2)
    self.client.add_operations(self.agent_id2, valid_data.VALID_OPERATIONS_SET)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_get_all_decision_trees_with_invalid_id(self):
    """get_decision_trees should fail when given non-string/empty string ID

    It should raise an error upon request for retrieval of multiple agents's
    decision tree with an ID that is not of type string, since agent IDs
    should always be strings.
    """
    for empty_id in invalid_data.UNDEFINED_KEY:
      payload = [{"id": invalid_data.UNDEFINED_KEY[empty_id],
                  "timestamp": valid_data.VALID_TIMESTAMP},
                 {"id": invalid_data.UNDEFINED_KEY[empty_id],
                  "timestamp": valid_data.VALID_TIMESTAMP}]
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.get_decision_trees,
        payload
      )
      self.addCleanup(self.clean_up_agents,
                      [self.agent_id1, self.agent_id2])

  def test_get_all_decision_trees_with_unknown_id(self):
    """get_decision_trees should fail when given unknown string ID

    It should raise an error upon request for retrieval of multiple agents's
    decision tree with an ID that is not known.
    """
    payload = [{"id": invalid_data.UNKNOWN_ID, "timestamp": valid_data.VALID_TIMESTAMP},
               {"id": invalid_data.UNKNOWN_ID_TWO, "timestamp": valid_data.VALID_TIMESTAMP}]
    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.get_decision_trees,
      payload
    )
    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_get_all_decision_trees_invalid_timestamp(self):
    """get_decision_trees should fail when given invalid timestamps

    It should raise an error upon request for retrieval of multiple agents's
    decision tree with an invalid timestamp, since timestamp should always be
    positive integer.
    """
    for timestamp in invalid_data.INVALID_TIMESTAMPS:
      payload = [{"id": self.agent_id1, "timestamp": timestamp},
                 {"id": self.agent_id2, "timestamp": timestamp}]
      self.assertRaises(
        craft_err.CraftAiBadRequestError,
        self.client.get_decision_trees,
        payload
      )
      self.addCleanup(self.clean_up_agents,
                      [self.agent_id1, self.agent_id2])


class TestGetDecisionTreesSomeFailure(unittest.TestCase):
  """Checks that the client succeed when getting an/multiple agent(s)
  with bad input and an/multiple agent(s) with valid input"""

  @classmethod
  def setUpClass(cls):
    cls.client = Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID_TWO  + "_" + settings.RUN_ID

  def setUp(self):
    # Makes sure that no agent with the same ID already exists
    self.client.delete_agent(self.agent_id1)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id1)
    self.client.add_operations(self.agent_id1, valid_data.VALID_OPERATIONS_SET)

    self.client.delete_agent(self.agent_id2)
    self.client.create_agent(valid_data.VALID_CONFIGURATION, self.agent_id2)
    self.client.add_operations(self.agent_id2, valid_data.VALID_OPERATIONS_SET)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_get_some_decision_trees_with_invalid_id(self):
    """get_decision_trees should succeed when given some non-string/empty string IDs
    and some valid IDs.

    It should give a proper JSON response with a list containing two dicts.
    The first one having the `error` field being a CraftAiBadRequestError.
    The second one with `id` field being string and 'tree' field being a dict.
    """
    for empty_id in invalid_data.UNDEFINED_KEY:
      payload = [{"id": invalid_data.UNDEFINED_KEY[empty_id], 
                  "timestamp": valid_data.VALID_TIMESTAMP},
                 {"id": self.agent_id2,
                  "timestamp": valid_data.VALID_TIMESTAMP}]
      decision_trees = self.client.get_decision_trees(payload)

      self.assertIsInstance(decision_trees[0].get("error"), craft_err.CraftAiBadRequestError)
      self.assertEqual(decision_trees[1].get("id"),self.agent_id2)
      self.assertIsInstance(decision_trees[1].get("tree"), dict)
      self.assertNotEqual(decision_trees[1].get("tree").get("_version"), None)
      self.assertNotEqual(decision_trees[1].get("tree").get("configuration"), None)
      self.assertNotEqual(decision_trees[1].get("tree").get("trees"), None)

      self.addCleanup(self.clean_up_agents,
                      [self.agent_id1, self.agent_id2])

  def test_get_some_decision_trees_with_unknown_id(self):
    """get_decision_trees should succeed when given some unknown string IDs
    and some known IDs.

    It should give a proper JSON response with a list containing two dicts.
    The first one having the `error` field being a CraftAiNotFoundError.
    The second one with `id` field being string and 'tree' field being a dict.
    """
    payload = [{"id": invalid_data.UNKNOWN_ID, "timestamp": valid_data.VALID_TIMESTAMP},
               {"id": self.agent_id2, "timestamp": valid_data.VALID_TIMESTAMP}]
    decision_trees = self.client.get_decision_trees(payload)

    self.assertIsInstance(decision_trees[0].get("error"), craft_err.CraftAiNotFoundError)
    self.assertEqual(decision_trees[1].get("id"), self.agent_id2)
    self.assertIsInstance(decision_trees[1].get("tree"), dict)
    self.assertNotEqual(decision_trees[1].get("tree").get("_version"), None)
    self.assertNotEqual(decision_trees[1].get("tree").get("configuration"), None)
    self.assertNotEqual(decision_trees[1].get("tree").get("trees"), None)

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_get_all_decision_trees_invalid_timestamp(self):
    """get_decision_trees should succeed when given some invalid timestamps
    and some valid ones.

    It should give a proper JSON response with a list containing two dicts.
    The first one having the `error` field being a CraftAiBadRequestError.
    The second one with `id` field being string and 'tree' field being a dict.
    """
    for timestamp in invalid_data.INVALID_TIMESTAMPS:
      payload = [{"id": self.agent_id1, "timestamp": timestamp},
                 {"id": self.agent_id2, "timestamp": valid_data.VALID_TIMESTAMP}]
      decision_trees = self.client.get_decision_trees(payload)

      self.assertEqual(decision_trees[0].get("id"),self.agent_id1)
      self.assertIsInstance(decision_trees[0].get("error"), craft_err.CraftAiBadRequestError)
      self.assertEqual(decision_trees[1].get("id"),self.agent_id2)
      self.assertIsInstance(decision_trees[1].get("tree"), dict)
      self.assertNotEqual(decision_trees[1].get("tree").get("_version"), None)
      self.assertNotEqual(decision_trees[1].get("tree").get("configuration"), None)
      self.assertNotEqual(decision_trees[1].get("tree").get("trees"), None)

      self.addCleanup(self.clean_up_agents,
                      [self.agent_id1, self.agent_id2])
