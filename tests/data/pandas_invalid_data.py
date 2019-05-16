import pandas as pd

INVALID_DF_INDEX = [                      # Should be a list of different timestamp
  range(300),                             # List of int
  [pd.Timestamp(2017, 1, 1, 12)]*300,     # List of the same timestamp
  [None]*300,                             # List of null
  [item * 0.001 for item in range(1, 301)]# List of float
]
