"""
GraqhQL Helper Classes
"""
import os
import sys

import pprint

import getpass
import json
import requests

import jinja2

import re

"""
try:
    import rpm
    RPM_SITE_PACKAGE_LOADED = True
except Exception as e:
"""

import version_utils
RPM_SITE_PACKAGE_LOADED = False

from requests.packages.urllib3.exceptions import InsecureRequestWarning

GRAPHQL_API_HOST   = '127.0.0.1'
GRAPHQL_API_URL    = '/api/v1/graphql'
GRAPHQL_LOGIN_URL  = '/api/v1/login'
GRAPHQL_LOCAL_PORT_NODE = 31516
GRAPHQL_LOCAL_PORT_NGINX = 31517
GRAPHQL_LOCAL_RPM_VERSION = ""

def set_local_rpm_version(version):
    global GRAPHQL_LOCAL_RPM_VERSION
    #print(f"*** Set Local RPM Version to {version} ***\n")
    GRAPHQL_LOCAL_RPM_VERSION=version

def update_by_type(dest, source):
    if isinstance(dest, list):
        assert isinstance(source, list), "update_by_type: dest is list, source is " + \
            source.__class__.__name__ 
        dest.extend(source)
    elif isinstance(dest, dict):
        if not isinstance(source, dict):
            assert False, "update_by_type: " + pprint.pformat(source)
        assert isinstance(source, dict), "update_by_type: dest is dict, source is " + \
            source.__class__.__name__ 
        dest.update(source)
    else:
        raise TypeError

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))
    print('------------END------------\n')

class RestToken:
  """
  REST API Token manager.
  The API token is stored at $HOME/.graphql/token
  """
  def __init__(self, doLogin=True, gql_path=None):
      if gql_path is None:
          home_path = os.path.expanduser("~")
          self.token_file_path = os.path.join(home_path, '.graphql', 'token')
      else:
          self.token_file_path = os.path.join(gql_path, 'token')
      try:
          with open(self.token_file_path, 'r') as file:
              data = file.read().replace('\n', '')     
          self.token = data
      except (IOError, FileNotFoundError) as exception_type:
          self.token=''
          self.init_token(gql_path=gql_path)

  @property
  def token(self):
      return self._token

  def init_token(self, username='', password='', gql_path=None):
      """
      """
      if username == '':
          username = getpass.getuser()
      if username == 'root':
          username = 'admin'
      if password == '':
          print(f'Please enter password for user {username} to generate a token.')
          print('You should only have to do this once')
          password = getpass.getpass()
          if password == '':
              return False

      requests.packages.urllib3.disable_warnings(InsecureRequestWarning)      
      
      api_url = 'https://%s%s' % (GRAPHQL_API_HOST, GRAPHQL_LOGIN_URL)
      headers = {'Content-Type': 'application/json'}
      credentials = {"username": username, "password": password}
      response = requests.post(api_url, headers=headers, data=json.dumps(credentials), verify=False)
      json_response = response.json()
      try:
         self.token = json_response['token']            
      except KeyError:
         pprint.pprint(json_response)
         print(f'Failed to obtain token for user "{username}"')
         sys.exit(1)

      if gql_path is None:
          token_path = os.path.join(os.environ['HOME'], '.graphql')
      else:
          token_path = gql_path
      token_file_path = os.path.join(token_path, 'token')
     
      if not os.path.exists(token_path):
          os.mkdir(token_path)

      with open(token_file_path, "w") as token_file:
          token_file.write(self.token)

      return True

  def get_token(self):
      return self.token


