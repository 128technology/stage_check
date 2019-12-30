"""
"""
import importlib

import re
import os
import sys
import getpass
import datetime

import shlex
import subprocess

import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import EntryTest
except ImportError:
    import EntryTest

try:
    from stage_check import Linux
except ImportError:
    import Linux

class Base(object):
  """
  Note that individual tests are unaware of their node context. It is up
  to the invoker to understand that some tests run on the primary node
  and others on the secondary, while still others run on both.
  """
  def __init__(self, test_id, config, args):
      self._debug = args.debug
      self.desc_string = ''
      self._test_id = str(test_id)
      
      self._schema = {}
      self.message_list = [ ]
      self.results = {}
      self.output = None
      self._version = "0.0.0"

      # These are set after creation to give the test context
      # about what has transpired so far (helpful for progressive
      # json output)     
      self.__last_test_id      = 0
      self.__router_index      = 0
      self.__last_router_index = 0

      try:
          self.desc_string = config["Description"]
      except KeyError:
          self.desc_string = "NO DESC PROVIDED"

      self.base_name     = 'AbstractTest'
      self.module_name   = config["TestModule"]
      self.output_suffix = config["OutputModule"]
     
      try:
          self.__enabled = config["Enable"]
      except KeyError:
          self.__enabled = True

      try:
          self.params = config["Parameters"]
      except Exception as e:
          print(f"***********************************")
          print(f"* Test: {type(self).__name__}")
          print(f"* Error validating test parameters ")
          print(f"* EXITING...") 
          print(f"***********************************")
          print(e)
          sys.exit(1)


  def requires_graphql(self):
      return False

  def requires_netconf(self):
      return False

  def resource_greedy(self):
      return False

  def description(self):
      return f'{self.test_id:>2} {self.desc_string}'

  def desc(self):
      return self.desc_string


  @property
  def enabled(self):
      return self.__enabled

  @property
  def debug(self):
      return self._debug

  @property
  def test_id(self):
      return self._test_id

  @property
  def schema(self):
      return self._schema

  @property 
  def version(self):
      return self._version

  @property
  def last_test_id(self):
      return self.__last_test_id

  @last_test_id.setter
  def last_test_id(self, last_test_id):
      self.__last_test_id = last_test_id

  @property
  def router_index(self):
      return self.__router_index

  @router_index.setter
  def router_index(self, router_index):
      self.__router_index = router_index

  @property
  def last_router_index(self):
      return self.__last_router_index

  @router_index.setter
  def last_router_index(self, last_router_index):
      self.__last_router_index = last_router_index

  def apply_default_params(self, default_params):
      params = self.params.copy()

      for param in default_params:
          if not param in params:
             params[param] = default_params[param]

      if self.debug:
          print(f'------ {self.description()}  ------')
          pprint.pprint(params)

      return params

  def create_output_instance(self, module_dict=None):
      """
      Load configured output module
      """
      self.output = None
      output_name_base = "Output" + self.module_name
      output_module_name = output_name_base + self.output_suffix

      if module_dict is None or \
          output_module_name not in module_dict:
          output_module = importlib.import_module(output_module_name)
          if hasattr(output_module, output_module_name):
              if module_dict is not None:
                  module_dict[output_module_name] = output_module
              # print(f"Successfully registered output plugin '{output_module_name}'")
          else:
              print(f"Module '{output_module_name}' has no class; skipping")

      if module_dict is not None:
          output_module = module_dict[output_module_name]              
      output = output_module.create_instance()

      required_base_name = output_name_base + '.Base'
      if output.full_name != required_base_name:
          print(f"Output Module '{output_module_name}' must have parent '{required_base_name}'")
          print(f"Parent is {output.full_name}")
          sys.exit(1)

      self.output = output      

  def run(self):
      """
      Abstract test template
      """
      return -1

  def exclude_flat_entry(self, entry, excludes):
      """
      Compare flattened list entry with special node_type and
      node_name entries against a list of exlusion dictionaries

      If the extry matches, it should be exluded from the test
      performed on the list.

      Note that a missing key from the entry will cause the
      exclusion rule to fail, and thus the test should be
      peformed... (consider just throwing an exception)
      """
      if entry is None:
          return True
      entry_excluded=False
      for exclude in excludes:
          excluded=True
          for exclude_key in exclude:
              if not exclude_key in entry or \
                 entry[exclude_key] != exclude[exclude_key]:
                  excluded=False
                  break
          if self.debug:
              pprint.pprint(exclude)
              print(f'Exclude: {excluded}')
          if excluded:
              entry_excluded=True
              break
      return entry_excluded 

  def eval_tests(self, flattened_json, entry_tests): 
      """
     Process test entries on the fly.
      """
      eval = EvalTest.eval(self.debug)
      for entry in flattened_json:
           return_status = test_entry()
           if self.ouput is not None:
               self.output.oproctest_match(entry) 

  def eval_tests(self, node, test_list, default_result):
      """
      Evaluate a series of tests against the provided node
      A node should be an entry in the list of json 
      objects for testing (e.g.network interfaces, device interfaces etc.)
      """
      if self.debug:
          print(f'-------  start eval_tests  ---------')
          pprint.pprint(node)
      result = default_result
      entry_text_result='?'
      for entry in test_list:
          if self.debug:
              entry_str = pprint.pformat(entry)
              print(f'-------  start eval_tests  ---------')
              print(f'{entry}')
          for key in entry:
              if key == "status":
                  continue
              match = self.test_key_value(node, key, entry[key])
              if match is None or \
                 match is False:
                  break
          if self.debug:
              print(f'-------Result={result}--------------')
          if match is not None and \
             match is True and \
             "status" in entry:
              entry_text_result = entry["status"]
              result = Output.text_to_status(entry_text_result)
              break           
      if self.debug:
          print(f'*******************************')
          print(f' eval_tests: FINAL RESULT {entry_text_result}({result})')
          print(f'*******************************')
            
      return result

  def test_key_value(self, node, key, value):
      """
      node is a dictionary to look up a value
      for a nested diectionary. 
      """
      try:
          key_list = key.split(".")
          for subkey in key_list:
              if self.debug:
                  nodestr = pprint.pformat(node)
                  print (f'test_key_value: {nodestr} -> subkey={subkey}')
              node = node[subkey]
      # Consider not catching this here to make it
      # more obvious to the caller...
      except (KeyError, TypeError) as e:
          return None
      if self.debug:
          print (f'test_key_value: {key} == {value}?')
      return (node == value)

      
  def test_info(self, local_info, router_context):
      info={}

      try:
          dt = datetime.datetime.now()
          info["DateTime"]          = dt
          #info["node_type"]         = router_context.node_type()
          info["StageCheckVersion"] = "1.0.0"
          info["TestModule"]        = self.__class__.__name__
          info["TestVersion"]       = self.version
          info["TestDescription"]   = self.desc()

          info["TestIndex"]         = int(self.test_id)
          info["TestIndexLast"]     = self.last_test_id
          info["RouterIndex"]       = self.router_index
          info["RouterIndexLast"]   = self.last_router_index

          info["InvokingRouter"]    = local_info.get_router_name()
          info["InvokingNode"]      = local_info.get_node_name()
          info["InvokingRole"]      = local_info.get_node_type()
          info["Router"]            = router_context.get_router()
          """
          info["Node"]              = router-context.get_node_by_type(node_type)
          info["NodeType"]          = node_type
          info["Asset"]             = router-context.get_asset_by_type(node_type)
          info["SWVersion"]         = router_context.get_version_by_type(node_type)
          """
      except Exception as e:
          print(e)
          pass

      # pprint.pprint(info)
      return info

  def test_end_by_status(self, status_list = []):
      """
      Perform whatever action occurs at test_end() except
      only if self.status matches an entry in the passed list
      
      @status_list -- List of statuses to natch
      """
      self.output.test_end_by_status(status_list)

 
