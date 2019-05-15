import unittest
import copy
import pandas as pd
import numpy as np
from numpy.random import randn

import craftai.pandas
from craftai import errors as craft_err

from . import settings
from .data import valid_data
from .data import invalid_data

NB_OPERATIONS_TO_ADD = 1000
NB_AGENTS_TO_ADD_OPERATIONS = 50

SIMPLE_AGENT_CONFIGURATION = {
  "context": {
    "a": {
      "type": "continuous"
    },
    "b": {
      "type": "continuous"
    },
    "c": {
      "type": "continuous"
    },
    "d": {
      "type": "continuous"
    },
    "e": {
      "type": "continuous"
    }
  },
  "output": ["a"],
  "time_quantum": 100,
  "deactivate_missing_values": True,
}
SIMPLE_AGENT_DATA = pd.DataFrame(
  randn(300, 5),
  columns=["a", "b", "c", "d", "e"],
  index=pd.date_range("20130101", periods=300, freq="T").tz_localize("Europe/Paris")
)


SIMPLE_AGENT_DATA_DICT = [
  {
    "timestamp": 1458741230,
    "context": {
      "a": 10,
      "b": 10,
      "c": 10,
      "d": 10,
      "e": 10,
    }
  },
  {
    "timestamp": 1458741331,
    "context": {
      "a": 10,
      "b": 11,
      "c": 12,
      "e": 13,
    }
  },
  {
    "timestamp": 1458741432,
    "context": {
      "a": 13,
      "b": 44,
      "c": 33,
      "d": 22,
    }
  },
  {
    "timestamp": 1458741533,
    "context": {
      "a": 11,
      "d": 55,
      "e": 55,
    }
  },
  {
    "timestamp": 1458741634,
    "context": {
      "a": 33,
      "c": 66,
      "d": 22,
      "e": 44,
    }
  },
  {
    "timestamp": 1458741735,
    "context": {
      "a": 1,
      "b": 33,
      "c": 33,
      "d": 44,
    }
  }
]

BAD_INDEX = [
  range(300), # int (not timestamp)
  [1458741735]*300, # Same timestamp # TODO
  [None]*300, # null
  [item * 0.001 for item in range(1,301)]#float
]


pd.date_range("20130101", periods=300,freq="T").tz_localize("Europe/Paris")