class RawGQL:
  """
  """
  def __init__(self, raw_string, debug=False):
      self.raw_string=raw_string
      self._debug = debug

  @property
  def debug(self):
      return self._debug

  @debug.setter
  def debug(self, value : bool):
      self._debug = value
    
  @property
  def flatten_reply(self):
      return False

  def get_top_level(self):
      return True

  def format(self):
      return self.raw_string

  def build_query(self):
      return { "query" : '{' + self.format() + '}' }

  def format_results(self, json_dict):
      return json_dict['data']

  def send_query(self, rt, json_reply, errors=None):
      global GRAPHQL_API_HOST
      global GRAPHQL_API_URL
      global GRAPHQL_LOCAL_RPM_VERSION
      global GRAPHQL_LOCAL_PORT_NODE
      global GRAPHQL_LOCAL_PORT_NGINX

      if self.get_top_level() is False:
         return

      # Don't validate rhe server's cert
      requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

      if rt is None:
          # WARNING: access via GRAPHQL_LOCAL_PORT will be dprecated in 4.4...
          if self.debug:
              print(f"{self.__class__.__name__}.send_query: local version={GRAPHQL_LOCAL_RPM_VERSION}")
          local_port=GRAPHQL_LOCAL_PORT_NODE
          local_version_tuple = ("0", GRAPHQL_LOCAL_RPM_VERSION, "0")
          nginx_version_tuple = ("0", "4.4.0", "0")
          if RPM_SITE_PACKAGE_LOADED:
              if rpm.labelCompare(local_version_tuple, nginx_version_tuple) >= 0:
                  local_port=GRAPHQL_LOCAL_PORT_NGINX
          else:
              if version_utils.rpm.labelCompare(local_version_tuple, nginx_version_tuple) >= 0:
                  local_port=GRAPHQL_LOCAL_PORT_NGINX

          url = 'http://' + GRAPHQL_API_HOST
          url = url + f":{local_port}"
      else:
          url = 'https://' + GRAPHQL_API_HOST
      url = url + GRAPHQL_API_URL

      headers = {}
      if not rt is None:
          headers['Authorization'] = 'Bearer %s' % rt.get_token()
      headers['Content-Type']  = 'application/json'

      data  = {}

      json_body = self.build_query()

      if self.debug:
          req = requests.Request('POST', url, data = json.dumps(json_body), headers = headers)
          prepared = req.prepare()
          pretty_print_POST(prepared)

      try:
          response = requests.post(url, data = json.dumps(json_body), headers = headers, verify = False)
          if self.debug:
              print('................START RAW REPLY ......................')
              pprint.pprint(response.status_code)
              print('......................................................')
              pprint.pprint(response.content)
              print('......................................................')
              pprint.pprint(response.json())
              print('.................END RAW REPLY .......................')

      except (ConnectionRefusedError, 
              requests.packages.urllib3.exceptions.NewConnectionError, 
              requests.exceptions.ConnectionError) as e:
          print(f'+----------------------------------------------------------------------------+')
          print(f'| Unable to communicate with GraphQL:')
          print(f'| {url}')
          print(f'| {e.__class__.__name__}')
          print(f'| {e}')
          print(f'+----------------------------------------------------------------------------+')
          sys.exit(1)

      server_status = response.status_code
      if server_status == 200:
          resp_as_json = response.json()
          try:
              if 'errors' in resp_as_json and \
                 errors is not None:
                  errors.clear()
                  errors.extend(resp_as_json["errors"])
              update_by_type(json_reply, self.format_results(resp_as_json))
              #json_reply.update(self.format_results(resp_as_json))
          except (KeyError, IndexError) as e:
              if self.debug:
                  print(f"GQLRaw::send_query: Exception - {e.__class__.__name__}")
              json_reply.clear()

      if self.debug:
          if server_status == 200:
              print('========= json reply =========')
              pprint.pprint(json_reply)
              if errors is not None:
                  print('========= errors ==========')
                  pprint.pprint(errors)
          else:
              print(f'========= server status: {server_status} =========')

      return server_status

  def flatten_json(self, node, stop_prefix, seperator='/', prefix='/', depth=0):
      output_list = []
      fields_noop = {}

      def unedgify(edgy_node):
          """
          Replaces ['edges']['node'][key]....
                     LIST     DICT
          With a list of dictionaries.

          Converts:
          {edges : [{node : { 'key-1' : 'value-1' }},
                    {node : { 'key-1' : 'value-1' }}
           ]}

          To:
          [{ 'key-1', 'value-1' },
           { 'key-1', 'value-1' }]
          """
          if isinstance(edgy_node, dict):
              if 'edges' in edgy_node:
                  edgy_node = edgy_node['edges']
                  index = 0
                  while index < len(edgy_node):
                      if isinstance(edgy_node[index], dict) and\
                         'node' in edgy_node[index]:
                          edgy_node[index] = edgy_node[index]['node']
                      edgy_node[index] = unedgify(edgy_node[index])
                      index = index + 1
              else:
                  for key in edgy_node:
                      edgy_node[key] = unedgify(edgy_node[key])
          return edgy_node

      skip_list = [ 'edges', 'node' ]

      def _make_new_prefix(prefix, key, sperator):
          prefstr = prefix
          if not key in skip_list:
              plen = len(prefix)
              if plen > 0 and prefix != key[0:plen]:
                  if prefix == seperator or \
                     key[0] == seperator:
                      prefstr = prefix + key
                  else:
                      prefstr = prefix + seperator + key
              else:
                  prefstr = key
          return prefstr

      def _flatten_json(node, stop_prefix, seperator='/', prefix='/', depth=0):
          """
          Flatten json reply, starting at root, down to stopkey, skipping edges and node
          key.  Each key is named with the levels traversed prepended (each named level
          seperated by the seperator parameter..

          Returns:
          node_list:  A list of nodes at level; stop_prefix built up during recursion
          field_dict: A dictionary of fields to be applied to node_list during tail-end
                      recursion (should be empty at finish)

          Note: 
          Currently this will not work for 'unusual' grapqhql where 'node' means a 128T node name
          and not a graphql node.  Likewise lists not in the form { 'edges' : [ entry1, entry2, ... ] }
          can cause poblems
          """
          node_list = []
          field_dict = {}

          # print(f"{' ' * depth}>>> {prefix}")

          node_type = type(node)
          if node_type == list:
              for entry in node:
                  sub_list, sub_fields  = _flatten_json(entry, stop_prefix, seperator, prefix, depth)
                  node_list = node_list + sub_list
                  field_dict.update(sub_fields)
          elif node_type == dict:
              for key in node:
                  prefstr = _make_new_prefix(prefix, key, seperator)
                  #print(f"{' ' * depth}PREFSTR: {prefstr} <- P:{prefix} S:{seperator} K:{key}")
                  sub_list, sub_fields = _flatten_json(node[key], stop_prefix, seperator, prefstr, depth + 1)
                  if prefstr == stop_prefix:
                      sub_list = unedgify(node[key])
                      if type(sub_list) == dict:
                         sub_list = sub_list.copy()
                      if type(sub_list) != list:
                         sub_list = [sub_list]
                  node_list = node_list + sub_list
                  field_dict.update(sub_fields)
          else:
              # at the stop-level, use normal field names
              key = prefix
              if stop_prefix in key:
                  key = prefix.split(seperator)[-1]
              #print(f'{" " * depth}PREFIX:{prefix} STOP_PREFIX:{stop_prefix} KEY:{key} VALUE:{pprint.pformat(node)}')
              field_dict[key] = node

          if len(node_list) > 0 and \
              len(field_dict) > 0:
              for entry in node_list:
                  # cannot blindly do entry.update(field_dict), as subtrees with
                  # no nodes for stop_prefix will bubble up and overwrite previous
                  # entries...
                  for field_key in field_dict:
                      if type(entry) == dict:
                          if field_key not in entry:
                              entry[field_key] = field_dict[field_key]
              field_dict = {}
          return node_list, field_dict.copy()

      output_list, fields_noop = _flatten_json(node, stop_prefix, seperator, prefix, depth)
      return output_list


