# To avoid conflicts between python's own 'time' and this 'time.py'
# cf. https://stackoverflow.com/a/28854227
from __future__ import absolute_import

import json
import time

from platform import python_implementation, python_version

import requests
import six

from craftai import __version__ as pkg_version
from craftai.constants import AGENT_ID_PATTERN, DEFAULT_DECISION_TREE_VERSION
from craftai.errors import CraftAiCredentialsError, CraftAiBadRequestError, CraftAiNotFoundError
from craftai.errors import CraftAiUnknownError, CraftAiInternalError, CraftAiLongRequestTimeOutError
from craftai.errors import CraftAiNetworkError
from craftai.interpreter import Interpreter
from craftai.jwt_decode import jwt_decode

USER_AGENT = "craft-ai-client-python/{} [{} {}]".format(pkg_version,
                                                        python_implementation(),
                                                        python_version())

ERROR_ID_MESSAGE = ("Invalid agent id given.\n"
                    "It must be a string containing only\n"
                    "characters in \"a-zA-Z0-9_-\" \n"
                    "and must be between 1 and 36 characters.")

def current_time_ms():
  return int(round(time.time() * 1000))

class CraftAIClient(object):
  """Client class for craft ai's API"""

  def __init__(self, cfg):
    self._base_url = ""
    self._headers = {}
    self._config = {}
    # Requests session: connection pooling and base configuration for all requests
    self._requests_session = requests.Session()

    try:
      self.config = cfg
    except (CraftAiCredentialsError, CraftAiBadRequestError) as e:
      raise e

  @property
  def config(self):
    return self._config

  @config.setter
  def config(self, cfg):
    cfg = cfg.copy()
    (payload, _, _, _) = jwt_decode(cfg.get("token"))
    cfg["owner"] = cfg["owner"] if "owner" in cfg else payload.get("owner")
    cfg["project"] = cfg["project"] if "project" in cfg else payload.get("project")
    cfg["url"] = cfg["url"] if "url" in cfg else payload.get("platform")

    if not isinstance(cfg.get("project"), six.string_types):
      raise CraftAiCredentialsError("""Unable to create client with no"""
                                    """ or invalid project provided.""")
    else:
      splitted_project = cfg.get("project").split("/")
      if len(splitted_project) == 2:
        cfg["owner"] = splitted_project[0]
        cfg["project"] = splitted_project[1]
      elif len(splitted_project) > 2:
        raise CraftAiCredentialsError("""Unable to create client with invalid"""
                                      """ project name.""")
    if not isinstance(cfg.get("owner"), six.string_types):
      raise CraftAiCredentialsError("""Unable to create client with no"""
                                    """ or invalid owner provided.""")
    if not isinstance(cfg.get("operationsChunksSize"), six.integer_types):
      cfg["operationsChunksSize"] = 200
    if (cfg.get("decisionTreeRetrievalTimeout") is not False and
        not isinstance(cfg.get("decisionTreeRetrievalTimeout"), six.integer_types)):
      cfg["decisionTreeRetrievalTimeout"] = 1000 * 60 * 5 # 5 minutes
    if not isinstance(cfg.get("url"), six.string_types):
      cfg["url"] = "https://beta.craft.ai"
    if cfg.get("url").endswith("/"):
      raise CraftAiBadRequestError("""Unable to create client with"""
                                   """ invalid url provided. The url"""
                                   """ should not terminate with a"""
                                   """ slash.""")
    self._config = cfg

    self._base_url = "{}/api/v1/{}/{}".format(self.config["url"],
                                              self.config["owner"],
                                              self.config["project"])

    if cfg.get("proxy"):
      scheme = six.moves.urllib.parse.urlparse(self.config["url"]).scheme
      if not scheme:
        raise CraftAiCredentialsError("""Unable to create client with an URL"""
                                      """ without a scheme. Cannot configure"""
                                      """ the proxy.""")
      proxies = {}
      proxies[scheme] = cfg.get("proxy")
      self._requests_session.proxies = proxies
    # Headers have to be set here to avoid multiple definitions
    # of the 'Authorization' header if config is modified
    base_headers = {}
    base_headers["Authorization"] = "Bearer " + self.config.get("token")
    base_headers["User-Agent"] = USER_AGENT
    self._requests_session.headers = base_headers

  #################
  # Agent methods #
  #################

  def create_agent(self, configuration, agent_id=""):
    # Extra header in addition to the main session's
    ct_header = {"Content-Type": "application/json; charset=utf-8"}

    # Building payload and checking that it is valid for a JSON
    # serialization
    payload = {"configuration": configuration}

    if agent_id != "":
      # Raises an error when agent_id is invalid
      self._check_agent_id(agent_id)

      payload["id"] = agent_id

    try:
      json_pl = json.dumps(payload)
    except TypeError as e:
      raise CraftAiBadRequestError("Invalid configuration or agent id given. {}"
                                   .format(e.__str__()))

    req_url = "{}/agents".format(self._base_url)
    resp = self._requests_session.post(req_url, headers=ct_header, data=json_pl)

    agent = self._decode_response(resp)

    return agent

  def create_agents(self, payload):
    # payload = [{"id": agent_id, "configuration": configuration}] the id key is optionnal
    # Check all ids, raise an error if all ids are invalid
    valid_indices, invalid_indices, invalid_agents = self._check_agent_id_bulk(payload)

    # Create the json file with the agents with valid id and send it
    valid_agents = self.create_and_send_json_bulk([payload[i] for i in valid_indices],
                                                  "{}/bulk/agents".format(self._base_url),
                                                  "POST")

    if invalid_indices == []:
      return valid_agents

    # Put the valid and invalid agents in their original index
    return self.recreate_list_with_indices(valid_indices,
                                           valid_agents,
                                           invalid_indices,
                                           invalid_agents)

  def get_agent(self, agent_id):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}".format(self._base_url, agent_id)
    resp = self._requests_session.get(req_url)

    agent = self._decode_response(resp)

    return agent

  def list_agents(self):

    req_url = "{}/agents".format(self._base_url)
    resp = self._requests_session.get(req_url)

    agents = self._decode_response(resp)

    return agents["agentsList"]

  def delete_agent(self, agent_id):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}".format(self._base_url, agent_id)
    resp = self._requests_session.delete(req_url)

    decoded_resp = self._decode_response(resp)

    return decoded_resp

  def delete_agents(self, payload):
    # payload = [{"id": agent_id}]
    # Check all ids, raise an error if all ids are invalid
    valid_indices, invalid_indices, invalid_agents = self._check_agent_id_bulk(payload)

    # Create the json file with the agents with valid id and send it
    valid_agents = self.create_and_send_json_bulk([payload[i] for i in valid_indices],
                                                  "{}/bulk/agents".format(self._base_url),
                                                  "DELETE")

    if invalid_indices == []:
      return valid_agents

    # Put the valid and invalid agents in their original index
    return self.recreate_list_with_indices(valid_indices,
                                           valid_agents,
                                           invalid_indices,
                                           invalid_agents) 

  def get_shared_agent_inspector_url(self, agent_id, timestamp=None):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}/shared".format(self._base_url, agent_id)
    resp = self._requests_session.get(req_url)

    url = self._decode_response(resp)

    if timestamp is not None:
      return "{}?t={}".format(url["shortUrl"], str(timestamp))

    return url["shortUrl"]

  def delete_shared_agent_inspector_url(self, agent_id):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}/shared".format(self._base_url, agent_id)
    resp = self._requests_session.delete(req_url)

    decoded_resp = self._decode_response(resp)

    return decoded_resp

  ###################
  # Context methods #
  ###################

  def add_operations(self, agent_id, operations):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    # Extra header in addition to the main session's
    ct_header = {"Content-Type": "application/json; charset=utf-8"}
    offset = 0

    is_looping = True

    while is_looping:
      next_offset = offset + self.config["operationsChunksSize"]

      try:
        json_pl = json.dumps(operations[offset:next_offset])
      except TypeError as e:
        raise CraftAiBadRequestError("Invalid configuration or agent id given. {}"
                                     .format(e.__str__()))

      req_url = "{}/agents/{}/context".format(self._base_url, agent_id)
      resp = self._requests_session.post(req_url, headers=ct_header, data=json_pl)
      self._decode_response(resp)

      if next_offset >= len(operations):
        is_looping = False

      offset = next_offset

    return {
      "message": "Successfully added %i operation(s) to the agent \"%s/%s/%s\" context."
                 % (len(operations), self.config["owner"], self.config["project"], agent_id)
    }

  def add_operations_bulk(self, payload):
    # payload = [{"id": agent_id, "operations": list_operations}]
    # Check all ids, raise an error if all ids are invalid
    valid_indices, _, invalid_agents = self._check_agent_id_bulk(payload)
    valid_payload = [payload[i] for i in valid_indices]

    valid_agents = []
    offset = 0
    is_looping = True
    while is_looping:
      next_offset = offset + self.config["operationsChunksSize"]
      payload_offset = []

      for agent in valid_payload:
        if offset <= len(agent["operations"]):
          new_agent = {"id": agent["id"]}
          new_agent["operations"] = agent["operations"][offset:next_offset]
          payload_offset.append(new_agent)

      if payload_offset == []:
        is_looping = False
      else:
        valid_agents.append(
          self.create_and_send_json_bulk(payload_offset,
                                         "{}/bulk/context".format(self._base_url),
                                         request_type="POST")
        )

        offset = next_offset

    return invalid_agents + valid_agents

  """
  def add_operations_bulk(self, payload):
    # payload = [{"id": agent_id, "operations": list_operations}]
    # Check all ids, raise an error if all ids are invalid
    valid_indices, invalid_indices, invalid_agents = self._check_agent_id_bulk(payload)
    valid_payload = [payload[i] for i in valid_indices]
    url = "{}/bulk/context".format(self._base_url)

    valid_agents = []
    payload_offset = []
    nb_operations = 0
    chunk_size = self.config["operationsChunksSize"]

    for agent in valid_payload:
      is_looping = True
      offset = 0

      while is_looping:

        new_agent = {"id": agent["id"]}
        next_offset = offset + chunk_size
        try:
          new_agent["operations"] = agent["operations"][offset:next_offset]
          nb_operations += len(new_agent["operations"])
          if new_agent["operations"] != []:
            payload_offset.append(new_agent)
        except TypeError as e:
          new_agent["error"] = e
          valid_agents.append([new_agent])

        # Send the operations when the size of the payload is max
        if nb_operations == self.config["operationsChunksSize"]:
          chunk_size = self.config["operationsChunksSize"]
          valid_agents.append(
            self.create_and_send_json_bulk(payload_offset, url, "POST")
          )
          payload_offset = []
          nb_operations = 0
          offset = next_offset

        # Add operations of the next agent before sending the payload
        else:
          is_looping = False
          chunk_size = self.config["operationsChunksSize"] - nb_operations


    # Send the last incomplete payload
    if payload_offset != []:
      valid_agents.append(
        self.create_and_send_json_bulk(payload_offset, url, "POST")
      )

    # Sort the agents to be in their original places
    return self.recreate_list_with_indices(valid_indices,
                                           self._recreate_list_add_operations_bulk(valid_agents),
                                           invalid_indices,
                                           invalid_agents)

  @staticmethod
  def _recreate_list_add_operations_bulk(responses):
    index = 0
    all_agent_id = {}
    res = []
    for response in responses:
      for agent in response:
        print(agent)

        if agent['id'] in all_agent_id:

          index_agent = all_agent_id[agent['id']]
          if 'message' in agent:
            if 'message' in res[index_agent]:
              res[index_agent]['message'] += agent['message']
            else:
              res[index_agent]['message'] = agent['message']
          if 'error' in agent:
            if 'error' in res[index_agent]:
              res[index_agent]['error'].append(agent['error'])
            else:
              res[index_agent]['error'] = [agent['error']]

        else:
          all_agent_id[agent['id']] = index
          index += 1
          new_agent = {}
          new_agent['id'] = agent['id']
          if 'message' in agent:
            new_agent['message'] = agent['message']
          else:
            new_agent['error'] = [agent['error']]
          res.append(new_agent)
    return res
  """
  def _get_operations_list_pages(self, url, ops_list):
    if url is None:
      return ops_list

    resp = self._requests_session.get(url)

    new_ops_list = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_operations_list_pages(next_page_url, ops_list + new_ops_list)

  def get_operations_list(self, agent_id, start=None, end=None):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}/context".format(self._base_url, agent_id)
    req_params = {
      "start": start,
      "end": end
    }
    resp = self._requests_session.get(req_url, params=req_params)

    initial_ops_list = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_operations_list_pages(next_page_url, initial_ops_list)

  def _get_state_history_pages(self, url, state_history):
    if url is None:
      return state_history

    resp = self._requests_session.get(url)

    new_state_history = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_state_history_pages(next_page_url, state_history + new_state_history)

  def get_state_history(self, agent_id, start=None, end=None):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}/context/state/history".format(self._base_url, agent_id)
    req_params = {
      "start": start,
      "end": end
    }
    resp = self._requests_session.get(req_url, params=req_params)

    initial_states_history = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_state_history_pages(next_page_url, initial_states_history)

  def get_context_state(self, agent_id, timestamp):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}/context/state?t={}".format(self._base_url,
                                                       agent_id,
                                                       timestamp)
    resp = self._requests_session.get(req_url)

    context_state = self._decode_response(resp)

    return context_state

  #########################
  # Decision tree methods #
  #########################

  def _get_decision_tree(self, agent_id, timestamp, version):
    headers = self._headers.copy()
    headers["x-craft-ai-tree-version"] = version
    # If we give no timestamp the default behaviour is to give the tree from the latest timestamp
    if timestamp is None:
      req_url = "{}/agents/{}/decision/tree?".format(self._base_url, agent_id)
    else:
      req_url = "{}/agents/{}/decision/tree?t={}".format(self._base_url, agent_id, timestamp)

    resp = self._requests_session.get(req_url)

    decision_tree = self._decode_response(resp)

    return decision_tree

  def get_decision_tree(self, agent_id, timestamp=None, version=DEFAULT_DECISION_TREE_VERSION):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)
    if self._config["decisionTreeRetrievalTimeout"] is False:
      # Don't retry
      return self._get_decision_tree(agent_id, timestamp, version)

    start = current_time_ms()
    while True:
      now = current_time_ms()
      if now - start > self._config["decisionTreeRetrievalTimeout"]:
        # Client side timeout
        raise CraftAiLongRequestTimeOutError()
      try:
        return self._get_decision_tree(agent_id, timestamp, version)
      except CraftAiLongRequestTimeOutError:
        # Do nothing and continue.
        continue

  def _get_decision_trees(self, payload, valid_indices, invalid_indices, invalid_dts):
    valid_dts = self.create_and_send_json_bulk([payload[i] for i in valid_indices],
                                               "{}/bulk/decision_tree".format(self._base_url),
                                               "POST")

    if invalid_indices == []:
      return valid_dts

    # Put the valid and invalid decision trees in their original index
    return self.recreate_list_with_indices(valid_indices, valid_dts, invalid_indices, invalid_dts)

  def get_decision_trees(self, payload, version=DEFAULT_DECISION_TREE_VERSION):
    # payload = [{"id": agent_id, "timestamp": timestamp}]
    headers = self._headers.copy()
    headers["x-craft-ai-tree-version"] = version
    # Check all ids, raise an error if all ids are invalid
    valid_indices, invalid_indices, invalid_dts = self._check_agent_id_bulk(payload)

    if self._config["decisionTreeRetrievalTimeout"] is False:
      # Don't retry
      return self._get_decision_trees(payload,
                                      valid_indices,
                                      invalid_indices,
                                      invalid_dts)
    start = current_time_ms()
    while True:
      now = current_time_ms()
      if now - start > self._config["decisionTreeRetrievalTimeout"]:
        # Client side timeout
        raise CraftAiLongRequestTimeOutError()
      try:
        return self._get_decision_trees(payload,
                                        valid_indices,
                                        invalid_indices,
                                        invalid_dts)
      except CraftAiLongRequestTimeOutError:
        # Do nothing and continue.
        continue

  @staticmethod
  def decide(tree, *args):
    return Interpreter.decide(tree, args)

  @staticmethod
  def _parse_body(response):
    try:
      return response.json()
    except:
      return response.text()
      # raise CraftAiInternalError(
      #   "Internal Error, the craft ai server responded in an invalid format."
      # )

  @staticmethod
  def _decode_response(response):
    status_code = response.status_code

    message = "Status code " + str(status_code)
    try:
      message = json.dumps(CraftAIClient._parse_body(response))
      #message = CraftAIClient._parse_body(response)["message"]
    except (CraftAiInternalError, KeyError, TypeError):
      pass

    if status_code in [200, 201, 204, 207]:
      return CraftAIClient._parse_body(response)
    if status_code == 202:
      raise CraftAiLongRequestTimeOutError(message)
    if status_code == 401 or status_code == 403:
      raise CraftAiCredentialsError(message)
    if status_code == 400:
      raise CraftAiBadRequestError(message)
    if status_code == 404:
      raise CraftAiNotFoundError(message)
    if status_code == 413:
      raise CraftAiBadRequestError("Given payload is too large")
    if status_code == 500:
      raise CraftAiInternalError(message)
    if status_code == 503:
      raise CraftAiNetworkError("""Service momentarily unavailable, please try"""
                                """again in a few minutes. If the problem """
                                """persists please contact us at support@craft.ai""")
    if status_code == 504:
      raise CraftAiBadRequestError("Request has timed out")

    raise CraftAiUnknownError(message)

  @staticmethod
  def _decode_response_bulk(response_bulk):
    resp = []
    for response in response_bulk:
      if ("status" in response):
        if response['status'] == 201:
          agent = {"id": response["id"],
                   "message": response["message"]}
        else:
          agent = {"id": response["id"]}
          status_code = response["status"]
          message = response["message"]

          if status_code == 202:
            agent["error"] = CraftAiLongRequestTimeOutError(message)
          elif status_code == 401 or status_code == 403:
            agent["error"] = CraftAiCredentialsError(message)
          elif status_code == 400:
            agent["error"] = CraftAiBadRequestError(message)
          elif status_code == 404:
            agent["error"] = CraftAiNotFoundError(message)
          elif status_code == 413:
            agent["error"] = CraftAiBadRequestError("Given payload is too large")
          elif status_code == 500:
            agent["error"] = CraftAiInternalError(message)
          elif status_code == 503:
            agent["error"] = CraftAiNetworkError("""Service momentarily unavailable, please try"""
                                                """again in a few minutes. If the problem """
                                                """persists please contact us at support@craft.ai""")
          elif status_code == 504:
            agent["error"] = CraftAiBadRequestError("Request has timed out")
          else:
            agent["error"] = CraftAiUnknownError(message)

        resp.append(agent)

      else:
        resp.append(response)

    return resp

  @staticmethod
  def _check_agent_id(agent_id):
    """Checks that the given agent_id is a valid non-empty string.

    Raises an error if the given agent_id is not of type string or if it is
    an empty string.
    """
    if (not isinstance(agent_id, six.string_types) or
        AGENT_ID_PATTERN.match(agent_id) is None):
      raise CraftAiBadRequestError(ERROR_ID_MESSAGE)

  def _check_agent_id_bulk(self, payload):
    """Checks that the given agent_id is a valid non-empty string.
        # payload = [{"id": agent_id}]


    Raises an error if the given agent_id is not of type string or if it is
    an empty string.
    """
    invalid_agent_indices = []
    invalid_agent_errors = []
    valid_agent_indices = []
    for index, agent in enumerate(payload):
      try:
        # Check if the agent ID is valid
        if "id" in agent:
          self._check_agent_id(agent["id"])
      except CraftAiBadRequestError:
        invalid_agent_indices.append(index)
        invalid_agent_errors.append(CraftAiBadRequestError(ERROR_ID_MESSAGE))
      else:
        try:
          # Check if the agent is serializable
          json.dumps([agent])
        except TypeError as e:
          invalid_agent_indices.append(index)
          invalid_agent_errors.append(e)
        else:
          valid_agent_indices.append(index)

    if len(invalid_agent_indices) == len(payload):
      raise CraftAiBadRequestError(ERROR_ID_MESSAGE)

    invalid_payload = []
    for index, invalid_agent in enumerate([payload[i] for i in invalid_agent_indices]):
      invalid_payload.append({"id": invalid_agent["id"],
                              "error": invalid_agent_errors[index]})

    return valid_agent_indices, invalid_agent_indices, invalid_payload

  @staticmethod
  def recreate_list_with_indices(indices1, values1, indices2, values2):
    full_list = [None] * (len(indices1) + len(indices2))
    for i, index in enumerate(indices1):
      full_list[index] = values1[i]
    for i, index in enumerate(indices2):
      full_list[index] = values2[i]

    return full_list

  def create_and_send_json_bulk(self, payload, req_url, request_type="GET"):
    # Extra header in addition to the main session's
    ct_header = {"Content-Type": "application/json; charset=utf-8"}

    try:
      json_pl = json.dumps(payload)
    except TypeError as e:
      raise CraftAiBadRequestError("Invalid configuration or agent id given to create JSON. {}"
                                   .format(e.__str__()))

    if request_type == "POST":
      resp = self._requests_session.post(req_url, headers=ct_header, data=json_pl)
    elif request_type == "DELETE":
      resp = self._requests_session.delete(req_url, headers=ct_header, data=json_pl)
    else:
      resp = self._requests_session.get(req_url, headers=ct_header, data=json_pl)

    agents = self._decode_response(resp)
    agents = self._decode_response_bulk(agents)

    return agents
