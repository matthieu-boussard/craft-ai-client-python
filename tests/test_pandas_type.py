import json
import pandas as pd

from nose.tools import with_setup

import craftai.pandas


from . import settings

CLIENT = craftai.pandas.Client(settings.CRAFT_CFG)

def setup_nothing():
  pass

def teardown_nothing():
  pass

@with_setup(setup_nothing, teardown_nothing)
def test_predict_month():
  tree_json = """{
        \"_version\": \"1.1.0\",
        \"trees\": {
            \"scream\": {
                \"children\": [
                    {
                        \"predicted_value\": 1.489081,
                        \"confidence\": 0.5,
                        \"standard_deviation\": 0,
                        \"decision_rule\": {
                            \"operand\": -2000.9,
                            \"operator\": \"<\",
                            \"property\": \"goat\"
                        }
                    },
                    {
                        \"predicted_value\": 1.309041,
                        \"confidence\": 0.5,
                        \"standard_deviation\": 0,
                        \"decision_rule\": {
                            \"operand\": -2000.9,
                            \"operator\": \">=\",
                            \"property\": \"goat\"
                        }
                    }
                ]
            }
        },
        \"configuration\": {
            \"time_quantum\": 20000,
            \"operations_as_events\": true,
            \"learning_period\": 157680000,
            \"tree_max_operations\": 50000,
            \"tree_max_depth\": 3,
            \"context\": {
                \"scream\": {
                    \"type\": \"continuous\"
                },
                \"goat\": {
                    \"type\": \"continuous\"
                },
                \"month\": {
                    \"type\": \"month_of_year\",
                    \"is_generated\": false
                }
            },
            \"output\": [
                \"scream\"
            ]
        }
  }"""
  tree = json.loads(tree_json)

  state_history = pd.read_pickle("tests/data/state_only_month.pkl")
  CLIENT.decide_from_contexts_df(tree, state_history)
