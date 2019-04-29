# pylint: skip-file
import os
import random as rnd
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin

class CraftEstimator(BaseEstimator):

  def __init__(self,
               agent_name="agent_test",
               configuration=None,
               add_timestamps_for_static=False):
    # The JSON configuration necessary to create a craft ai agent
    # See the doc for more details (https://beta.craft.ai/doc/http).
    self.configuration = configuration

    # The agent name used for this craft ai agent.
    self.agent_name = agent_name

    # If multiple agents are launched - with a GridSearch for example
    # The given agent name will be used as a base name for all the tested
    # agents.
    self.agent_name_base = agent_name

    import craftai.pandas as craftai_pandas
    # Initialize the craft ai client.
    self.craft_client = craftai_pandas.Client({
      "token": os.environ.get("CRAFT_TOKEN")
    })

    # If the dataset is static - it does not contain any timestamp and
    # this flag must be set at true.
    self.add_timestamps_for_static = add_timestamps_for_static

    self.output_name = None

    super(BaseEstimator, self).__init__()

  def set_params(self, **params):
    self.configuration = params["configuration"]
    self.output_name = params["configuration"]["output"][0]

    # If the agent name has not been changed in the new configuration - use the base name
    # and add a random id to have a separated agent from the previous one
    # This allows to compute multiple craft ai agent in parallel during a GridSearch for example.
    if not "agent_name" in params["configuration"]:
      self.agent_name = "{}_id_{}".format(self.agent_name_base, rnd.randint(0, 100000))
    else:
      self.agent_name = params["configuration"]["agent_name"]
    return self

  def fit(self, input_x, target):
    # Add timestamps for the input and output dataframes
    if self.add_timestamps_for_static:
      input_x = CraftEstimator.add_timestamp(input_x)
      target = CraftEstimator.add_timestamp(pd.DataFrame(target))

    # Add the output in the input dataframe - the craft ai client takes both in an unique DF.
    input_x = input_x.assign(**{self.output_name: target})

    # Delete an agent if it has the same name to avoid conflicting data.
    self.craft_client.delete_agent(self.agent_name)

    # Create a new agent with its corresponding configuration
    self.craft_client.create_agent(self.configuration, self.agent_name)
    # Send all the dataset to the agent
    self.craft_client.add_operations(self.agent_name, input_x)

    return self

  def predict(self, input_x):
    # Add timestamps for the input dataframe
    if self.add_timestamps_for_static:
      last_timestamp = self.craft_client.get_agent(self.agent_name)["lastTimestamp"]
      input_x = CraftEstimator.add_timestamp(input_x, last_timestamp)
    else:
      last_timestamp = int(input_x.index.values[0]) // 10**9

    # Get the decision tree for all the sent data (corresponding
    # to the DT generated at the last timestamp)
    tree = self.craft_client.get_decision_tree(self.agent_name, last_timestamp)

    # Compute the decision of this DT on the input_x data
    predictions_df = self.craft_client.decide_from_contexts_df(tree, input_x)

    # Return the predictions
    return predictions_df["{}_predicted_value".format(self.output_name)].fillna("unknown")

  @staticmethod
  def add_timestamp(df, start=0):
    df.index = pd.date_range(start, periods=df.shape[0], freq="s", tz="UTC")
    return df

class CraftEstimatorClassifier(CraftEstimator, ClassifierMixin):
  def __init__(self,
               agent_name="agent_test",
               configuration=None,
               add_timestamps_for_static=False):
    super(CraftEstimatorRegressor, self).__init__(
      agent_name,
      configuration,
      add_timestamps_for_static)

class CraftEstimatorRegressor(CraftEstimator, RegressorMixin):
  def __init__(self,
               agent_name="agent_test",
               configuration=None,
               add_timestamps_for_static=False):
    super(CraftEstimatorRegressor, self).__init__(
      agent_name,
      configuration,
      add_timestamps_for_static)
