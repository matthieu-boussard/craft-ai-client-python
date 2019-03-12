import pandas as pd
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

from numpy.random import randn
from nose.tools import assert_true

from craftai.sklearn_model import CraftEstimatorRegressor

from . import settings

AGENT_ID = "test_sklearn_" + settings.RUN_ID
def configuration_agent(max_depth=5):
  return {
    "agent_name": "{}_depth_{}".format(AGENT_ID, str(max_depth)),
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
    "output": ["e"],
    "time_quantum": 100,
    "tree_max_depth": max_depth
  }

SIMPLE_AGENT_DATA_TIMESTAMPS = pd.DataFrame(
  randn(300, 5),
  columns=["a", "b", "c", "d", "e"],
  index=pd.date_range("20130101", periods=300, freq="T").tz_localize("Europe/Paris")
)

G_S = GridSearchCV(CraftEstimatorRegressor(),
                   {"configuration": [configuration_agent(max_depth=3),
                                      configuration_agent(max_depth=6),
                                      configuration_agent(max_depth=9)]},
                   cv=TimeSeriesSplit(n_splits=5))

X_TRAIN = SIMPLE_AGENT_DATA_TIMESTAMPS[["a", "b", "c", "d"]]
Y_TRAIN = SIMPLE_AGENT_DATA_TIMESTAMPS[["e"]]

G_S.fit(X_TRAIN, Y_TRAIN)

assert_true(len(G_S.cv_results_.keys()) > 0)
