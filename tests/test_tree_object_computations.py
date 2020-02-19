import json
import os

from nose.tools import assert_equal
from nose.tools import assert_true
from craft_ai.pandas.utils import get_paths
from craft_ai.pandas.utils import get_neighbours


HERE = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(HERE, "data", "interpreter")

TREES_DIR = os.path.join(DATA_DIR, "decide", "trees")
PATH_DIR = os.path.join(DATA_DIR, "tree_computations_expectations", "get_paths")
NEIGHBOURS_DIR = os.path.join(
    DATA_DIR, "tree_computations_expectations", "get_neighbours"
)


def test_path():
    """
     Testing expectations in data/interpreter/tree_computations_expectations/get_paths/
     Trees located in data/interpreter/decide/trees/
  """
    for version in os.listdir(PATH_DIR):
        for filename in os.listdir(os.path.join(PATH_DIR, version)):
            # Loading the json tree
            with open(os.path.join(TREES_DIR, version, filename)) as f:
                results = get_paths(json.load(f))
            # Loading the expectation for this tree
            with open(os.path.join(PATH_DIR, version, filename)) as f:
                expectation = json.load(f)

            assert_true(sorted(list(results)) == expectation)


def test_neighbours():
    """
     Testing expectations in data/interpreter/tree_computations_expectations/get_neighbours/
     Trees located in data/interpreter/decide/trees/
  """
    for version in os.listdir(NEIGHBOURS_DIR):
        for filename in os.listdir(os.path.join(NEIGHBOURS_DIR, version)):
            # Loading the json tree
            with open(os.path.join(TREES_DIR, version, filename)) as f:
                tree = json.load(f)

            # Loading expectations for this tree
            with open(os.path.join(NEIGHBOURS_DIR, version, filename)) as f:
                expectations = json.load(f)

            for expect in expectations:
                result = get_neighbours(
                    tree=tree,
                    decision_path=expect["decision_path"],
                    max_depth=expect["max_depth"],
                    include_self=expect["include_self"],
                )
                assert_equal(sorted(expect["neighbours"]), sorted(result))
