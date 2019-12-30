"""
"""
import pprint
import json

try:
    from stage_check import gql_helper
except ImportError:
    import gql_helper

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest

try:
    from stage_check import EntryTester
except ImportError:
    import EntryTester


def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance
   
    @test_id - test index number
    @config  - test parameters from configuration 
    @args    - command line args
    """
    return TestDeviceState(test_id, config, args)


class TestDeviceState(AbstractTest.GraphQL):
  """
  Test device interface state
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)

  def requires_grapqhl(self):
      """
      Override
      """
      return True

  def get_params(self):
      # apply defaults
      default_params = {
          "status_tests"      : [],
          "default_status"    : Output.Status.OK,
          "exclude_tests"     : [],
          "device-interfaces" : []
      }
     
      params = self.apply_default_params(default_params)
      return params

  def _add_peer_device_info(self, dev_data):
      """
      Build up a database of data[device][node_type][info_key]
      which is then applied to the 'other' node so rules like:

      name = 'fubar' && state.operationalStatus != 'OPER_UP' && \
             peer_op_status != 'OPER_UP' => FAIL
       :
      name != 'fubar' && name != ... state.operationalStatus != 'OPER_UP'

      A database is also added which allows any entry to look up the 
      state of any other entry by using states.secondary.t1__backup.op_status          
      """
      dev_states = {}
      for dev in dev_data:
          if self.debug:
               print(f"_add_peer_device_info: processing {dev['name']}")
          try:
              dev_name = dev["name"].replace('-', '__')
              node_type = dev["node_type"]
              dev_admin_status = ""
              dev_ha_status = ""
              dev_op_status = ""
              if isinstance(dev["state"], dict):
                  if "operationalStatus" in dev["state"]:
                      dev_op_status = dev["state"]["operationalStatus"]
                  dev["op_status"] = dev_op_status
                  if "adminStatus" in dev["state"]:
                      dev_admin_status = dev["state"]["adminStatus"]
                  dev["admin_status"] = dev_admin_status
                  if "redundancyStatus" in dev["state"]:
                      dev_ha_status = dev["state"]["redundancyStatus"]
                  dev["ha_status"] = dev_ha_status
              if not node_type in dev_states:
                  dev_states[node_type] = {}
              if not dev_name in dev_states[node_type]:
                  dev_states[node_type][dev_name] = {}
              dev_states[node_type][dev_name]["op_status"] = dev_op_status
              dev_states[node_type][dev_name]["admin_status"] = dev_admin_status
              dev_states[node_type][dev_name]["ha_status"] = dev_ha_status
              dev["dStates"] = dev_states
              if self.debug:
                  print(f"_add_peer_device_info: dev_states[{node_type}][{dev_name}]['peer_op_status']={dev_op_status}")
                  print(f"_add_peer_device_info: dev_states[{node_type}][{dev_name}]['peer_admin_status']={dev_admin_status}")
                  print(f"_add_peer_device_info: dev_states[{node_type}][{dev_name}]['peer_ha_status']={dev_ha_status}")
          except KeyError as e:
              #assert False, f"_add_peer_device_info[{dev['name']}]: {e} {e.__class__.__name__}"
              assert False, f"_add_peer_device_info[dn={dev_name}]: " + \
                             f"{e} {e.__class__.__name__}\n DATA:\n {json.dumps(dev_data, indent=2)}"
              if self.debug:
                  print(f"_add_peer_device_info[{dev['name']}]: {e} {e.__class__.__name__}")
              continue
      for dev in dev_data:
          try:
              dev["peer_op_status"] = ""
              dev["peer_admin_status"] = ""
              dev["peer_ha_status"] = ""
              dev_name  = dev["name"].replace('-', '__')
              node_type = dev["node_type"]
              for ntype in dev_states:
                  if ntype != node_type: 
                      other_node = dev_states[ntype]
                      #assert False, f"nt: {ntype} n_t: {node_type} dn: {dev_name} " + pprint.pformat(other_node)
                      if dev_name in other_node:
                          other_dev  = other_node[dev_name]
                          #assert False, f"nt: {ntype} n_t: {node_type} dn: {dev_name} " + pprint.pformat(other_dev)
                          dev["peer_op_status"] = other_dev["op_status"]
                          dev["peer_admin_status"] = other_dev["admin_status"]
                          dev["peer_ha_status"] = other_dev["ha_status"]
                          #assert False, f"node_type: {node_type}" + pprint.pformat(dev)
                          #assert False, f"nt: {ntype} n_t: {node_type} dn: {dev_name} " + pprint.pformat(dev)
                      break
          except KeyError as e:    
              assert False, f"_add_peer_device_info[dn={dev_name}],nt={node_type}]: " + \
                             f"{e} {e.__class__.__name__}\n DATA:\n {json.dumps(dev_data, indent=2)}"
              if self.debug:
                  print(f"_add_peer_device_info[{dev['name']}]: {e} {e.__class__.__name__}")
              continue
                    
      #assert False, pprint.pformat(dev_data)
      return dev_states

  def run(self, local_info, router_context, gql_token, fp):
      """
      This test uses the gql engine to get device state state
      """
      # Process test parameters
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      params = self.get_params()
      self.init_stats()
      # TODO either keep and implement as a parameter or toss
      include_list = params["device-interfaces"]
      entry_tests = params["entry_tests"]

      # GraphQL Preperation
      qr = gql_helper.NewGQL(
          api_name="allRouters", 
          api_args={"name" : router_context.get_router()},
          api_fields=[ "name" ],
          api_has_edges=True, 
          debug=self.debug
      )
      qn = gql_helper.NewGQL(
          api_name="nodes", 
          api_fields=[ "name" ],
          api_has_edges=True,
          debug=self.debug
      )
      api_args_data=None,
      if len(include_list) > 0:
          api_args_data = { "names" : include_list } 
      qd = gql_helper.NewGQL(
          api_name="deviceInterfaces", 
          api_fields=[ "name", "state { operationalStatus adminStatus redundancyStatus } forwarding" ],
          api_has_edges=True, 
          debug=self.debug
      )
      qr.add_node(qn)
      qn.add_node(qd)

      flatter_json=[]
      qr.api_flat_key = 'allRouters/nodes/deviceInterfaces'
      if not self.send_query(qr, gql_token, flatter_json):
          return self.output.test_end(fp)

      router_context.set_allRouters_node_type(flatter_json)
      dev_states = self._add_peer_device_info(flatter_json)          
      router_context.set_device_states(dev_states)
 
      #assert False, "DevState: " + pprint.pformat(flatter_json)
      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)

      # Run test / process results
      engine = EntryTester.Parser(debug=self.debug)
      for entry in flatter_json:
          if engine.exclude_entry(entry, params["exclude_tests"]):
              continue
          test_status = engine.eval_entry_by_tests(entry, entry_tests)
          router_context.add_entry_tags(test_status, entry)
          Output.update_stats(self.stats, test_status, entry=entry, inc_total=True)
          self.output.proc_dev_result(test_status, entry)

      self.output.proc_test_result(entry_tests, self.stats)
      status = self.output.stats_to_status_value(self.stats)
      self.output.status = status

      # status_text = Output.status_to_text(status)
      # assert False, f"{status_text}: " + self.output.message + "\n" + \
      #             pprint.pformat(self.output.message_list)

      return self.output.test_end(fp)