class NodeGQL(RawGQL):
  """
  """
  def __init__(self, name, fields=[], names=[], top_level=False, debug=False):
     super().__init__('', debug)

     self.fields=fields
     self.nodes=[]
     self.name=name
     self.names=names
     self.top_level = top_level

     # if the name starts with 'all' then assume its top_level...
     if self.top_level is False:
         if self.name[:3] == 'all':
             self.top_level = True

  def get_top_level(self):
     return self.top_level

  def set_fields(self, fields):
      self.fields = fields

  def clear_fields(self):
      self.fields=[]

  def add_node(self, node):
      node.top_level = False
      self.nodes.append(node)

  def get_api_string(self):
      api_string = self.name
      if len(self.names) > 0:
          name_count = 0
          api_string += '(names: [ '
          for name in self.names:
              if name_count > 0:
                  api_string += ', '
              api_string += '"' + name + '"'
              name_count += 1
          api_string += ' ])'
      return api_string

  def format(self):
      str = self.get_api_string()
      
      field_count=0
      if len(self.fields) > 0 or len (self.nodes > 0):
          str += ' { edges { node {'  
          for field in self.fields:
              str += ' ' + field
          for node in self.nodes:
              str += ' ' + node.format()
          str += ' } } }'
      #print(str)
      return str         

  def format_results(self, json_dict):
      #return json_dict['data'][self.name]['edges'][0]
      return json_dict['data']


