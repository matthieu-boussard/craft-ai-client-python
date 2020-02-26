import json
import os

from nose.tools import assert_equal, assert_true, assert_is_instance, assert_raises
from craft_ai import (
    errors,
    retrieve_decision_paths_from_tree,
    retrieve_decision_path_neighbors,
    retrieve_output_tree,
)


HERE = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(HERE, "data", "interpreter")

TREES_DIR = os.path.join(DATA_DIR, "decide", "trees")
PATH_DIR = os.path.join(DATA_DIR, "tree_computations_expectations", "get_paths")
NEIGHBOURS_DIR = os.path.join(
    DATA_DIR, "tree_computations_expectations", "get_neighbours"
)


def test_retrieve_output_tree_invalid_tree_1():
    path = os.path.join(DATA_DIR, "decide", "trees", "v1", "emptyArray.json")
    tree = None
    with open(path) as f:
        tree = json.load(f)
    assert_raises(errors.CraftAiError, retrieve_output_tree, tree)


def test_retrieve_output_tree_invalid_tree_2():
    path = os.path.join(DATA_DIR, "decide", "trees", "v1", "emptyObject.json")
    tree = None
    with open(path) as f:
        tree = json.load(f)
    assert_raises(errors.CraftAiError, retrieve_output_tree, tree)


def test_retrieve_output_tree_default_v2():
    path = os.path.join(DATA_DIR, "decide", "trees", "v2", "boolean_operator.json")
    tree = None
    with open(path) as f:
        tree = json.load(f)
    assert_is_instance(retrieve_output_tree(tree), dict)


def test_retrieve_output_tree_specific_output():
    path = os.path.join(DATA_DIR, "decide", "trees", "v2", "oneColor.json")
    tree = None
    with open(path) as f:
        tree = json.load(f)
    assert_is_instance(retrieve_output_tree(tree, "value"), dict)


def test_retrieve_output_tree_bad_output():
    path = os.path.join(DATA_DIR, "decide", "trees", "v2", "oneColor.json")
    tree = None
    with open(path) as f:
        tree = json.load(f)
    assert_raises(errors.CraftAiError, retrieve_output_tree, tree, "foo")


def test_retrieve_decision_paths_from_tree():
    """
    Testing expectations
        in data/interpreter/tree_computations_expectations/get_paths`/
    Trees located in data/interpreter/decide/trees/
    """
    for version in os.listdir(PATH_DIR):
        for filename in os.listdir(os.path.join(PATH_DIR, version)):
            # Loading the json tree
            tree = None
            with open(os.path.join(TREES_DIR, version, filename)) as f:
                tree = json.load(f)

            results = retrieve_decision_paths_from_tree(tree)

            # Loading the expectation for this tree
            with open(os.path.join(PATH_DIR, version, filename)) as f:
                expectation = json.load(f)

            assert_true(sorted(list(results)) == expectation)


def test_retrieve_decision_path_neighbors():
    """
    Testing expectations
        in data/interpreter/tree_computations_expectations/get_neighbours/
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
                result = retrieve_decision_path_neighbors(
                    tree=tree,
                    decision_path=expect["decision_path"],
                    max_depth=expect["max_depth"],
                    include_self=expect["include_self"],
                )
                assert_equal(sorted(expect["neighbours"]), sorted(result))
