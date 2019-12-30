"""
"""
import pprint
import ipaddress

try:
    from stage_check import gql_helper
except ImportError:
    import gql_helper

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


def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance
   
    @test_id - test index number
    @config  - test parameters from, config 
    @args    - command line args
    """
    return TestGatewayPing(test_id, config, args)


class TestGatewayPing(AbstractTest.GraphQL):
  """
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)

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
         "device-interfaces"         : [],
         "network-interfaces"        : [],
         "sequence"                  : 1,
         "size"                      : 100,
         "timeout"                   : 2,
         "identifier"                : 68686868,
         "iterations"                : 10,
         "destination-ip"            : '',
         "address_mode"              : "auto",
         "network_exclude_tests"     : [ ],
         "address_exclude_tests"     : [ ],
         "omit_gateway"              : False,
         "max_single_response_time"  : 0.0,
         "max_response_overages"     : 0, 
         "max_average_response_time" : 0.0,
         "max_ping_failures"         : 3,
         "omit_text_on_passing"      : False,
         "red_text_for_ping_fails"   : False,
         "fail_status"               : "FAIL"
      }

      params = self.apply_default_params(default_params)

      # for backwards compatibility: params["node_type"] now replaces
      # network_exclude_tests with an extry excluding the opposite
      # node type.  
      try:
          node_type = params["node_type"] 
          if node_type == 'primary':
              params["network_exclude_tests"].append("node_type == 'secondary'")
          elif node_type == 'secondary':
              params["network_exclude_tests"].append("node_type == 'primary'")

          address_type = params["address-type"]
          if address_type == 'static':
              params["address_exclude_tests"] = [ "address_type == 'dynamic'" ]
          elif node_type == 'secondary':
              params["address_exclude_tests"] = [ "address_type == 'static'" ]
      except KeyError:
          pass

      return params

  def valid_address(self, address):
      """
      A valid address must be a dictionary where:
         address["ipAddress"] exists,
         is a string,
         and is not:
           - ''
           - '<empty>'
      """
      bad_ip_values = [ "", "<empty>" ]
      if not isinstance(address, dict):
          return False
      try:
          ip_address = address["ipAddress"]
          for ip_value in bad_ip_values:
              if ip_address == ip_value:
                  return False
      except (KeyError, TypeError, ValueError) as e:
          return False
      return True
 
  def valid_addresses(self, addresses):
      """
      If one or more addresses is valid then the address list
      is considred valid...
      """
      if not isinstance(addresses, list):
          return False
      if len(addresses) == 0:
          return False
      valid_address = False
      for address in addresses:
          if self.valid_address(address):
              valid_address = True
              break
      return valid_address

  def set_address_type(self, addresses, typestr):
      if not isinstance(addresses, list):
          return
      for addr in addresses:
          if not isinstance(addr, dict):
              addr["address_type"] = typestr
      
  def get_address_list(self, entry):
      addresses = None
      typestr   = None
      try:
          if self.valid_addresses(entry["addresses"]):
              addresses = entry["addresses"]
              typestr = "static"
      except KeyError: 
          pass
      if addresses is None:
          try:
              if self.valid_addresses(entry["state"]["addresses"]):
                  addresses = entry["state"]["addresses"]
                  typestr = "dynamic"
          # if entry["state"] is None, TypeError exception is raised 
          except (KeyError, TypeError) as e:
              pass
      self.set_address_type(addresses, typestr)
      return addresses      

  long_state_key = 'allRouters/nodes/deviceInterfaces/state'

  def is_interface_down(self, netintf, stats, address_entry=None):
      is_down = False
      op_status_key = self.long_state_key + '/' + 'operationalStatus'
      admin_status_key = self.long_state_key + '/' + 'adminStatus'
      if op_status_key in netintf:
          oper_status = netintf[op_status_key]
          if oper_status != 'OPER_UP':
              self.output.proc_cannot_ping_dev_status(netintf, address_entry, oper_status)
              stats["address_dev_status"] += 1
              is_down = True
      elif admin_status_key in netintf:
          admin_status = netintf[admin_status_key]
          if admin_status != 'ADMIN_UP':
              self.output.proc_cannot_ping_dev_status(netintf, address_entry, admin_status)
              stats["address_dev_status"] += 1
              is_down = True
      else:
          # Continue as there is no operationalStatus to evaluate
          self.output.proc_cannot_ping_dev_status(netintf, address_entry, "NO_DEV_STATUS")
      return is_down
      
          
  def run(self, local_info, router_context, gql_token, fp):
      """
      This test uses the gql engine to learn gateway IP addresses
      and ping them, processing the latency results.

      Note apparently timeout is in seconds and not ms as suggested
      by grapql documentation
      """
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      params = self.get_params()

      # First, query allRouters...nodes...networkInterfaces... to determine
      # the router and gateway
      """
      API    = allRouters
      Fields = name
      """
      intf_list = params["network-interfaces"]
      dev_list  = params["device-interfaces"]
      network_exclude_tests = params["network_exclude_tests"]
      address_exclude_tests = params["address_exclude_tests"]

      # backwards compatibility
      try:
          if params["static-address"]:
              address_mode = "static"
          else:
              address_mode = "dynamic"
      except KeyError:
          address_mode = params["address_mode"]

      if self.debug:
          print(f'------ Network Interfaces to Process  ------')
          pprint.pprint(intf_list)

      devint_fields = "state { operationalStatus adminStatus redundancyStatus }"
      qr = gql_helper.NodeGQL("allRouters", ['name'], [ router_context.get_router() ], debug=self.debug)
      qn = gql_helper.NodeGQL("nodes", [ 'name' , 'assetId' ])
      qd = gql_helper.NodeGQL("deviceInterfaces", [ 'name', 'type', 'sharedPhysAddress', devint_fields ], dev_list)
      qi = gql_helper.NodeGQL("networkInterfaces", ['name', 'type', 'state { addresses { ipAddress gateway prefixLength } }'], intf_list)
      qa = gql_helper.NodeGQL("addresses", ['ipAddress', 'gateway', 'prefixLength'])
      qr.add_node(qn)
      qn.add_node(qd)
      qd.add_node(qi)
      qi.add_node(qa)

      json_reply={}
      if not self.send_query(qr, gql_token, json_reply):
          return self.output.test_end(fp);

      """
      WARNING if prefix is the current default of '/', the expression parser will see 
              /allRouters/nodes/deviceInterfaces/networkInterfaces as an attempt to
              do divsion and fail with little indication as to why.
      """
      flatter_json = qr.flatten_json(json_reply, 'allRouters/nodes/deviceInterfaces/networkInterfaces', prefix='')
      #assert False, "GatewayPing: " + pprint.pformat(flatter_json)

      router_context.set_allRouters_node_type(flatter_json, node_name_key='allRouters/nodes/name')

      self._workaround_graphql_api(flatter_json)

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)

      engine = EntryTester.Parser(debug=self.debug)
      self.output.progress_start(fp)

      gateway_success_count = 0
      gateway_fail_count    = 0
      gateway_count         = 0

      stats = {}
      Output.init_result_stats(stats);
      stats["entry_count"] = len(flatter_json)
      stats["address_count"] = 0
      stats["address_total_count"] = 0
      stats["exclude_count"] = 0
      stats["address_exclude_count"] = 0
      stats["address_pass"] = 0
      stats["address_fail"] = 0
      stats["address_no_gateway"] = 0  
      stats["address_dev_status"] = 0  

      for netintf in flatter_json:
          if self.debug:
              print(f'%%% process NI for Ping %%%')
              pprint.pprint(netintf)

          if engine.exclude_entry(netintf, network_exclude_tests):
              stats["exclude_count"] += 1
              continue

          address = ''
          gateway = ''

          try:
              addresses = self.get_address_list(netintf)
              if self.debug:
                  print(f'%%%% process address for Ping %%%%')
                  pprint.pprint(addresses)

              # addesses can be None if interface is down
              if addresses is None:
                  if self.debug:
                      print(f'*** Skipping empty addresses...')
                  if self.is_interface_down(netintf, stats):
                      break
                  else:
                      continue

              egress_interface = netintf["name"]
              stats["address_total_count"] += len(addresses)
              for address_entry in addresses:
                  if engine.exclude_entry(address_entry, address_exclude_tests):
                      stats["address_exclude_count"] += 1
                      continue

                  stats["address_count"] += 1
                  address = address_entry['ipAddress']
                  gateway = address_entry['gateway']
                  prefix_length = int(address_entry['prefixLength'])
                  address_entry["target"] = gateway
                  dest_ip = None

                  if gateway is None:
                      # hack for ipv4 only!
                      hack = int(ipaddress.IPv4Address(address))
                      if prefix_length == 31:
                          gateway_hack = hack&0xfffffffe|-(hack&0x01)+1
                          gateway_ip = ipaddress.IPv4Address(gateway_hack)
                          dest_ip = str(gateway_ip)
                          gateway = ''
                          address_entry["target"] = dest_ip
                      elif prefix_length == 30:
                          gateway_hack = hack&0xfffffffc|-(hack&0x03)+3
                          gateway_ip = ipaddress.IPv4Address(gateway_hack)
                          dest_ip= str(gateway_ip)
                          gateway = ''
                          address_entry["target"] = dest_ip
                      else:
                          if params["destination-ip"] == '':
                              self.output.proc_cannot_ping_no_gateway(netintf, address_entry)
                              stats["address_no_gateway"] += 1
                              continue
                          else:
                              gateway = ''

                  if self.is_interface_down(netintf, stats, address_entry):
                      break

                  # Invoke Graphql PING API
                  if dest_ip is None:
                      if params["destination-ip"] != '':
                          dest_ip = params["destination-ip"]
                          address_entry["target"] = dest_ip
                          if params["omit_gateway"] == True:
                              gateway = ''
                      else:
                          dest_ip = gateway

                  size    =  params["size"]
                  timeout = params["timeout"]
                  seqno   = params["sequence"]
                  router  = netintf["allRouters/name"]
                  node    = netintf["node_name"]
                  identifier = params["identifier"]

                  address_entry["total_response_time"] = float(0)
                  address_entry["average_response_time"] = float(0)
                  address_entry["ping_success_count"] = 0
                  address_entry["ping_fail_count"] = 0
                  address_entry["test_gateway"] = gateway
                  address_entry["test_destination"] = dest_ip
                  address_entry["ping_count"] = 0
                  address_entry["response_time_overages"] = 0

                  ping_count = 0
                  while ping_count < params["iterations"]:
                      argstr  = f'routerName: "{router}"'
                      argstr += f', nodeName: "{node}"'
                      argstr += f', identifier: {identifier}'
                      argstr += f', egressInterface: "{egress_interface}"'
                      if dest_ip != '':
                          argstr += f', destinationIp: "{dest_ip}"'
                      if gateway != '':
                          argstr += f', gatewayIp: "{gateway}"'
                      argstr += f', sequence: {seqno}'
                      if size != '':
                          argstr += f', size: {size}'
                      argstr += f', timeout: {timeout}'
                      if self.debug:
                          print(f'argstr={argstr}')

                      # display progress in-place as does 128status.sh...
                      now_message=f"NI {netintf['name']}: ping {gateway} {ping_count}/{params['iterations']} tmo={params['timeout']}s"
                      self.output.progress_display(now_message, fp)
                      qp = gql_helper.RawGQL(f'ping({argstr}) ' + '{ status statusReason reachable sequence ttl responseTime }', debug=self.debug)
                      json_ping_reply = {}
                      qp.send_query(gql_token, json_ping_reply)

                      # standard graphql error processing may not be appropriate here as a failure can
                      # be part of the test process w/o ruining the test.

                      ping_count += 1
                      seqno += 1

                      try:
                          # "0" used < 4.2.0; "SUCCESS" used in 4.2.0+
                          json_ping_reply = json_ping_reply['ping']
                          if json_ping_reply['reachable'] == True and \
                             (json_ping_reply['status'] == "0" or \
                              json_ping_reply['status'] == "SUCCESS"):
                              address_entry["ping_success_count"] += 1
                              address_entry["total_response_time"] += float(json_ping_reply['responseTime'])
                              address_entry["average_response_time"] = address_entry["total_response_time"] / float(address_entry["ping_success_count"])
                              if params['max_single_response_time'] > 0.0 and \
                                 float(json_ping_reply['responseTime']) > params['max_single_response_time']:
                                  address_entry["response_time_overages"] += 1
                          else:
                              address_entry["ping_fail_count"] += 1
                      except (KeyError, TypeError) as e:
                          self.output.proc_no_data_in_reply(netintf, address_entry)
                          address_entry["ping_fail_count"] += 1
                          continue

                  address_entry["ping_count"] = ping_count
                  if self.debug:
                      headline=f"GW Ping Summary: (ni={netintf['name']} gw={gateway} dest={dest_ip}"
                      border = '-' * len(headline)
                      print(headline)
                      print(border)
                      print(f"Pings: Total={ping_count} MaxFails={params['max_ping_failures']}")
                      print(f"Successes={address_entry['ping_success_count']} Fails={address_entry['ping_fail_count']}")
                      print(f"Response Time Overages: Max={params['max_response_overages']} Calculated={address_entry['response_time_overages']}")
                      print(f"Average Response Time:  Max={params['max_average_response_time']} Calculated={address_entry['average_response_time']}")
                  if address_entry["ping_fail_count"] <= params["max_ping_failures"] and \
                     address_entry["response_time_overages"] <= params["max_response_overages"] and \
                     (params["max_average_response_time"] == 0.0 or \
                      address_entry["average_response_time"] <= params["max_average_response_time"]):
                      # fix this for multiple matching entries
                      stats["address_pass"] += 1
                      self.output.proc_ping_result_pass(netintf, address_entry, params)
                  else:
                      stats["address_fail"] += 1
                      self.output.proc_ping_result_fail(netintf, address_entry, params)             

          except (ValueError) as e:
              self.output.proc_no_address_in_reply(netintf);
              continue
      
      status = self.output.status
      if stats["entry_count"] == 0 or \
         stats["address_total_count"] == 0 or \
         stats["address_count"] == 0:
          status = Output.Status.WARN
      if stats["address_fail"] > 0 or \
         stats["address_dev_status"] > 0:
          status = Output.text_to_status(params['fail_status'])

      self.output.proc_test_result(status, stats, params)
      return self.output.test_end(fp)