class NewGQL(RawGQL):
      """
      API arguments are expressed as a dictionary, where the key is the argument name
      (must always be a string) and the value is the argument value:
      
      api_args = { 
          "name" : "fubar", 
          "names" : [ "Name_1", "Name_2" ... ], 
          "integer_arg" : 2, 
          "float_arg" : 2.2 
      }

      API fields represent the elements being queried... Note that currently the
      way to create a 'list' usng edges is to create a named (or unnamed) ai node and
      attach it to this one.

      api_fields = [
          "leaf_1",
          "leaf_2",
          "complex_field",
          [
             "sub_field_1" 
             "sub_field_2",
          }
      ]
      """
     
      def __init__(
          self,
          api_name, 
          api_args=None, 
          api_fields=None, 
          api_flat_key=None, 
          api_has_edges=None, 
          single_entry_to_dict=False,
          debug=False
      ):
          self.debug = debug
          self._api_name = api_name
          self._api_args = api_args
          self._api_fields = api_fields 
          self._api_flat_key = api_flat_key
          self._top_level = True
          self._nodes = []
          self.assert_post_flat = False
          if not api_has_edges is None:
              if not isinstance(api_has_edges, bool):
                  raise TypeError
              self._api_has_edges = api_has_edges
          else:
              self._api_has_edges = False
          if self.api_fields is not None:
              for field in self.api_fields:
                  if isinstance(field, NewGQL):
                      field._top_level = False
          self._single_entry_to_dict = single_entry_to_dict
          self.api_key_prefix = ''
          self.api_key_seperator = '/'

      @property
      def api_name(self):
          return self._api_name

      @property
      def api_args(self):
          return self._api_args

      @api_args.setter
      def api_args(self, value):
          if not isinstance(value, dict):
              raise TypeError
          if len (dict) < 1:
              raise ValueError
          self._api_args = value

      @property
      def api_fields(self):
          return self._api_fields

      @api_fields.setter
      def api_fields(self, value):
          if not isinstance(value, dict):
              raise TypeError
          if len (dict) < 1:
              raise ValueError
          self._api_fields = value

      @property
      def api_has_edges(self):
          return self._api_has_edges

      @api_has_edges.setter
      def api_has_edges(self, value):
          if not isinstance(value, dict):
              raise TypeError
          if len (dict) < 1:
              raise ValueError
          self._api_has_edges = value

      @property
      def api_flat_key(self):
          return self._api_flat_key

      @api_flat_key.setter
      def api_flat_key(self, value):
          if not isinstance(value, str) and \
             not value is None:
              raise TypeError
          self._api_flat_key = value

      @property
      def single_entry_to_dict(self):
          return self._single_entry_to_dict

      @api_flat_key.setter
      def single_entry_to_dict(self, value):
          if not isinstance(value, bool):
              raise TypeError
          self._single_entry_to_dict = value

      @property
      def top_level(self):
          return self._top_level

      @property
      def flatten_reply(self):
          return not self.api_flat_key is None

      def get_top_level(self):
          """
          Overrides parent
          """
          return self.top_level

      def add_node(self, node):
          node._top_level = False
          self._nodes.append(node)

      def add_field(self, field):
          """
          Overrides parent
          """
          valid_types = [ str, list, NewGQL ]
          for valid_type in valid_types:
              if not isinstance(field, valid_type):
                  raise TypeError
          self._api_fields.append(field)

      def _api_value_string(self, value):
          value_string = None
          # isinstance(value, bool) does not match booleans ??
          if value.__class__.__name__ == "bool":
              value_string = f"{value}"
              value_string = value_string.lower()
          elif isinstance(value, int) or \
             isinstance(value, float):
              value_string = f'{value}'
          elif isinstance(value, str):
              value_string = f'"{value}"'
          else:
              assert False, value.__class__.__name__
              raise ValueError
          if self.debug:
             print(f"_api_value_string: {value} type={value.__class__.__name__} -> {value_string}")
          return value_string

      def _format_api_string(self):
          """
          Formats the graphql argument list, given a dictionary of argument names
          The following types are supported:
          - list (of the following types)
          - str
          - int
          - float
          """
          api_string = self.api_name
          arg_string_list = []
          if not self.api_args is None and \
             len(self.api_args) > 0:
              for key in self.api_args:
                  try:
                      value = self.api_args[key]
                  except TypeError:
                      #assert False, f"node: {self.api_name} key: {key} bad arg: {self.api_args}" + \
                      #       f" type: {self.api_args.__class__.__name__}"
                      print(f"node: {self.api_name} key: {key} bad arg: {self.api_args}" + \
                            f" type: {self.api_args.__class__.__name__}")
                      raise TypeError
                  if isinstance(value, list):
                      value_string = "[ " + ",".join([self._api_value_string(x) for x in value]) + " ]"
                  else:
                      if value is None:
                          assert False, f"key={key}"
                      value_string = self._api_value_string(value)
                  arg_string_list.append(f"{key}:{value_string}")
              api_string += "(" + " ".join(arg_string_list) + ")"
              #assert False, f"{self.api_name}: {api_string}"
          return api_string

      def _format_field_string(self):
          """
          A field string can be:
          - A string representing a leaf node name
          - A list representing a sub-list of fields
            Note that crrently there is no simple way to represent:
                { field1, field2 { edges { node { field2.1 } } } }, as
                field2 is just  string...
                [ "field1", "field2", [ "edges", [ "node", [ "field2.1" ] ] ] ]
                should work, but it is ugly...
          - A NewGQL instance reresenting an API call
          """
          def _field_string(entry, depth) :
              if isinstance(entry, list):
                  if len(entry) == 0 or \
                     isinstance(entry[0], list):
                      raise ValueError
                  return_string = " ".join([_field_string(entry, depth+1) \
                         for entry in self.api_fields]) 
                  if depth > 0:
                      return_string = "{ " + return_string + " }"
                  return return_string
              elif isinstance(entry, str):
                  return entry
              elif isinstance(entry, NewGQL):
                  return entry.format()
              elif entry is None:
                  return ""
              else:
                  if self.debug:
                      print(f"**** value = {entry} ****")
                  raise ValueError
          return _field_string(self.api_fields, 0)

      def format(self):
          """
          Overrides parent
          """
          prefix = ""
          suffix = ""
          # assert False, f"format: api_has_edges = {self.api_has_edges}"
          if self.api_has_edges:
              prefix = "edges { node { "
              suffix = " } }"
          result = ""
          result += self._format_api_string() + " { "
          result += prefix
          result += self._format_field_string()
          if len(self._nodes) > 0:
              result += " "
          for node in self._nodes:
              result += node.format()
          result += suffix + " }"
          # assert False, f"RESULT: {result}"
          return result

      def build_query(self):
          return { "query" : '{ ' + self.format() + ' }' }
          
      def send_query(self, rt, json_reply, errors=None):
          """
          Overrides parent
         
          json_reply should be a list, even if only one item is expected to
          be returned.  This eases dict versus list confusion at the cost
          of doing only_entry = list[0].  NewGQL.single_entry_to_dict
          can be used to work around this...
          """
          #assert isinstance(json_reply, list)
          json_data = {}
          status_code = super().send_query(rt, json_data, errors)
          #assert False, "NewGQL:lumpy: " + pprint.pformat(json_data)
          if not errors is None and len(errors) > 0 and len(json_data) == 0:
              if self.debug:
                  print(f"NewGQL::send_query: error return, status={status_code}") 
              return status_code
          if self.api_flat_key is not None:
              #assert False, "NewGQL::send_query: " + pprint.pformat(json_data)
              if len(self.api_key_prefix) == 0:
                  regex=f"^{self.api_key_seperator}+"
                  prev_key = self.api_flat_key 
                  self.api_flat_key = re.sub(regex, "", self.api_flat_key)
                  #assert False, f"KEY_CHANGE: {prev_key} -> {self.api_flat_key}"

              flatter_json = self.flatten_json(json_data, self.api_flat_key, seperator=self.api_key_seperator, prefix=self.api_key_prefix)
              if self.assert_post_flat:
                  assert False, f"NewGQL:flat({self.api_flat_key}): " + pprint.pformat(flatter_json)
              #assert False, "NewGQL:flat: " + pprint.pformat(flatter_json)
              if self.debug:
                  print('........ flattened data ..........')
                  pprint.pprint(flatter_json)
              json_reply.clear()
              if self.single_entry_to_dict and \
                 isinstance(flatter_json, list) and \
                 isinstance(json_reply, dict) and \
                 len(flatter_json) == 1:
                  if isinstance(flatter_json[0], dict):
                      flatter_json = flatter_json[0]
                  else:
                      flatter_json = {}
                  # assert False, "single_entry_to_dict: " + pprint.pformat(flatter_json)
              if not errors is None and len(errors) > 0 and \
                 len(flatter_json) == 0:
                  if self.debug:
                      print(f"NewGQL::send_query: ERROR status={status_code} " + \
                            f"len(json_reply)={len(json_reply)} " + \
                            f"type(json_reply)={json_reply.__class__.__name__} " + \
                            f"type(flatter_json)={flatter_json.__class__.__name__}") 
                  return status_code
              #assert False, "NewGQL:flat: " + pprint.pformat(flatter_json)
              update_by_type(json_reply, flatter_json)
          else:
              update_by_type(json_reply, json_data)
          #assert False, pprint.pformat(json_reply)
          if self.debug:
              print(f"NewGQL::send_query: normal return,  status={status_code}") 
          return status_code
          
      def format_results(self, json_dict):
          """
          Overrides parent
          """
          return json_dict['data']
          

