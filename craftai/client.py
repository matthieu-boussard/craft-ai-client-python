import requests
import json
import six

from craftai import helpers

from craftai.errors import *


class CraftAIClient(object):
    """docstring for CraftAIClient"""
    def __init__(self, cfg):
        self._base_url = ""
        self._headers = {}

        try:
            self.config = cfg
        except (CraftAICredentialsError, CraftAIBadRequestError) as e:
            raise e

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, cfg):
        cfg = cfg.copy()
        if (not isinstance(cfg.get("token"), six.string_types)):
            raise CraftAICredentialsError("""Unable to create client with no"""
                                          """ or invalid token provided.""")
        if (not isinstance(cfg.get("owner"), six.string_types)):
            raise CraftAICredentialsError("""Unable to create client with no"""
                                          """ or invalid owner provided.""")
        if (not isinstance(cfg.get("url"), six.string_types)):
            cfg["url"] = "https://beta.craft.ai"
        if cfg.get("url").endswith("/"):
            raise CraftAIBadRequestError("""Unable to create client with"""
                                         """invalid url provided. The url """
                                         """should not terminate with a """
                                         """slash. """)
        self._config = cfg

        self._base_url = "{}/api/{}".format(
            self.config["url"],
            self.config["owner"])

        # Headers have to be reset here to avoid multiple definitions
        # of the 'Authorization' header if config is modified
        self._headers = {}
        self._headers["Authorization"] = "Bearer " + self.config.get("token")

    #################
    # Agent methods #
    #################

    def create_agent(self, model, agent_id=""):
        # Building final headers
        ct_header = {"Content-Type": "application/json; charset=utf-8"}
        headers = helpers.join_headers(self._headers, ct_header)

        # Building payload and checking that it is valid for a JSON
        # serialization
        payload = {
            "id": agent_id,
            "model": model
        }
        try:
            json_pl = json.dumps(payload)
        except TypeError as e:
            raise CraftAIBadRequestError("Invalid model or agent id given. {}".
                                         format(e.__str__())
                                         )

        req_url = "{}/agents".format(self._base_url)
        resp = requests.post(req_url, headers=headers, data=json_pl)

        agent = self._decode_response(resp)

        return agent

    def get_agent(self, agent_id):
        # Raises an error when agent_id is invalid
        self._check_agent_id(agent_id)

        # No supplementary headers needed
        headers = self._headers.copy()

        req_url = "{}/agents/{}".format(self._base_url, agent_id)
        resp = requests.get(req_url, headers=headers)

        agent = self._decode_response(resp)

        return agent

    def delete_agent(self, agent_id):
        # Raises an error when agent_id is invalid
        self._check_agent_id(agent_id)

        # No supplementary headers needed
        headers = self._headers.copy()

        req_url = "{}/agents/{}".format(self._base_url, agent_id)
        resp = requests.delete(req_url, headers=headers)

        decoded_resp = self._decode_response(resp)

        return decoded_resp

    ###################
    # Context methods #
    ###################

    def add_operations(self, agent_id, operations):
        # Raises an error when agent_id is invalid
        self._check_agent_id(agent_id)

        # Building final headers
        ct_header = {"Content-Type": "application/json; charset=utf-8"}
        headers = helpers.join_headers(self._headers, ct_header)

        try:
            json_pl = json.dumps(operations)
        except TypeError as e:
            raise CraftAIBadRequestError("Invalid model or agent id given. {}".
                                         format(e.__str__())
                                         )

        req_url = "{}/agents/{}/context".format(self._base_url, agent_id)
        resp = requests.post(req_url, headers=headers, data=json_pl)

        decoded_resp = self._decode_response(resp)

        return decoded_resp

    def get_operations_list(self, agent_id):
        # Raises an error when agent_id is invalid
        self._check_agent_id(agent_id)

        headers = self._headers.copy()

        req_url = "{}/agents/{}/context".format(self._base_url, agent_id)

        resp = requests.get(req_url, headers=headers)

        ops_list = self._decode_response(resp)

        return ops_list

    def get_context_state(self, agent_id, timestamp):
        # Raises an error when agent_id is invalid
        self._check_agent_id(agent_id)

        headers = self._headers.copy()

        req_url = "{}/agents/{}/context/state?t={}".format(
            self._base_url,
            agent_id,
            timestamp)
        resp = requests.get(req_url, headers=headers)

        context_state = self._decode_response(resp)

        return context_state

    #########################
    # Decision tree methods #
    #########################

    def get_decision_tree(self, agent_id, timestamp):
        # Raises an error when agent_id is invalid
        self._check_agent_id(agent_id)

        headers = self._headers.copy()

        req_url = "{}/agents/{}/decision/tree?t={}".format(
            self._base_url,
            agent_id,
            timestamp)

        resp = requests.get(req_url, headers=headers)

        decision_tree = self._decode_response(resp)

        return decision_tree

    def get_decision_from_context(self, agent_id, timestamp, decision_context):
        pass

    ####################
    # Internal helpers #
    ####################

    def _decode_response(self, response):
        if response.status_code == requests.codes.not_found:
            raise CraftAINotFoundError(response.text)
        if response.status_code == requests.codes.bad_request:
            raise CraftAIBadRequestError(response.text)
        if response.status_code == requests.codes.unauthorized:
            raise CraftAICredentialsError(response.text)

        try:
            return response.json()
        except json.JSONDecodeError:
            raise CraftAIUnknownError(response.text)

    def _check_agent_id(self, agent_id):
        """Checks that the given agent_id is a valid non-empty string.

        Raises an error if the given agent_id is not of type string or if it is
        an empty string.
        """
        if (not isinstance(agent_id, six.string_types) or
                agent_id == ""):
            raise CraftAIBadRequestError("""agent_id has to be a non-empty"""
                                         """string""")
