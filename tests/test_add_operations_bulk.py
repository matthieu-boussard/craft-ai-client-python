import unittest
import six

from nose.tools import nottest
from craftai import Client, errors as craft_err

from . import settings
from .data import valid_data
from .data import invalid_data

class TestCreateBulkAgentsSuccess(unittest.TestCase):
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