class GQLTemplate(RawGQL):
    def __init__(
        self, 
        template_text=None, 
        variables={}, 
        flatpath=None,
        debug=False
     ):
        if not template_text is None:
            self.load_template_text(template_text)
        self._flatpath  = flatpath
        self._variables = variables
        self._debug = debug
        self._flatten_reply = True
        # For unit test debugging, assert after flattening
        self._assert_post_flat = False
        # Normally results are expressed as a list of dicts, but
        # if there is a list of one dict, this flag can be used
        # to return a dict
        self._single_entry_to_dict = False    

    @property
    def flatpath(self):
        return self._flatpath 

    @property
    def variables(self):
        return self._variables 

    @variables.setter
    def variables(self, value):
        if not isinstance(variables, dict):
            raise TypeError
        self._variables = value 

    @property
    def flatten_reply(self):
        return self._flatten_reply

    @flatten_reply.setter
    def flatten_reply(self, value):
        if not isinstance(value, bool):
            raise TypeError
        self._flatten_reply = value
        return self._flatten_reply

    @property
    def assert_post_flat(self):
        return self._assert_post_flat

    @assert_post_flat.setter
    def assert_post_flat(self, value):
        if not isinstance(value, bool):
            raise TypeError
        self._assert_post_flat = value
        return self._assert_post_flat

    @property
    def single_entry_to_dict(self):
        return self._single_entry_to_dict

    @single_entry_to_dict.setter
    def single_entry_to_dict(self, value):
        if not isinstance(value, bool):
            raise TypeError
        self._single_entry_to_dict = value

    def load_template_text(self, text):
         self._template_text = None
         self._template = jinja2.Template(text)
         return True

    def load_template_file(self, filename):
        self._template = None
        self._template_text = None
        if os.path.exists(filename):
            with open(filename) as fh:
                template_text = fh.read()
            self._template = jinja2.Template(template_text)
            self._template_text = template_text
            return True
        return False

    def render_template(self, variables=None):
        """
        Renders previously loaded template using provided variables and checks the output
        for any remaining unpopulated variables.  If template is fully populated, then
        the string is returned; otherwise None is returned
 
        If None is passed for 'variables', the variables (if any) passed to the constructor
        are used
        """
        if self._template is None:
            return None
        if variables is None:
            variables = self._variables
        if variables is None:
            return None
        rendered = self._template.render(variables)
        lines = rendered.splitlines()
        for line in lines:
            matches = re.search(r"\{\{[^\{\}]*\}\}", line)
            if matches is not None:
                return None
        return rendered
      
    def get_reply_fields(self):
        """
        Process the template into a list of allowed field names for
        test conditionals...
        """ 
        def alter_request_edges(self, jdata):
            """
            From the jsonified request template, converts
                "edges" : { "node" :  { "key1" : value1, ... }  }
            to something resembling a reply message body:
                "edges" : [ { "key1" : value, ... } }
            so that flatten_json can be run against it to extract
            valid field names.
            """
            if isinstance(jdata, list):
                for entry in jdata:
                    self._alter_request_edges(entry)
            if isinstance(jdata, dict):
                for key in jdata:
                    if key == "edges":
                        edge_dict = jdata[key]
                        jdata[key] = []
                        for subkey in edge_dict:
                            jdata[key].append(edge_dict[subkey])  
                    self._alter_request_edges(jdata[key])         

        json1 = re.sub(r'([z-zA-z0-9_-]+)(?:\(.*?\))*\s*([\[\{])', r'"\1" : \2', self.template_text)
        json2 = re.sub(r'\.*([a-zA-Z0-9]+)\s*\n', r'"\1" : true,\n', json1)
        json3 = re.sub(r'("[a-zA-Z0-9_-]+"\s*:[^,]+),(\s*\n\s*[\}\]].*)', r'\1\2', json2)
        jdata = json.loads(json3)
        alter_request_edges(jdata)
        jreply = self.flatten_json(jdata, self.flatpath)
        self.reply_fields = [ key for key in jdata[0] ]
        return self._reply_fields 

    def build_query(self):
        reqbody = self.render_template(variables=None)
        if reqbody is None:
            return {}
        return { "query" : reqbody }  
        
    def send_query(self, rt, json_reply, errors=None):
        """
        Overrides parent
        
        json_reply should be a list, even if only one item is expected to
        be returned.  This eases dict versus list confusion at the cost
        of doing only_entry = list[0].  NewGQL.single_entry_to_dict
        can be used to work around this...
        """
        json_data = {}
        status_code = super().send_query(rt, json_data, errors)
        if not errors is None and len(errors) > 0 and len(json_data) == 0:
            if self.debug:
                print(f"NewGQL::send_query: error return, status={status_code}") 
            return status_code
        if self.flatten_reply and \
           self.flatpath is not None:
            flatter_json = self.flatten_json(json_data, self.flatpath, seperator='/', prefix='/')
            if self.assert_post_flat:
                assert False, f"NewGQL:flat({self.api_flat_key}): " + pprint.pformat(flatter_json)
            if self.debug:
                print('........ flattened data ..........')
                pprint.pprint(flatter_json)
            json_reply.clear()
            if self.single_entry_to_dict and \
               isinstance(flatter_json, list) and \
               isinstance(json_reply, dict) and \
               len(flatter_json) == 1:
                if isinstance(flatter_json[0], dict):
                    flatter_json = flatter_json[0]
                else:
                    flatter_json = {}
            if not errors is None and len(errors) > 0 and \
               len(f>latter_json) == 0:
                if self.debug:
                    print(f"NewGQL::send_query: ERROR status={status_code} " + \
                          f"len(json_reply)={len(json_reply)} " + \
                          f"type(json_reply)={json_reply.__class__.__name__} " + \
                          f"type(flatter_json)={flatter_json.__class__.__name__}") 
                return status_code
            update_by_type(json_reply, flatter_json)
        else:
            update_by_type(json_reply, json_data)
        if self.debug:
            print(f"NewGQL::send_query: normal return,  status={status_code}") 
        return status_code

    def format_results(self, json_dict):
        """
        Overrides parent
        """
        return json_dict['data']
