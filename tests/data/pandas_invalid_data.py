import pandas as pd

NB_OPERATIONS = 300

INVALID_DF_INDEX = [  # Should be a list of different timestamp
    range(NB_OPERATIONS),  # List of int
    [pd.Timestamp(2017, 1, 1, 12)] * NB_OPERATIONS,  # List of the same timestamp
    [None] * NB_OPERATIONS,  # List of null
    [(item + 1) * 0.001 for item in range(NB_OPERATIONS)],  # List of float
]
