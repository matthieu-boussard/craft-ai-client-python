import pandas as pd
import numpy as np
from numpy.random import randn

NB_OPERATIONS_TO_ADD = 1000

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

SIMPLE_AGENT_MANY_DATA = pd.DataFrame(
  randn(1000, 5),
  columns=["a", "b", "c", "d", "e"],
  index=pd.date_range("20130101", periods=1000, freq="T").tz_localize("Europe/Paris")
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
  "time_quantum": 100,
  "deactivate_missing_values": True,
}

COMPLEX_AGENT_CONFIGURATION_2 = {
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
  "output": ["a"],
  "time_quantum": 100,
  "deactivate_missing_values": True,
}

COMPLEX_AGENT_DATA = pd.DataFrame(
  [
    [1, "Pierre", "+02:00"],
    [2, "Paul"],
    [3],
    [4],
    [5, "Jacques"],
    [6],
    [7],
    [8, np.nan, "+01:00"],
    [9],
    [10]
  ],
  columns=["a", "b", "tz"],
  index=pd.date_range("20130101", periods=10, freq="D").tz_localize("Europe/Paris")
)

COMPLEX_AGENT_DATA_2 = pd.DataFrame(
  [
    [1, "Pierre", "+02:00", [8, 9]],
    [2, "Paul"],
    [3],
    [4],
    [5, "Jacques"],
    [6],
    [7],
    [8, np.nan, "+01:00", [1, 2, 3]],
    [9],
    [10]
  ],
  columns=["a", "b", "tz", "arrays"],
  index=pd.date_range("20130101", periods=10, freq="D").tz_localize("Europe/Paris")
)

DATETIME_AGENT_CONFIGURATION = {
  "context": {
    "a": {
      "type": "continuous"
    },
    "b": {
      "type": "enum"
    },
    "myTimeOfDay": {
      "type": "time_of_day"
    },
    "myCoolTimezone": {
      "type": "timezone"
    }
  },
  "output": ["b"],
  "time_quantum": 3600,
  "deactivate_missing_values": True
}

DATETIME_AGENT_DATA = pd.DataFrame(
  [
    [1, "Pierre", "+02:00"],
    [2, "Paul"],
    [3, np.nan, "+04:00"],
    [4],
    [5, "Jacques", "UTC"],
    [6],
    [7, np.nan, "+08:00"],
    [8],
    [9],
    [10, np.nan, "+10:00"]
  ],
  columns=["a", "b", "myCoolTimezone"],
  index=pd.date_range("20130101 00:00:00", periods=10, freq="H").tz_localize("UTC")
)
