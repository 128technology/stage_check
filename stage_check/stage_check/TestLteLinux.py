"""
This module should never be run directly from a test.  It is used for other tests
to inherit from!!!
"""
import pprint
import ipaddress
import json

try:
    from stage_check import gql_helper
except ImportError:
    import gql_helper

try:
    from stage_check import Linux
except ImportError:
    import Linux

try:
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest

try:
    from stage_check import EntryTester
except ImportError:
    import EntryTester

try:
    from stage_check import Output
except ImportError:
    import Output

def make_device_key(node_name=None, device=None):
    """
    In order to support entries from multiple nodes, a device key must
    include the node name

    Note that this is deliberately not a method so that if so desired one 
    could do TestLteInfo.make_device_key(node_name=mynode, device=mydevice)
    """
    if node_name is None:
       node_name="<NONE>"
    if device is None:
       device="<NONE>"
    return node_name + "|" + device

class Base(AbstractTest.GraphQL, AbstractTest.Linux, EntryTester.MatchFunction):
  """
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)
      self.matching_entries = []

  def requires_grapqhl(self):
      """
      Override
      """
      return True

  def get_params(self):
      """
      Some of these defaults (e.g. node_type) should be caught in
      the schema check, if they are missing...
      """
      default_params = {
          "exclude_tests"    : [], 
          "namespace_prefix" : "lte-ns-",
          "script"           : "lte-state"
      }

      params = self.apply_default_params(default_params)
      return params

  def process_match(
      self,
      entry,
      test_index,
      test,
      defaults
      ):
      """
      Invoked every time an entry_test sucessfully matches an entry.
      """
      out_strings = []
      format_string = ''
      # assert False, pprint.pformat(test)
      if "test_exception" in entry and \
          entry["test_exception"] is not None:
          out_strings.append(entry["test_exception"])

      if "format" in test:
          format_string = test["format"]
      elif "format" in defaults:
          format_string = defaults["format"]
      else:
          return
      out_strings.append(Output.populate_format(entry, format_string))
      
      list_key = Linux.LteFiles.MESSAGE_LIST_KEY
      if not list_key in entry:
          entry[list_key] = []
      for out_string in out_strings:                      
          if not out_string in entry[list_key]:
              entry[list_key].append(out_string)

      if not entry in self.matching_entries:
          self.matching_entries.append(entry)

  def linux_command(self):
      assert False, "TestLteLinux.linux_command(): Must be overriden in child class!"

  def run(self, local_info, router_context, gql_token, fp):
      """
      This test scans LTE interfaces, or find all which
      exist and match the test criteria against them.
      """
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      params = self.get_params()

      # First, query allRouters...nodes...deviceInterfaces... to determine
      # which are LTE
      """
      API    = allRouters
      Fields = name
      """
      device_exclude_tests = params["exclude_tests"]
      self.output.progress_start(fp)

      if self.check_user() != Output.Status.OK:
          return self.output.test_end(fp)

      devint_state = "state { operationalStatus adminStatus redundancyStatus }"
      qr = gql_helper.NodeGQL("allRouters", ['name'], [ router_context.get_router() ], debug=self.debug)
      qn = gql_helper.NodeGQL("nodes", [ 'name' , 'assetId' ])
      qd = gql_helper.NodeGQL("deviceInterfaces", [ 'name', 'type', 'targetInterface',  devint_state ])
      qr.add_node(qn)
      qn.add_node(qd)

      json_reply={}
      if not self.send_query(qr, gql_token, json_reply):
          return self.output.test_end(fp)

      flatter_json = qr.flatten_json(json_reply, 'allRouters/nodes/deviceInterfaces', prefix='')
      di_name_key='name'

      router_context.set_allRouters_node_type(flatter_json)

      self._workaround_graphql_api(flatter_json)

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)

      devices128 = {}
      for entry in flatter_json:
          try:
              if entry["type"].lower() == "lte":
                  device_key = make_device_key(
                            node_name=entry["node_name"], 
                            device=entry["targetInterface"]
                        )
                  devices128[device_key] = entry
          except KeyError:
              pass

      engine = EntryTester.Parser(debug=self.debug)

      linux_command = self.linux_command()

      json_data = []
      error_lines = []
      namespace_regex = "lte-ns-[0-9]+"
      device_regex = "wwp.*?[0-9]+"

      self.fp = fp
      shell_status = linux_command.run_linux_args(
          router_context,
          params["node_type"],
          namespace_regex,
          device_regex,
          error_lines,
          json_data
      )
      self.fp = None

      if len(error_lines) > 0:
          if self.debug:
              print("-------- TestLteLinux Shell Error Lines ---------")
              pprint.pprint(error_lines)
          self.output.proc_run_linux_error(shell_status, error_lines[0])
          return self.output.test_end(fp)

      stats = {}
      Output.init_result_stats(stats)
      stats["exclude_count"] = 0
      stats["linux_count"] = len(json_data)
      stats["t128_count"] = len(devices128)
      stats["t128_full_count"] = len(flatter_json)
      stats["linux_no_t128"] = 0 
      stats["t128_no_linux"] = 0
      stats["bad_json"] = 0

      #assert False, f"JSON_DATA: {json.dumps(json_data, indent=2)}"

      linux_devs = {}
      self.matching_entries.clear()
      for devintf in json_data:
          if self.debug:
              print(f'%%% process LTE Device %%%')
              pprint.pprint(devintf)

          #assert False, "%%%%% Jsonified Linux Entry %%%%%:\n"  + pprint.pformat(devintf)
          try:
               target_device = devintf["linux_device"]
               node_name     = devintf["node_name"]
          except KeyError:
               self.output.proc_missing_json(devintf)
               stats["bad_json"] += 1
               continue
  
          device_key = make_device_key(node_name=node_name, device=target_device)
          linux_devs[device_key] = devintf

          if engine.exclude_entry(devintf, device_exclude_tests):
              stats["exclude_count"] += 1
              continue

          #  Add 128T config data to the linux ip netns exec entry...
          try:
              dev128 = devices128[device_key]
          except:
              stats["linux_no_t128"] += 1
              if not devintf in self.matching_entries:
                  self.matching_entries.append(devintf)
              self.output.proc_no_128_config(devintf)
              continue
          devintf["name"] = dev128["name"]

          if engine.exclude_entry(devintf, device_exclude_tests):
              stats["exclude_count"] += 1
              continue

          engine = EntryTester.Parser(debug=False)
          engine.eval_tests_by_entry(devintf, params['entry_tests'], self)

      # 128 devices without matching linux info...
      #assert False, pprint.pformat(linux_devs)
      #assert False, pprint.pformat(devices128)
      for device_key in devices128:
          if not device_key in linux_devs:
              stats["t128_no_linux"] += 1
              devintf = devices128[device_key]
              if not devintf in self.matching_entries:
                  self.matching_entries.append(devintf)
              self.output.proc_no_linux_device(
                  devices128[device_key]
              )

      status = self.output.status
      if len(self.matching_entries) > 0 or \
         stats["t128_no_linux"] > 0 or \
         stats["linux_no_t128"] > 0:
          status = Output.Status.FAIL
      else:
          status = Output.Status.OK

      if stats["linux_count"] == 0 and \
         stats["t128_count"] == 0:
          status = Output.Status.WARN

      self.output.proc_test_result(
          status, 
          json_data, 
          self.matching_entries, 
          devices128, 
          stats)
      return self.output.test_end(fp)