class GraphQL(Base):
  """
  Base class for GraphQL tests
  """
  class ReplyStatus(object):
    """
    Simplified Server / API status...
    """
    def __init__(self):
        self._server_code = 200
        self._error_list  = []
  
    @property
    def error_list(self):
        return self._error_list

    @error_list.setter
    def error_list(self, value):
        if isinstance(value, list):
            self._error_list.extend(value)
    
    @property
    def server_code(self):
        return self._server_code
  
    @server_code.setter
    def server_code(self, value):
        self._server_code = value

  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)

  def process_gql_status(self, query_status, errors=None):
      error_list=[]
      if errors is not None:
          for entry in errors:
              if "message" in entry and \
                 not entry["message"] in error_list:
                  error_list.append(entry["message"])
      if query_status is None or \
         query_status > 299 or \
         len(error_list) > 0:
          self.output.graphql_error(query_status, error_list)
          return False
      return True

  def send_query(self, gql_node, gql_token, json_reply, status=None):
      errors=[]
      query_status = gql_node.send_query(gql_token, json_reply, errors)
      if status is not None:
          status.server_code = query_status
          status.error_list  = errors
      return self.process_gql_status(query_status, errors)
      

  def _workaround_graphql_api(self, intf_list):
      """
      Works around a problem / bug with the graphql API not always returning state
      information for a L2 HA network-interface.
      """
      statemap = {}
      statekey=''
      for entry in intf_list:
          try:
              sharedPhysAddr = entry['router/nodes/deviceInterfaces/sharedPhysAddress']
              if sharedPhysAddr == '':
                  continue
              statekey = sharedPhysAddr + ':' + entry['name']
          except (KeyError, TypeError):
              continue
          if 'state' in entry and \
              entry['state'] is not None:
              statemap[statekey] = entry['state']
      for entry in intf_list:
          try:
              sharedPhysAddr = entry['router/nodes/deviceInterfaces/sharedPhysAddress']
              if sharedPhysAddr == '':
                  continue
              statekey = sharedPhysAddr + ':' + entry['name']
              if 'state' not in entry or \
                  entry['state'] is None:
                  entry['state'] = statemap[statekey]
          except (KeyError, TypeError):
              continue


