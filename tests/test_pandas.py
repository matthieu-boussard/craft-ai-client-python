from craft_ai.pandas import CRAFTAI_PANDAS_ENABLED

if CRAFTAI_PANDAS_ENABLED:
    import copy
    import pandas as pd

    from numpy.random import randn
    from nose.tools import (
        assert_equal,
        assert_not_equal,
        assert_raises,
        with_setup,
        assert_true,
        assert_is_instance,
    )

    import craft_ai.pandas

    from .data import pandas_valid_data, valid_data
    from .utils import generate_entity_id
    from . import settings

    AGENT_ID = generate_entity_id("test_pandas_agent_1")
    AGENT_ID_2 = generate_entity_id("test_pandas_agent_2")
    GENERATOR_ID = generate_entity_id("test_pandas_generator")

    SIMPLE_AGENT_CONFIGURATION = pandas_valid_data.SIMPLE_AGENT_CONFIGURATION
    SIMPLE_AGENT_DATA = pandas_valid_data.SIMPLE_AGENT_DATA
    COMPLEX_AGENT_CONFIGURATION = pandas_valid_data.COMPLEX_AGENT_CONFIGURATION
    COMPLEX_AGENT_CONFIGURATION_2 = pandas_valid_data.COMPLEX_AGENT_CONFIGURATION_2
    COMPLEX_AGENT_DATA = pandas_valid_data.COMPLEX_AGENT_DATA
    COMPLEX_AGENT_DATA_2 = pandas_valid_data.COMPLEX_AGENT_DATA_2
    DATETIME_AGENT_CONFIGURATION = pandas_valid_data.DATETIME_AGENT_CONFIGURATION
    DATETIME_AGENT_DATA = pandas_valid_data.DATETIME_AGENT_DATA
    MISSING_AGENT_CONFIGURATION = pandas_valid_data.MISSING_AGENT_CONFIGURATION
    MISSING_AGENT_DATA = pandas_valid_data.MISSING_AGENT_DATA
    MISSING_AGENT_DATA_DECISION = pandas_valid_data.MISSING_AGENT_DATA_DECISION
    INVALID_PYTHON_IDENTIFIER_CONFIGURATION = (
        pandas_valid_data.INVALID_PYTHON_IDENTIFIER_CONFIGURATION
    )
    INVALID_PYTHON_IDENTIFIER_DATA = pandas_valid_data.INVALID_PYTHON_IDENTIFIER_DATA
    INVALID_PYTHON_IDENTIFIER_DECISION = (
        pandas_valid_data.INVALID_PYTHON_IDENTIFIER_DECISION
    )

    CLIENT = craft_ai.pandas.Client(settings.CRAFT_CFG)

    def setup_simple_agent():
        CLIENT.delete_agent(AGENT_ID)
        CLIENT.create_agent(SIMPLE_AGENT_CONFIGURATION, AGENT_ID)

    def setup_complex_agent():
        CLIENT.delete_agent(AGENT_ID)
        CLIENT.create_agent(COMPLEX_AGENT_CONFIGURATION, AGENT_ID)

    def setup_agent_w_operations():
        CLIENT.delete_agent(AGENT_ID)
        CLIENT.create_agent(valid_data.VALID_CONFIGURATION, AGENT_ID)
        CLIENT.add_operations(AGENT_ID, valid_data.VALID_OPERATIONS_SET)

    def setup_complex_agent_2():
        CLIENT.delete_agent(AGENT_ID)
        CLIENT.create_agent(COMPLEX_AGENT_CONFIGURATION_2, AGENT_ID)

    def setup_datetime_agent():
        CLIENT.delete_agent(AGENT_ID)
        CLIENT.create_agent(DATETIME_AGENT_CONFIGURATION, AGENT_ID)

    def setup_missing_agent():
        CLIENT.delete_agent(AGENT_ID)
        CLIENT.create_agent(MISSING_AGENT_CONFIGURATION, AGENT_ID)

    def setup_invalid_python_identifier():
        CLIENT.delete_agent(AGENT_ID)
        CLIENT.create_agent(INVALID_PYTHON_IDENTIFIER_CONFIGURATION, AGENT_ID)

    def setup_generator_with_agent_with_operations():
        CLIENT.delete_agent(AGENT_ID)
        CLIENT.delete_agent(AGENT_ID_2)
        CLIENT.delete_generator(GENERATOR_ID)
        CLIENT.create_agent(valid_data.VALID_CONFIGURATION, AGENT_ID)
        CLIENT.create_agent(valid_data.VALID_CONFIGURATION, AGENT_ID_2)
        CLIENT.add_operations(AGENT_ID, valid_data.VALID_OPERATIONS_SET)
        CLIENT.add_operations(AGENT_ID_2, valid_data.VALID_OPERATIONS_SET)
        generator_configuration = copy.deepcopy(
            valid_data.VALID_GENERATOR_CONFIGURATION
        )
        generator_configuration["filter"] = [AGENT_ID, AGENT_ID_2]
        CLIENT.create_generator(generator_configuration, GENERATOR_ID)

    def teardown():
        CLIENT.delete_agent(AGENT_ID)
        CLIENT.delete_agent(AGENT_ID_2)
        CLIENT.delete_generator(GENERATOR_ID)

    @with_setup(setup_simple_agent, teardown)
    def test_add_operations_df_bad_index():
        df = pd.DataFrame(randn(10, 5), columns=["a", "b", "c", "d", "e"])

        assert_raises(
            craft_ai.pandas.errors.CraftAiBadRequestError,
            CLIENT.add_operations,
            AGENT_ID,
            df,
        )

    @with_setup(setup_simple_agent, teardown)
    def test_add_operations_df():
        CLIENT.add_operations(AGENT_ID, SIMPLE_AGENT_DATA)
        agent = CLIENT.get_agent(AGENT_ID)
        assert_equal(
            agent["firstTimestamp"],
            SIMPLE_AGENT_DATA.first_valid_index().value // 10 ** 9,
        )
        assert_equal(
            agent["lastTimestamp"],
            SIMPLE_AGENT_DATA.last_valid_index().value // 10 ** 9,
        )

    @with_setup(setup_complex_agent, teardown)
    def test_add_operations_df_complex_agent():
        CLIENT.add_operations(AGENT_ID, COMPLEX_AGENT_DATA)
        agent = CLIENT.get_agent(AGENT_ID)
        assert_equal(
            agent["firstTimestamp"],
            COMPLEX_AGENT_DATA.first_valid_index().value // 10 ** 9,
        )
        assert_equal(
            agent["lastTimestamp"],
            COMPLEX_AGENT_DATA.last_valid_index().value // 10 ** 9,
        )

    @with_setup(setup_missing_agent, teardown)
    def test_add_operations_df_missing_agent():
        CLIENT.add_operations(AGENT_ID, MISSING_AGENT_DATA)
        agent = CLIENT.get_agent(AGENT_ID)
        assert_equal(
            agent["firstTimestamp"],
            MISSING_AGENT_DATA.first_valid_index().value // 10 ** 9,
        )
        assert_equal(
            agent["lastTimestamp"],
            MISSING_AGENT_DATA.last_valid_index().value // 10 ** 9,
        )

    @with_setup(setup_simple_agent, teardown)
    def test_add_operations_df_unexpected_property():
        df = pd.DataFrame(
            randn(300, 6),
            columns=["a", "b", "c", "d", "e", "f"],
            index=pd.date_range("20130101", periods=300, freq="T").tz_localize(
                "Europe/Paris"
            ),
        )

        assert_raises(
            craft_ai.pandas.errors.CraftAiBadRequestError,
            CLIENT.add_operations,
            AGENT_ID,
            df,
        )

    @with_setup(setup_complex_agent, teardown)
    def test_add_operations_df_without_tz():
        test_df = COMPLEX_AGENT_DATA.drop(columns="tz")
        CLIENT.add_operations(AGENT_ID, test_df)
        agent = CLIENT.get_agent(AGENT_ID)
        assert_equal(
            agent["firstTimestamp"],
            COMPLEX_AGENT_DATA.first_valid_index().value // 10 ** 9,
        )
        assert_equal(
            agent["lastTimestamp"],
            COMPLEX_AGENT_DATA.last_valid_index().value // 10 ** 9,
        )

    def setup_simple_agent_with_data():
        setup_simple_agent()
        CLIENT.add_operations(AGENT_ID, SIMPLE_AGENT_DATA)

    @with_setup(setup_simple_agent_with_data, teardown)
    def test_get_operations_list_df():
        df = CLIENT.get_operations_list(AGENT_ID)

        assert_equal(len(df), 300)
        assert_equal(len(df.dtypes), 5)
        assert_equal(
            df.first_valid_index(),
            pd.Timestamp("2013-01-01 00:00:00", tz="Europe/Paris"),
        )
        assert_equal(
            df.last_valid_index(),
            pd.Timestamp("2013-01-01 04:59:00", tz="Europe/Paris"),
        )

    @with_setup(setup_simple_agent_with_data, teardown)
    def test_get_state_history_df():
        df = CLIENT.get_state_history(AGENT_ID)

        assert_equal(len(df), 180)
        assert_equal(len(df.dtypes), 5)
        assert_equal(
            df.first_valid_index(),
            pd.Timestamp("2013-01-01 00:00:00", tz="Europe/Paris"),
        )
        assert_equal(
            df.last_valid_index(),
            pd.Timestamp("2013-01-01 04:58:20", tz="Europe/Paris"),
        )

    def setup_complex_agent_with_data():
        setup_complex_agent()
        CLIENT.add_operations(AGENT_ID, COMPLEX_AGENT_DATA)

    @with_setup(setup_complex_agent_with_data, teardown)
    def test_get_operations_list_df_complex_agent():
        df = CLIENT.get_operations_list(AGENT_ID)

        assert_equal(
            df["b"].notnull().tolist(),
            [True, True, False, False, True, False, False, False, False, False],
        )

        assert_equal(len(df), 10)
        assert_equal(len(df.dtypes), 3)
        assert_equal(
            df.first_valid_index(),
            pd.Timestamp("2013-01-01 00:00:00", tz="Europe/Paris"),
        )
        assert_equal(
            df.last_valid_index(),
            pd.Timestamp("2013-01-10 00:00:00", tz="Europe/Paris"),
        )

    @with_setup(setup_complex_agent_with_data, teardown)
    def test_decide_from_contexts_df():
        tree = CLIENT.get_decision_tree(
            AGENT_ID, COMPLEX_AGENT_DATA.last_valid_index().value // 10 ** 9
        )
        test_df = COMPLEX_AGENT_DATA
        test_df_copy = test_df.copy(deep=True)
        df = CLIENT.decide_from_contexts_df(tree, test_df)

        assert_equal(len(df), 10)
        assert_equal(len(df.dtypes), 6)
        assert_true(test_df.equals(test_df_copy))
        assert_equal(
            df.first_valid_index(),
            pd.Timestamp("2013-01-01 00:00:00", tz="Europe/Paris"),
        )
        assert_equal(
            df.last_valid_index(),
            pd.Timestamp("2013-01-10 00:00:00", tz="Europe/Paris"),
        )

        # Also works as before, with a plain context
        output = CLIENT.decide(tree, {"a": 1, "tz": "+02:00"})

        assert_equal(output["output"]["b"]["predicted_value"], "Pierre")

    @with_setup(setup_complex_agent_with_data, teardown)
    def test_decide_from_contexts_df_zero_rows():
        tree = CLIENT.get_decision_tree(
            AGENT_ID, COMPLEX_AGENT_DATA.last_valid_index().value // 10 ** 9
        )
        test_df = COMPLEX_AGENT_DATA.iloc[:0, :]
        test_df_copy = test_df.copy(deep=True)
        df = CLIENT.decide_from_contexts_df(tree, test_df)

        assert_true(isinstance(df, pd.DataFrame))
        assert_equal(len(df), 0)
        assert_true(test_df.equals(test_df_copy))

    def setup_complex_agent_2_with_data():
        setup_complex_agent_2()
        CLIENT.add_operations(AGENT_ID, COMPLEX_AGENT_DATA)

    @with_setup(setup_complex_agent_2_with_data, teardown)
    def test_decide_from_contexts_df_null_decisions():
        tree = CLIENT.get_decision_tree(
            AGENT_ID, COMPLEX_AGENT_DATA.last_valid_index().value // 10 ** 9
        )

        test_df = pd.DataFrame(
            [["Jean-Pierre", "+02:00"], ["Paul"]],
            columns=["b", "tz"],
            index=pd.date_range("20130201", periods=2, freq="D").tz_localize(
                "Europe/Paris"
            ),
        )
        test_df_copy = test_df.copy(deep=True)

        df = CLIENT.decide_from_contexts_df(tree, test_df)
        assert_equal(len(df), 2)
        assert_true(test_df.equals(test_df_copy))

        assert pd.notnull(df["a_predicted_value"][0])
        assert pd.notnull(df["a_predicted_value"][1])

    def setup_complex_agent_3_with_data():
        setup_complex_agent_2()
        CLIENT.add_operations(AGENT_ID, COMPLEX_AGENT_DATA_2)

    @with_setup(setup_complex_agent_3_with_data, teardown)
    def test_decide_from_contexts_df_with_array():
        tree = CLIENT.get_decision_tree(
            AGENT_ID, COMPLEX_AGENT_DATA_2.last_valid_index().value // 10 ** 9
        )

        test_df = pd.DataFrame(
            [["Jean-Pierre", "+02:00"], ["Paul"]],
            columns=["b", "tz"],
            index=pd.date_range("20130201", periods=2, freq="D").tz_localize(
                "Europe/Paris"
            ),
        )
        test_df_copy = test_df.copy(deep=True)

        df = CLIENT.decide_from_contexts_df(tree, test_df)
        assert_equal(len(df), 2)
        assert_true(test_df.equals(test_df_copy))
        assert pd.notnull(df["a_predicted_value"][0])
        assert pd.notnull(df["a_predicted_value"][1])

    def setup_missing_agent_with_data():
        setup_missing_agent()
        CLIENT.add_operations(AGENT_ID, MISSING_AGENT_DATA)

    @with_setup(setup_missing_agent_with_data, teardown)
    def test_decide_from_missing_contexts_df():
        tree = CLIENT.get_decision_tree(
            AGENT_ID, MISSING_AGENT_DATA.last_valid_index().value // 10 ** 9, "2"
        )

        df = CLIENT.decide_from_contexts_df(tree, MISSING_AGENT_DATA_DECISION)

        assert_equal(len(df), 2)
        assert_equal(
            df.first_valid_index(),
            pd.Timestamp("2013-01-01 00:00:00", tz="Europe/Paris"),
        )
        assert_equal(
            df.last_valid_index(),
            pd.Timestamp("2013-01-02 00:00:00", tz="Europe/Paris"),
        )

        # Also works as before, with a context containing an optional value
        output = CLIENT.decide(tree, {"b": {}, "tz": "+02:00"})

        assert pd.notnull(output["output"]["a"]["predicted_value"])

        # Also works as before, with a context containing a missing value
        output = CLIENT.decide(tree, {"b": None, "tz": "+02:00"})

        assert pd.notnull(output["output"]["a"]["predicted_value"])

    def setup_datetime_agent_with_data():
        setup_datetime_agent()
        CLIENT.add_operations(AGENT_ID, DATETIME_AGENT_DATA)

    @with_setup(setup_datetime_agent_with_data, teardown)
    def test_datetime_state_history_df():
        df = CLIENT.get_state_history(AGENT_ID)

        assert_equal(len(df), 10)
        assert_equal(len(df.dtypes), 4)
        assert_equal(df["myTimeOfDay"].tolist(), [2, 3, 6, 7, 4, 5, 14, 15, 16, 19])

    # This test is commented because of the current non-deterministic behavior of craft ai.
    # @with_setup(setup_datetime_agent_with_data, teardown)
    # def test_datetime_decide_from_contexts_df():
    #   tree = CLIENT.get_decision_tree(AGENT_ID,
    #                                   DATETIME_AGENT_DATA.last_valid_index().value // 10 ** 9)

    #   test_df = pd.DataFrame(
    #     [
    #       [1],
    #       [3],
    #       [7]
    #     ],
    #     columns=["a"],
    #     index=pd.date_range("20130101 00:00:00",
    #                         periods=3,
    #                         freq="H").tz_localize("Asia/Shanghai"))
    #   test_df_copy = test_df.copy(deep=True)

    #   df = CLIENT.decide_from_contexts_df(tree, test_df)
    #   assert_equal(len(df), 3)
    #   assert_equal(len(df.dtypes), 6)
    #   assert_equal(df["b_predicted_value"].tolist(), ["Pierre", "Paul", "Jacques"])
    #   assert_true(test_df.equals(test_df_copy))

    @with_setup(setup_simple_agent_with_data, teardown)
    def test_tree_visualization():
        tree1 = CLIENT.get_decision_tree(
            AGENT_ID, DATETIME_AGENT_DATA.last_valid_index().value // 10 ** 9
        )
        craft_ai.pandas.utils.create_tree_html(tree1, "", "constant", None, 500)

    def setup_agent_with_data_invalid_identifier():
        setup_invalid_python_identifier()
        CLIENT.add_operations(AGENT_ID, INVALID_PYTHON_IDENTIFIER_DATA)

    @with_setup(setup_agent_with_data_invalid_identifier, teardown)
    def test_decide_from_python_invalid_identifier():
        tree = CLIENT.get_decision_tree(
            AGENT_ID,
            INVALID_PYTHON_IDENTIFIER_DATA.last_valid_index().value // 10 ** 9,
            "2",
        )

        test_df = INVALID_PYTHON_IDENTIFIER_DECISION.copy(deep=True)
        df = CLIENT.decide_from_contexts_df(tree, test_df)
        assert_equal(len(df), 3)
        assert_equal(len(df.dtypes), 8)

    @with_setup(setup_agent_w_operations, teardown)
    def test_get_decision_tree_with_pdtimestamp():
        # test if we get the same decision tree
        decision_tree = CLIENT.get_decision_tree(
            AGENT_ID, pd.Timestamp(valid_data.VALID_TIMESTAMP, unit="s", tz="UTC")
        )
        ground_truth_decision_tree = CLIENT.get_decision_tree(
            AGENT_ID, valid_data.VALID_TIMESTAMP
        )
        assert_is_instance(decision_tree, dict)
        assert_not_equal(decision_tree.get("_version"), None)
        assert_not_equal(decision_tree.get("configuration"), None)
        assert_not_equal(decision_tree.get("trees"), None)
        assert_equal(decision_tree, ground_truth_decision_tree)

    @with_setup(setup_generator_with_agent_with_operations, teardown)
    def test_get_generator_decision_tree_with_pdtimestamp():
        # test if we get the same decision tree
        decision_tree = CLIENT.get_generator_decision_tree(
            GENERATOR_ID, pd.Timestamp(valid_data.VALID_TIMESTAMP, unit="s", tz="UTC")
        )
        ground_truth_decision_tree = CLIENT.get_generator_decision_tree(
            GENERATOR_ID, valid_data.VALID_TIMESTAMP
        )
        assert_is_instance(decision_tree, dict)
        assert_not_equal(decision_tree.get("_version"), None)
        assert_not_equal(decision_tree.get("configuration"), None)
        assert_not_equal(decision_tree.get("trees"), None)
        assert_equal(decision_tree, ground_truth_decision_tree)
