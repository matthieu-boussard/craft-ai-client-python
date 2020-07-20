import unittest

from craft_ai.pandas import CRAFTAI_PANDAS_ENABLED

if CRAFTAI_PANDAS_ENABLED:

    import json
    import pandas as pd

    import craft_ai.pandas

    from . import settings


@unittest.skipIf(CRAFTAI_PANDAS_ENABLED==False, "pandas is not enabled")
class TestPandasType(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.client = craft_ai.pandas.Client(settings.CRAFT_CFG)
    
    def test_predict_month(self):
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

        states = pd.read_csv("tests/data/state_only_month.csv", index_col=0)
        states.index = pd.to_datetime(states.index)
        self.client.decide_from_contexts_df(tree, states)