class TestAddOperationsBulkSuccess(unittest.TestCase):
  """Checks that the client succeeds when adding operations to
  multiple agent(s) with OK input"""

  @classmethod
  def setUpClass(cls):
    cls.client = craftai.pandas.Client(settings.CRAFT_CFG)
    cls.agent_id1 = valid_data.VALID_ID  + "_" + settings.RUN_ID
    cls.agent_id2 = valid_data.VALID_ID_TWO  + "_" + settings.RUN_ID

  def setUp(self):
    self.client.delete_agent(self.agent_id1)
    self.client.delete_agent(self.agent_id2)
    self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, self.agent_id1)
    self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, self.agent_id2)

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_add_operations_bulk_with_correct_input1(self):
    """add_operations_bulk should succeed when given correct input data1,
    with correct `id`s and a correct df as `operations`.

    It should give a proper JSON response with a list containing dicts with
    'id' fields being the same as the one in parameters, 'message' fields
    being a string, 'status' fields being 201 and no 'error' field.
    """
    payload = [{"id": self.agent_id1, "operations": SIMPLE_AGENT_DATA},
               {"id": self.agent_id2, "operations": SIMPLE_AGENT_DATA}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertEqual(resp[0].get("status"), 201)
    self.assertEqual(resp[1].get("status"), 201)
    self.assertTrue("message" in resp[0].keys())
    self.assertTrue("message" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_with_correct_input2(self):
    """add_operations_bulk should succeed when given correct input data2,
    with correct `id`s and a correct dictionary as `operations`.

    It should give a proper JSON response with a list containing dicts with
    'id' fields being the same as the one in parameters, 'message' fields
    being a string, 'status' fields being 201 and no 'error' field.
    """
    payload = [{"id": self.agent_id1, "operations": SIMPLE_AGENT_DATA_DICT},
               {"id": self.agent_id2, "operations": SIMPLE_AGENT_DATA_DICT}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertEqual(resp[0].get("status"), 201)
    self.assertEqual(resp[1].get("status"), 201)
    self.assertTrue("message" in resp[0].keys())
    self.assertTrue("message" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])

  def test_add_operations_bulk_with_correct_input3(self):
    """add_operations_bulk should succeed when given correct input data3,
    with correct `id`s and a correct dictionary or df as `operations`.

    It should give a proper JSON response with a list containing dicts with
    'id' fields being the same as the one in parameters, 'message' fields
    being a string, 'status' fields being 201 and no 'error' field.
    """
    payload = [{"id": self.agent_id1, "operations": SIMPLE_AGENT_DATA},
               {"id": self.agent_id2, "operations": SIMPLE_AGENT_DATA_DICT}]
    resp = self.client.add_operations_bulk(payload)

    self.assertIsInstance(resp, list)
    self.assertEqual(resp[0].get("id"), self.agent_id1)
    self.assertEqual(resp[1].get("id"), self.agent_id2)
    self.assertEqual(resp[0].get("status"), 201)
    self.assertEqual(resp[1].get("status"), 201)
    self.assertTrue("message" in resp[0].keys())
    self.assertTrue("message" in resp[1].keys())

    self.addCleanup(self.clean_up_agents,
                    [self.agent_id1, self.agent_id2])


class TestAddOperationsBulkFailure(unittest.TestCase):
  """Checks that the client fail when adding operations to
  multiple agent(s) with incorrect input"""

  @classmethod
  def setUpClass(cls):
    cls.client = craftai.pandas.Client(settings.CRAFT_CFG)
    cls.agent_name = valid_data.VALID_ID_TEMPLATE + "{}_" + settings.RUN_ID

  def clean_up_agent(self, aid):
    # Makes sure that no agent with the standard ID remains
    self.client.delete_agent(aid)

  def clean_up_agents(self, aids):
    # Makes sure that no agent with the standard ID remains
    for aid in aids:
      self.clean_up_agent(aid)

  def test_add_operations_bulk_invalid_agent_id(self):
    """add_operations_bulk should fail when given non-string/empty ID.

    It should raise an error upon request for operations posting
    for all agents with an ID that is not of type string, since agent IDs
    should always be strings.
    """
    payload = []
    for empty_id in invalid_data.UNDEFINED_KEY:
      payload.append({"id": invalid_data.UNDEFINED_KEY[empty_id],
                      "operations": SIMPLE_AGENT_DATA})

    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.add_operations_bulk,
      payload
    )

  def test_add_operations_bulk_unexpected_property(self):
    """add_operations_bulk should fail when given a df with unexpected property
    (which is not in the context).

    It should raise an error upon request for operations posting for all agents
    with invalid operations set.
    """
    agent_id = self.agent_name.format(0)
    self.client.delete_agent(agent_id)
    self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, agent_id)

    df = pd.DataFrame(randn(300, 6),
                      columns=["a", "b", "c", "d", "e", "f"],
                      index=pd.date_range("20130101",
                                          periods=300,
                                          freq="T").tz_localize("Europe/Paris"))
    payload = [{"id": agent_id,
                "operations": df}]

    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.add_operations_bulk,
      payload
    )

    self.addCleanup(self.clean_up_agent,
                    agent_id)

  def test_add_operations_bulk_invalid_index(self):
    """add_operations_bulk should fail when given a df with unexpected property
    (which is not in the context).

    not time indexed
    TS null
    TS float
    TS neg
    TS same

    It should raise an error upon request for operations posting for all agents
    with invalid operations set.
    """
    list_agents = []
    payload = []
    for i, index in enumerate(BAD_INDEX):
      agent_id = self.agent_name.format(i)
      self.client.delete_agent(agent_id)
      self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, agent_id)

      df = pd.DataFrame(randn(300, 5),
                        columns=["a", "b", "c", "d", "e"],
                        index=index)
      payload.append({"id": agent_id, "operations": df})
      list_agents.append(agent_id)

    self.assertRaises(
      craft_err.CraftAiBadRequestError,
      self.client.add_operations_bulk,
      payload
    )

    self.addCleanup(self.clean_up_agents,
                    list_agents)

