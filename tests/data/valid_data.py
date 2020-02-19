VALID_ID_TEMPLATE = "craft_ai_test_agent"
VALID_ID = VALID_ID_TEMPLATE + "_1"
VALID_ID_TWO = VALID_ID_TEMPLATE + "_2"
VALID_GENERATOR_ID = VALID_ID_TEMPLATE + "_gen1"
VALID_GENERATOR_ID_2 = VALID_ID_TEMPLATE + "_gen2"

VALID_CONTEXT = {
    "tz": {"type": "timezone"},
    "presence": {"type": "enum"},
    "lightIntensity": {"type": "continuous"},
    "lightbulbColor": {"type": "enum"},
}
VALID_OUTPUT = ["lightbulbColor"]
VALID_GENERATOR_FILTER = [VALID_ID]
VALID_TQ = 100
VALID_TREE_MAX_OPERATIONS = 50000
VALID_LEARNING_PERIOD = 6000000
VALID_CONFIGURATION = {
    "context": VALID_CONTEXT,
    "output": VALID_OUTPUT,
    "time_quantum": VALID_TQ,
}

VALID_GENERATOR_CONFIGURATION = {
    "context": VALID_CONTEXT,
    "output": VALID_OUTPUT,
    "time_quantum": VALID_TQ,
    "operations_as_events": True,
    "learning_period": VALID_LEARNING_PERIOD,
    "tree_max_operations": VALID_TREE_MAX_OPERATIONS,
    "filter": VALID_GENERATOR_FILTER,
}

VALID_LARGE_CONFIGURATION = {
    "context": {
        "e1": {"type": "enum"},
        "e2": {"type": "enum"},
        "e3": {"type": "enum"},
        "e4": {"type": "enum"},
        "c1": {"type": "continuous"},
        "c2": {"type": "continuous"},
        "c3": {"type": "continuous"},
        "c4": {"type": "continuous"},
        "time": {"type": "time_of_day", "is_generated": True},
        "day_of_week": {"type": "time_of_day", "is_generated": True},
        "tz": {"type": "timezone"},
    },
    "output": ["c4"],
    "time_quantum": 100,
    "learning_period": 3600 * 24 * 7,
}

VALID_TIMESTAMP = 1458741230
VALID_LAST_TIMESTAMP = 1458741735
VALID_OPERATIONS_SET = [
    {
        "timestamp": VALID_TIMESTAMP,
        "context": {
            "tz": "+02:00",
            "presence": "occupant",
            "lightIntensity": 1,
            "lightbulbColor": "#ffffff",
        },
    },
    {
        "timestamp": 1458741331,
        "context": {"presence": "player", "lightIntensity": 0.5},
    },
    {"timestamp": 1458741432, "context": {"presence": "none", "lightIntensity": 0}},
    {"timestamp": 1458741533, "context": {"presence": "occupant+player"}},
    {
        "timestamp": 1458741634,
        "context": {
            "tz": "+01:00",
            "presence": "occupant",
            "lightIntensity": 0.8,
            "lightbulbColor": "#f56fff",
        },
    },
    {
        "timestamp": VALID_LAST_TIMESTAMP,
        "context": {
            "presence": "player",
            "lightIntensity": 0.5,
            "lightbulbColor": "#fff596",
        },
    },
]
