from craft_ai.pandas import CRAFTAI_PANDAS_ENABLED

if CRAFTAI_PANDAS_ENABLED:
    import unittest
    import pandas as pd
    from numpy.random import randn

    import craft_ai.pandas
    from craft_ai import errors as craft_err

    from . import settings
    from .utils import generate_entity_id
    from .data import valid_data, invalid_data, pandas_valid_data, pandas_invalid_data

    NB_AGENTS_TO_ADD_OPERATIONS = 3

    AGENT_ID_BASE = "add_agents_op_bulk"
    SIMPLE_AGENT_CONFIGURATION = pandas_valid_data.SIMPLE_AGENT_CONFIGURATION
    SIMPLE_AGENT_DATA = pandas_valid_data.SIMPLE_AGENT_DATA
    SIMPLE_AGENT_MANY_DATA = pandas_valid_data.SIMPLE_AGENT_MANY_DATA
    SIMPLE_AGENT_DATA_DICT = pandas_valid_data.SIMPLE_AGENT_DATA_DICT
    INVALID_DF_INDEX = pandas_invalid_data.INVALID_DF_INDEX
    SIMPLE_AGENT_MANY_DATA = pandas_valid_data.SIMPLE_AGENT_MANY_DATA

    @unittest.skipIf(CRAFTAI_PANDAS_ENABLED is False, "pandas is not enabled")
    class TestAddOperationsBulkSuccess(unittest.TestCase):
        """Checks that the client succeeds when adding operations to
        multiple agent(s) with OK input"""

        @classmethod
        def setUpClass(cls):
            cls.client = craft_ai.pandas.Client(settings.CRAFT_CFG)

        def setUp(self):
            self.agent_id1 = generate_entity_id(AGENT_ID_BASE + "BulkSuccess")
            self.agent_id2 = generate_entity_id(AGENT_ID_BASE + "BulkSuccess")
            self.client.delete_agent(self.agent_id1)
            self.client.delete_agent(self.agent_id2)
            self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, self.agent_id1)
            self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, self.agent_id2)

        def tearDown(self):
            self.client.delete_agent(self.agent_id1)
            self.client.delete_agent(self.agent_id2)

        def clean_up_agent(self, aid):
            # Makes sure that no agent with the standard ID remains
            self.client.delete_agent(aid)

        def clean_up_agents(self, aids):
            # Makes sure that no agent with the standard ID remains
            for aid in aids:
                self.clean_up_agent(aid)

        def test_add_agents_operations_bulk_with_df_operations(self):
            """add_agents_operations_bulk should succeed when given dataframe as input
            data, with correct `id`s and a correct df as `operations`.

            It should give a proper JSON response with a list containing dicts with
            'id' fields being the same as the one in parameters, 'message' fields
            being a string, 'status' fields being 201 and no 'error' field.
            """
            payload = [
                {"id": self.agent_id1, "operations": SIMPLE_AGENT_DATA},
                {"id": self.agent_id2, "operations": SIMPLE_AGENT_DATA},
            ]
            resp = self.client.add_agents_operations_bulk(payload)

            self.assertIsInstance(resp, list)
            self.assertEqual(resp[0].get("id"), self.agent_id1)
            self.assertEqual(resp[1].get("id"), self.agent_id2)
            self.assertEqual(resp[0].get("status"), 201)
            self.assertEqual(resp[1].get("status"), 201)
            self.assertTrue("message" in resp[0].keys())
            self.assertTrue("message" in resp[1].keys())

            self.addCleanup(self.clean_up_agents, [self.agent_id1, self.agent_id2])

        def test_add_agents_operations_bulk_with_dict_operations(self):
            """add_agents_operations_bulk should succeed when given dictionary as input
            data, with correct `id`s and a correct dictionary as `operations`.

            It should give a proper JSON response with a list containing dicts with
            'id' fields being the same as the one in parameters, 'message' fields
            being a string, 'status' fields being 201 and no 'error' field.
            """
            payload = [
                {"id": self.agent_id1, "operations": SIMPLE_AGENT_DATA_DICT},
                {"id": self.agent_id2, "operations": SIMPLE_AGENT_DATA_DICT},
            ]
            resp = self.client.add_agents_operations_bulk(payload)

            self.assertIsInstance(resp, list)
            self.assertEqual(resp[0].get("id"), self.agent_id1)
            self.assertEqual(resp[1].get("id"), self.agent_id2)
            self.assertEqual(resp[0].get("status"), 201)
            self.assertEqual(resp[1].get("status"), 201)
            self.assertTrue("message" in resp[0].keys())
            self.assertTrue("message" in resp[1].keys())

            self.addCleanup(self.clean_up_agents, [self.agent_id1, self.agent_id2])

        def test_add_agents_operations_bulk_with_mixed_input(self):
            """add_agents_operations_bulk should succeed when given correct input data,
            with correct `id`s and a correct dictionary or df as `operations`.

            It should give a proper JSON response with a list containing dicts with
            'id' fields being the same as the one in parameters, 'message' fields
            being a string, 'status' fields being 201 and no 'error' field.
            """
            payload = [
                {"id": self.agent_id1, "operations": SIMPLE_AGENT_DATA},
                {"id": self.agent_id2, "operations": SIMPLE_AGENT_DATA_DICT},
            ]
            resp = self.client.add_agents_operations_bulk(payload)

            self.assertIsInstance(resp, list)
            self.assertEqual(resp[0].get("id"), self.agent_id1)
            self.assertEqual(resp[1].get("id"), self.agent_id2)
            self.assertEqual(resp[0].get("status"), 201)
            self.assertEqual(resp[1].get("status"), 201)
            self.assertTrue("message" in resp[0].keys())
            self.assertTrue("message" in resp[1].keys())

            self.addCleanup(self.clean_up_agents, [self.agent_id1, self.agent_id2])

        @unittest.skip("Remove temporary due to beta performance issues")
        def test_add_agents_operations_bulk_with_many_operations(self):
            """add_agents_operations_bulk should succeed when given a big df as input
            data, with correct `id`s and a correct df as `operations`.

            It should give a proper JSON response with a list containing dicts with
            'id' fields being the same as the one in parameters, 'message' fields
            being a string, 'status' fields being 201 and no 'error' field.
            """
            payload = [
                {"id": self.agent_id1, "operations": SIMPLE_AGENT_MANY_DATA},
                {"id": self.agent_id2, "operations": SIMPLE_AGENT_MANY_DATA},
            ]
            resp = self.client.add_agents_operations_bulk(payload)

            self.assertIsInstance(resp, list)
            self.assertEqual(resp[0].get("id"), self.agent_id1)
            self.assertEqual(resp[1].get("id"), self.agent_id2)
            self.assertEqual(resp[0].get("status"), 201)
            self.assertEqual(resp[1].get("status"), 201)
            self.assertTrue("message" in resp[0].keys())
            self.assertTrue("message" in resp[1].keys())
            self.assertEqual(
                resp[0].get("added_operations_count"), len(SIMPLE_AGENT_MANY_DATA)
            )
            self.assertEqual(
                resp[1].get("added_operations_count"), len(SIMPLE_AGENT_MANY_DATA)
            )

            self.addCleanup(self.clean_up_agents, [self.agent_id1, self.agent_id2])

        def test_add_agents_operations_bulk_correct_order(self):
            """add_agents_operations_bulk should succeed when given two dataframe as input
            data which are in a chronological order with the same correct `id`s.

            It should give a proper JSON response with a list containing dicts with
            'id' fields being the same as the one in parameters, 'message' fields
            being a string, 'status' fields being 201 and no 'error' field.
            """
            data_part1 = SIMPLE_AGENT_DATA.iloc[: int(0.5 * len(SIMPLE_AGENT_DATA)), :]
            data_part2 = SIMPLE_AGENT_DATA.iloc[
                int(0.5 * len(SIMPLE_AGENT_DATA)) + 1 :, :
            ]

            payload = [
                {"id": self.agent_id1, "operations": data_part1},
                {"id": self.agent_id1, "operations": data_part2},
                {"id": self.agent_id2, "operations": data_part1},
                {"id": self.agent_id2, "operations": data_part2},
            ]
            resp = self.client.add_agents_operations_bulk(payload)

            self.assertIsInstance(resp, list)
            self.assertEqual(resp[0].get("id"), self.agent_id1)
            self.assertEqual(resp[0].get("added_operations_count"), len(data_part1))
            self.assertEqual(resp[1].get("id"), self.agent_id1)
            self.assertEqual(resp[1].get("added_operations_count"), len(data_part2))
            self.assertEqual(resp[2].get("id"), self.agent_id2)
            self.assertEqual(resp[2].get("added_operations_count"), len(data_part1))
            self.assertEqual(resp[3].get("id"), self.agent_id2)
            self.assertEqual(resp[3].get("added_operations_count"), len(data_part2))

            self.addCleanup(self.clean_up_agents, [self.agent_id1, self.agent_id2])

    @unittest.skipIf(CRAFTAI_PANDAS_ENABLED is False, "pandas is not enabled")
    class TestAddOperationsGroupAgentBulkSuccess(unittest.TestCase):
        """Checks that the client succeeds when adding operations to
        multiple agent(s) with OK input"""

        @classmethod
        def setUpClass(cls):
            cls.client = craft_ai.pandas.Client(settings.CRAFT_CFG)

        def setUp(self):
            self.agents = [
                generate_entity_id(AGENT_ID_BASE + "GroupBulkSuccess")
                for i in range(NB_AGENTS_TO_ADD_OPERATIONS)
            ]
            for agent_id in self.agents:
                self.client.delete_agent(agent_id)
                self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, agent_id)

        def tearDown(self):
            for agent_id in self.agents:
                self.client.delete_agent(agent_id)

        def clean_up_agent(self, aid):
            # Makes sure that no agent with the standard ID remains
            self.client.delete_agent(aid)

        def clean_up_agents(self, aids):
            # Makes sure that no agent with the standard ID remains
            for aid in aids:
                self.clean_up_agent(aid)

        def test_add_agents_operations_bulk_group_agents(self):
            """add_agents_operations_bulk should succeed when given many agents to add
            operations to, with correct `id`s and a correct df as `operations`.

            It should give a proper JSON response with a list containing dicts with
            'id' fields being the same as the one in parameters, 'message' fields
            being a string, 'status' fields being 201 and no 'error' field.
            """
            payload = []
            for agent_id in self.agents:
                payload.append({"id": agent_id, "operations": SIMPLE_AGENT_DATA})
            response = self.client.add_agents_operations_bulk(payload)

            for i, resp in enumerate(response):
                self.assertEqual(resp.get("id"), self.agents[i])
                self.assertEqual(resp.get("status"), 201)
                self.assertTrue("message" in resp.keys())
                self.assertEqual(resp["added_operations_count"], len(SIMPLE_AGENT_DATA))

            self.addCleanup(self.clean_up_agents, self.agents)

    @unittest.skipIf(CRAFTAI_PANDAS_ENABLED is False, "pandas is not enabled")
    class TestAddOperationsBulkFailure(unittest.TestCase):
        """Checks that the client fail when adding operations to
        multiple agent(s) with incorrect input"""

        @classmethod
        def setUpClass(cls):
            cls.client = craft_ai.pandas.Client(settings.CRAFT_CFG)

        def clean_up_agent(self, aid):
            # Makes sure that no agent with the standard ID remains
            self.client.delete_agent(aid)

        def clean_up_agents(self, aids):
            # Makes sure that no agent with the standard ID remains
            for aid in aids:
                self.clean_up_agent(aid)

        def test_add_agents_operations_bulk_invalid_agent_id(self):
            """add_agents_operations_bulk should fail when given non-string/empty ID.

            It should raise an error upon request for operations posting
            for all agents with an ID that is not of type string, since agent IDs
            should always be strings.
            """
            payload = []
            for empty_id in invalid_data.UNDEFINED_KEY:
                payload.append(
                    {
                        "id": invalid_data.UNDEFINED_KEY[empty_id],
                        "operations": SIMPLE_AGENT_DATA,
                    }
                )

            self.assertRaises(
                craft_err.CraftAiBadRequestError,
                self.client.add_agents_operations_bulk,
                payload,
            )

        def test_add_agents_operations_bulk_undefined_operations(self):
            """add_agents_operations_bulk should fail when given some undefined operations set.

            It should raise an error upon request for operations posting for all agents
            with invalid operations set.
            """
            payload = []
            agents_lst = []
            for i, invalid_operation_set in enumerate(invalid_data.UNDEFINED_KEY):
                new_agent_id = generate_entity_id(
                    "test_add_agents_operations_bulk_undefined_operations"
                )
                self.client.delete_agent(new_agent_id)
                self.client.create_agent(valid_data.VALID_CONFIGURATION, new_agent_id)
                agents_lst.append(new_agent_id)
                payload.append(
                    {"id": new_agent_id, "operations": invalid_operation_set}
                )

            self.assertRaises(
                craft_err.CraftAiBadRequestError,
                self.client.add_agents_operations_bulk,
                payload,
            )

            self.addCleanup(self.clean_up_agents, agents_lst)

        def test_add_agents_operations_bulk_invalid_operations(self):
            """add_agents_operations_bulk should fail when given some invalid operations set.

            It should raise an error upon request for operations posting for all agents
            with invalid operations set.
            """
            payload = []
            agents_lst = []
            for i, invalid_operation_set in enumerate(invalid_data.INVALID_OPS_SET):
                new_agent_id = generate_entity_id(
                    "test_add_agents_operations_bulk_invalid_operations"
                )
                self.client.delete_agent(new_agent_id)
                self.client.create_agent(valid_data.VALID_CONFIGURATION, new_agent_id)
                agents_lst.append(new_agent_id)
                payload.append(
                    {"id": new_agent_id, "operations": invalid_operation_set}
                )

            self.assertRaises(
                craft_err.CraftAiBadRequestError,
                self.client.add_agents_operations_bulk,
                payload,
            )

            self.addCleanup(self.clean_up_agents, agents_lst)

        def test_add_agents_operations_bulk_unexpected_property(self):
            """add_agents_operations_bulk should fail when given a df with unexpected property
            which is not in the context.

            It should raise an error upon request for operations posting for all agents
            with invalid operations set.
            """
            agent_id = generate_entity_id(
                "test_add_agents_operations_bulk_unexpected_property"
            )
            self.client.delete_agent(agent_id)
            self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, agent_id)

            df = pd.DataFrame(
                randn(300, 6),
                columns=["a", "b", "c", "d", "e", "f"],
                index=pd.date_range("20130101", periods=300, freq="T").tz_localize(
                    "Europe/Paris"
                ),
            )
            payload = [{"id": agent_id, "operations": df}]

            self.assertRaises(
                craft_err.CraftAiBadRequestError,
                self.client.add_agents_operations_bulk,
                payload,
            )

            self.addCleanup(self.clean_up_agent, agent_id)

        def test_add_agents_operations_bulk_invalid_index(self):
            """add_agents_operations_bulk should fail when given a df with invalid index.

            It should raise an error upon request for operations posting for all agents
            with invalid index in the operations set.
            """
            list_agents = []
            payload = []
            for i, index in enumerate(INVALID_DF_INDEX):
                agent_id = generate_entity_id(
                    "test_add_agents_operations_bulk_invalid_index"
                )
                self.client.delete_agent(agent_id)
                self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, agent_id)

                df = pd.DataFrame(
                    randn(300, 6),
                    columns=["a", "b", "c", "d", "e", "f"],
                    index=pd.date_range("20130101", periods=300, freq="T").tz_localize(
                        "Europe/Paris"
                    ),
                )
                payload.append({"id": agent_id, "operations": df})
                list_agents.append(agent_id)

            self.assertRaises(
                craft_err.CraftAiBadRequestError,
                self.client.add_agents_operations_bulk,
                payload,
            )

            self.addCleanup(self.clean_up_agents, list_agents)

        def test_add_agents_operations_bulk_wrong_order(self):
            """add_agents_operations_bulk should fails when the DataFrame are in a non
            chrological order.

            It should raise an error upon request for operations posting when an agent
            appears multiple time in the same bulk and the operations are not in
            chronological order.
            """
            agent_id = generate_entity_id("test_add_agents_operations_bulk_wrong_order")
            self.client.delete_agent(agent_id)
            self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, agent_id)

            data_part1 = SIMPLE_AGENT_DATA.iloc[: int(0.5 * len(SIMPLE_AGENT_DATA)), :]
            data_part2 = SIMPLE_AGENT_DATA.iloc[
                int(0.5 * len(SIMPLE_AGENT_DATA)) + 1 :, :
            ]

            payload = [
                {"id": agent_id, "operations": data_part2},
                {"id": agent_id, "operations": data_part1},
            ]
            self.assertRaises(
                craft_err.CraftAiBadRequestError,
                self.client.add_agents_operations_bulk,
                payload,
            )

            self.addCleanup(self.clean_up_agent, agent_id)

    @unittest.skipIf(CRAFTAI_PANDAS_ENABLED is False, "pandas is not enabled")
    class TestAddOperationsBulkSomeFailure(unittest.TestCase):
        """Checks that the client succeed when adding operations to
        an/multiple agent(s) with bad input and an/multiple agent(s)
        with valid input"""

        @classmethod
        def setUpClass(cls):
            cls.client = craft_ai.pandas.Client(settings.CRAFT_CFG)

        def setUp(self):
            self.agent_id = generate_entity_id(
                "test_add_agents_operations_bulk_some_failure"
            )
            self.client.delete_agent(self.agent_id)
            self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, self.agent_id)

        def tearDown(self):
            self.client.delete_agent(self.agent_id)

        def clean_up_agent(self, aid):
            # Makes sure that no agent with the standard ID remains
            self.client.delete_agent(aid)

        def test_add_agents_operations_bulk_some_invalid_agent_id(self):
            """add_agents_operations_bulk should succeed when given some non-string/empty ID
            and some valid ID.

            It should give a proper JSON response with a list containing dicts.
            The ones having valid ids have the `id` field being the same as the one given
            as a parameter and message field being a string.
            The ones having valid ids doesn't have a dict associated.
            """
            payload = [{"id": self.agent_id, "operations": SIMPLE_AGENT_DATA}]
            for empty_id in invalid_data.UNDEFINED_KEY:
                payload.append(
                    {
                        "id": invalid_data.UNDEFINED_KEY[empty_id],
                        "operations": SIMPLE_AGENT_DATA,
                    }
                )

                self.addCleanup(self.clean_up_agent, self.agent_id)

            def test_add_agents_operations_bulk_invalid_index(self):
                """add_agents_operations_bulk should fail when given a df with invalid index.

                It should raise an error upon request for operations posting for all agents
                with invalid index in the operations set.
                """
                list_agents = []
                payload = []
                for i, index in enumerate(INVALID_DF_INDEX):
                    agent_id = generate_entity_id(
                        "test_add_agents_operations_bulk_invalid_index"
                    )
                    self.client.delete_agent(agent_id)
                    self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, agent_id)

                    df = pd.DataFrame(
                        randn(300, 5), columns=["a", "b", "c", "d", "e"], index=index
                    )
                    payload.append({"id": agent_id, "operations": df})
                    list_agents.append(agent_id)

                self.assertRaises(
                    craft_err.CraftAiBadRequestError,
                    self.client.add_agents_operations_bulk,
                    payload,
                )

                self.addCleanup(self.clean_up_agents, list_agents)

            def test_add_agents_operations_bulk_wrong_order(self):
                """add_agents_operations_bulk should fails when the DataFrame are in a non
                chrological order.

                It should raise an error upon request for operations posting when an agent
                appears multiple time in the same bulk and the operations are not in
                chronological order.
                """
                agent_id = generate_entity_id(
                    "test_add_agents_operations_bulk_wrong_order"
                )
                self.client.delete_agent(agent_id)
                self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, agent_id)

                data_part1 = SIMPLE_AGENT_DATA.iloc[
                    : int(0.5 * len(SIMPLE_AGENT_DATA)), :
                ]
                data_part2 = SIMPLE_AGENT_DATA.iloc[
                    int(0.5 * len(SIMPLE_AGENT_DATA)) + 1 :, :
                ]

                payload = [
                    {"id": agent_id, "operations": data_part2},
                    {"id": agent_id, "operations": data_part1},
                ]
                self.assertRaises(
                    craft_err.CraftAiBadRequestError,
                    self.client.add_agents_operations_bulk,
                    payload,
                )

                self.addCleanup(self.clean_up_agent, agent_id)

        @unittest.skipIf(CRAFTAI_PANDAS_ENABLED is False, "pandas is not enabled")
        class TestAddOperationsBulkSomeFailure(unittest.TestCase):
            """Checks that the client succeed when adding operations to
            an/multiple agent(s) with bad input and an/multiple agent(s)
            with valid input"""

            @classmethod
            def setUpClass(cls):
                cls.client = craft_ai.pandas.Client(settings.CRAFT_CFG)

            def setUp(self):
                self.agent_id = generate_entity_id(
                    "test_add_agents_operations_bulk_some_failure"
                )
                self.client.delete_agent(self.agent_id)
                self.client.create_agent(SIMPLE_AGENT_CONFIGURATION, self.agent_id)

            def tearDown(self):
                self.client.delete_agent(self.agent_id)

            def clean_up_agent(self, aid):
                # Makes sure that no agent with the standard ID remains
                self.client.delete_agent(aid)

            def test_add_agents_operations_bulk_some_invalid_agent_id(self):
                """add_agents_operations_bulk should succeed when given some non-string/empty ID
            and some valid ID.

            It should give a proper JSON response with a list containing dicts.
            The ones having valid ids have the `id` field being the same as the one given
            as a parameter and message field being a string.
            The ones having valid ids doesn't have a dict associated.
            """
                payload = [{"id": self.agent_id, "operations": SIMPLE_AGENT_DATA}]
                for empty_id in invalid_data.UNDEFINED_KEY:
                    payload.append(
                        {
                            "id": invalid_data.UNDEFINED_KEY[empty_id],
                            "operations": SIMPLE_AGENT_DATA,
                        }
                    )

                resp = self.client.add_agents_operations_bulk(payload)

                self.assertIsInstance(resp, list)
                self.assertEqual(resp[0].get("id"), self.agent_id)
                self.assertTrue("message" in resp[0].keys())
                self.assertFalse("error" in resp[0].keys())
                self.assertTrue(len(resp) == 1)

                self.addCleanup(self.clean_up_agent, self.agent_id)
