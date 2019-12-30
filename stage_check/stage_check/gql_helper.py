"""
GraqhQL Helper Classes
"""
import os
import sys

import requests
import json
import pprint
import getpass

from requests.packages.urllib3.exceptions import InsecureRequestWarning

GRAPHQL_API_HOST   = '127.0.0.1'
GRAPHQL_API_URL    = '/api/v1/graphql'
GRAPHQL_LOGIN_URL  = '/api/v1/login'
GRAPHQL_LOCAL_PORT = 31516 

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
    
  def get_top_level(self):
      return True

  def format(self):
      return self.raw_string

  def build_query(self):
      return { "query" : '{' + self.format() + '}' }

  def format_results(self, json_dict):
      return json_dict['data']

  def send_query(self, rt, json_reply, errors=None):
      if self.get_top_level() is False:
         return

      # Don't validate rhe server's cert
      requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

      url = 'https://' + GRAPHQL_API_HOST
      if rt is None:
          url = url + f":{GRAPHQL_LOCAL_PORT}"
      url = url + GRAPHQL_API_URL


      headers = {}
      if rt is not None:
          headers['Authorization'] = 'Bearer %s' % rt.get_token()
      headers['Content-Type']  = 'application/json'

      files = {}
      data  = {}

      #json_body={ "query": self.build_query() }
      json_body = self.build_query()
      files['json'] = (None, json.dumps(json_body), 'application/json')

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
              json_reply.update(self.format_results(resp_as_json))
          except (KeyError, IndexError) as e:
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

  def flatten_json(self, node, stop_prefix, seperator='/', prefix='router', depth=0):
      output_list = []
      fields_noop = {}

      def unedgify(edgy_dict):
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
          if edgy_dict is not None:
              if 'edges' in edgy_dict:
                  edgy_dict = edgy_dict['edges']
                  index = 0
                  while index < len(edgy_dict):
                      if 'node' in edgy_dict[index]:
                          edgy_dict[index] = edgy_dict[index]['node']
                      unedgify(edgy_dict[index])
                      index += 1
                  #print(f'#####################')
                  #pprint.pprint(edgy_dict)
                  #print(f'#####################')
          return edgy_dict

      def _flatten_json(node, stop_prefix, seperator='.', prefix='router', depth=0):
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
          skip_list = [ 'edges', 'node' ]

          node_type = type(node)
          if node_type == list:
              for entry in node:
                  sub_list, sub_fields  = _flatten_json(entry, stop_prefix, seperator, prefix, depth)
                  node_list = node_list + sub_list
                  field_dict.update(sub_fields)
          elif node_type == dict:
              for key in node:
                  prefstr = prefix
                  if not key in skip_list:
                      prefstr = prefix + seperator + key
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
              #print(f'PREFIX:{prefix} STOP_PREFIX:{stop_prefix}')
              #pprint.pprint(node)
              if stop_prefix in key:
                  key = prefix.split(seperator)[-1]
                  #print(f'KEY NOW: {key}')
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
      return json_dict['data'][self.name]['edges'][0]

