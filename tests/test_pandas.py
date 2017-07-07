import pandas as pd
import numpy as np

from numpy.random import randn

import craftai.pandas

from nose.tools import assert_equal, assert_raises, with_setup

from . import settings

AGENT_ID = "test_pandas_" + settings.RUN_ID
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
  "time_quantum": 100
}
SIMPLE_AGENT_DATA = pd.DataFrame(
  randn(300, 5),
  columns=['a', 'b', 'c', 'd', 'e'],
  index=pd.date_range('20130101', periods=300, freq='T')
)
COMPLEX_AGENT_CONFIGURATION = {
  "context": {
    "a": {
      "type": "continuous"
    },
    "b": {
      "type": "enum"
    },
    "tz": {
      "type": "timezone"
    }
  },
  "output": ["b"],
  "time_quantum": 100
}
COMPLEX_AGENT_DATA = pd.DataFrame(
  [
    [1, 'Pierre', '+02:00'],
    [2, 'Paul'],
    [3],
    [4],
    [5, 'Jacques'],
    [6],
    [7],
    [8, np.nan, '+01:00'],
    [9],
    [10]
  ],
  columns=['a', 'b', 'tz'],
  index=pd.date_range('20130101', periods=10, freq='D')
)
CLIENT = craftai.pandas.Client(settings.CRAFT_CFG)

def setup_simple_agent():
  CLIENT.delete_agent(AGENT_ID)
  CLIENT.create_agent(SIMPLE_AGENT_CONFIGURATION, AGENT_ID)

def setup_complex_agent():
  CLIENT.delete_agent(AGENT_ID)
  CLIENT.create_agent(COMPLEX_AGENT_CONFIGURATION, AGENT_ID)

def teardown():
  CLIENT.delete_agent(AGENT_ID)

@with_setup(setup_simple_agent, teardown)
def test_add_operations_df_bad_index():
  df = pd.DataFrame(randn(10, 5),
                    columns=['a', 'b', 'c', 'd', 'e'])

  assert_raises(
    craftai.pandas.errors.CraftAiBadRequestError,
    CLIENT.add_operations,
    AGENT_ID,
    df
  )

@with_setup(setup_simple_agent, teardown)
def test_add_operations_df():
  CLIENT.add_operations(AGENT_ID, SIMPLE_AGENT_DATA)
  agent = CLIENT.get_agent(AGENT_ID)
  assert_equal(agent['firstTimestamp'], SIMPLE_AGENT_DATA.first_valid_index().value // 10 ** 9)
  assert_equal(agent['lastTimestamp'], SIMPLE_AGENT_DATA.last_valid_index().value // 10 ** 9)

@with_setup(setup_complex_agent, teardown)
def test_add_operations_df_complex_agent():
  CLIENT.add_operations(AGENT_ID, COMPLEX_AGENT_DATA)
  agent = CLIENT.get_agent(AGENT_ID)
  assert_equal(agent['firstTimestamp'], COMPLEX_AGENT_DATA.first_valid_index().value // 10 ** 9)
  assert_equal(agent['lastTimestamp'], COMPLEX_AGENT_DATA.last_valid_index().value // 10 ** 9)

@with_setup(setup_simple_agent, teardown)
def test_add_operations_df_unexpected_property():
  df = pd.DataFrame(randn(300, 6),
                    columns=['a', 'b', 'c', 'd', 'e', 'f'],
                    index=pd.date_range('20130101', periods=300, freq='T'))

  assert_raises(
    craftai.pandas.errors.CraftAiBadRequestError,
    CLIENT.add_operations,
    AGENT_ID,
    df
  )

def setup_simple_agent_with_data():
  setup_simple_agent()
  CLIENT.add_operations(AGENT_ID, SIMPLE_AGENT_DATA)

@with_setup(setup_simple_agent_with_data, teardown)
def test_get_operations_list_df():
  df = CLIENT.get_operations_list(AGENT_ID)

  assert_equal(len(df), 300)
  assert_equal(len(df.dtypes), 5)
  assert_equal(df.first_valid_index(), pd.Timestamp('2013-01-01 00:00:00'))
  assert_equal(df.last_valid_index(), pd.Timestamp('2013-01-01 04:59:00'))

def setup_complex_agent_with_data():
  setup_complex_agent()
  CLIENT.add_operations(AGENT_ID, COMPLEX_AGENT_DATA)

@with_setup(setup_complex_agent_with_data, teardown)
def test_get_operations_list_df_complex_agent():
  df = CLIENT.get_operations_list(AGENT_ID)

  assert_equal(
    df['b'].notnull().tolist(),
    [True, True, False, False, True, False, False, False, False, False]
  )

  assert_equal(len(df), 10)
  assert_equal(len(df.dtypes), 3)
  assert_equal(df.first_valid_index(), pd.Timestamp('2013-01-01 00:00:00'))
  assert_equal(df.last_valid_index(), pd.Timestamp('2013-01-10 00:00:00'))