class Linux(Base, Linux.Callbacks):
  """
  Base Class for tests using linux commands
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)
      try:
          self.__timeout = config["Timeout"]
      except KeyError:
          pass

  @property 
  def timeout(self):
      return __timeout

  def run_linux_progress(self, message):
      self.output.progress_display(message, self.fp)

  def line_to_message(self, line, regex=None, message_format='No Format Provided'):
      """
      If provided, The format is applied to matching groups from regex as
      applied to line.   
      """
      output_string = message_format
      if regex is not None:
          matches = re.search(regex, line, re.MULTILINE|re.DOTALL)
          if matches is not None:
              index = 1
              while index < 10:
                  try:
                      dest = '{' + str(index) + '}'
                      source = matches.group(index)
                      output_string = output_string.replace(dest, source)
                  except IndexError:
                      pass
                  index += 1
      return output_string


  def convert_to_json(self, text_list, pattern, regex_groups, json_data):
      """
      Derived classes can override this with their own conversion routines
      See TestT1Detail
      """
      json_data.clear()
      return json_data
 
  def run_linux_json(self, 
                     local_info, 
                     router_context, 
                     node_type, 
                     command, 
                     patterns, 
                     json_data, 
                     error_lines, 
                     fp):
      """
      """
      # run the command...
      candidate_lines = []
      shell_status = self.run_linux(local_info, router_context, node_type, command, 
                                    None, candidate_lines, error_lines, fp)

      # convert output to json...
      if len(error_lines) == 0:
         self.convert_to_json(candidate_lines, patterns, json_data)

      return shell_status


  def run_linux(self, local_info, router_context, node_type, command, 
                candidate_regex, candidate_lines, error_lines, fp):
          """
          """
          salt_error_indicators = []
          salt_error_indicators.append('^\s*Minion did not return.')
          salt_error_indicators.append('^\s*No minions matched the target.')

          asset_id = router_context.get_asset_by_type(node_type)

          if  asset_id is None or asset_id == '':
              error_lines.append(f"Missing asset info for {node_type} node")
              return 0 

          candidate_lines.clear()
          linux_command = command
          if local_info.get_node_type() == 'conductor':
              linux_command = 't128-salt ' + asset_id + " cmd.run '" + command + "'"

          if self.debug:
              if candidate_regex is not None:
                  print(f'Candidate Regex: {candidate_regex}')
              print(f'Linux Command:   {linux_command}')
              print(f'Asset ID:        {asset_id}')

          # subprocess.DEVNULL is python 3.3+ only
          self.output.progress_display(f"Run '{linux_command}'...", fp=fp)
          pipe = subprocess.Popen(shlex.split(linux_command),
                                  stdin=open(os.devnull, 'rb'),
                                  bufsize=0,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL,
                                  close_fds=True)
          for line in iter(pipe.stdout.readline, b''):
              bline = line.rstrip()
              xline = bline.decode('utf-8') 
              if self.debug:
                  print(f'Consider: {xline}')
              if candidate_regex is not None and \
                 candidate_regex != '' and \
                 not re.search(candidate_regex, xline):
                  continue
              candidate_lines.append(xline)
              if self.debug:
                  print(f'*Matched: {xline}')
              for indicator in salt_error_indicators:
                  if re.search(indicator, xline):
                      error_lines.append(xline.lstrip())

          if self.debug:
              pprint.pprint(candidate_lines)

          return_code = pipe.poll()
          return return_code

  def check_user(self, required_user):
      message = None
      status = Output.Status.OK
      user = getpass.getuser()
      if user != required_user:
          status=Output.Status.WARN
          self.output.run_as_wrong_user(user, status=status)
      return status

