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
         "node_type"          : '',
         "device-interfaces"  : [],
         "network-interfaces" : [],
         "sequence"           : 1,
         "size"               : 100,
         "timeout"            : 2,
         "identifier"         : 68686868,
         "iterations"         : 100,
         "destination-ip"     : '',
         "static-address"     : False,
         "exclude_list"       : [ ]
      }

      params = self.apply_default_params(default_params)
      return params

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

      if self.debug:
          print(f'------ Network Interfaces to Process  ------')
          pprint.pprint(intf_list)

      qr = gql_helper.NodeGQL("allRouters", ['name'], [ router_context.get_router() ], debug=self.debug)
      qn = gql_helper.NodeGQL("nodes", [ 'name' , 'assetId' ])
      qd = gql_helper.NodeGQL("deviceInterfaces", [ 'name', 'sharedPhysAddress', 'state { operationalStatus }' ], dev_list)
      qi = gql_helper.NodeGQL("networkInterfaces", ['name', 'state { addresses { ipAddress gateway prefixLength } }'], intf_list)
      qa = gql_helper.NodeGQL("addresses", ['ipAddress', 'gateway', 'prefixLength'])
      qr.add_node(qn)
      qn.add_node(qd)
      qd.add_node(qi)
      qi.add_node(qa)

      json_reply={}
      if not self.send_query(qr, gql_token, json_reply):
          return self.output.test_end(fp);

      if params["static-address"]:
          flatter_json = qr.flatten_json(json_reply, 'router/nodes/deviceInterfaces/networkInterfaces/addresses', '/')
          ni_name_key='router/nodes/deviceInterfaces/networkInterfaces/name'
      else:
          # stop prefix should be router/nodes/deviceInterfaces/networkInterfaces/state, but because no address is
          # returned for one of the peers (state=None), flatten_json skips that node. So go one level higher and
          # live with it for now.
          flatter_json = qr.flatten_json(json_reply, 'router/nodes/deviceInterfaces/networkInterfaces', '/')
          ni_name_key='name'

      router_context.set_allRouters_node_type(flatter_json)

      self._workaround_graphql_api(flatter_json)

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)

      self.output.progress_start(fp)

      gateway_success_count = 0
      gateway_fail_count    = 0
      gateway_count         = 0

      for entry in flatter_json:
          if self.debug:
              print(f'%%% process NI for Ping %%%')
              pprint.pprint(entry)
          if params["node_type"] != '' and \
              entry['node_type'] != params["node_type"]:
              if self.debug:
                  print(f"NI {entry[ni_name_key]}: Skipping {entry['node_type']} node {entry['node_name']}")
              continue
          address = ''
          gateway = ''
          try:
              if params["static-address"]:
                   addresses = [ entry ]
              else:
                   addresses = entry['state']['addresses']
              if self.debug:
                  print(f'%%%% process address for Ping %%%%')
                  pprint.pprint(addresses)
              egress_interface = entry[ni_name_key]
              for address_entry in addresses:
                  address = address_entry['ipAddress']
                  gateway = address_entry['gateway']
                  prefix_length = int(address_entry['prefixLength'])
                  target = gateway
                  dest_ip = None

                  if gateway is None:
                      # hack for ipv4 only!
                      hack = int(ipaddress.IPv4Address(address))
                      if prefix_length == 31:
                          gateway_hack = hack&0xfffffffe|-(hack&0x01)+1
                          gateway_ip = ipaddress.IPv4Address(gateway_hack)
                          dest_ip = str(gateway_ip)
                          gateway = ''
                          target  = dest_ip
                      elif prefix_length == 30:
                          gateway_hack = hack&0xfffffffc|-(hack&0x03)+3
                          gateway_ip = ipaddress.IPv4Address(gateway_hack)
                          dest_ip= str(gateway_ip)
                          gateway = ''
                          target = dest_ip
                      else:
                          self.output.proc_cannot_ping_no_gateway(entry, ni_name_key)
                          msg_list.append(f'Cannot ping via NI {entry[ni_name_key]}, No Gateway!')
                          gateway_count += 1
                          continue

                  try:
                      oper_status = entry['router/nodes/deviceInterfaces/state/operationalStatus']
                      if oper_status != 'OPER_UP':
                          self.output.proc_cannot_ping_dev_status(entry, ni_name_key, oper_status)
                          gateway_count += 1
                          #continue
                          break
                  except KeyError:
                      # Continue as there is no operationalStatus to evaluate
                      pass

                  # Invoke Graphql PING API
                  ping_count = 0
                  if dest_ip is None:
                      if "destination-ip" in params and \
                          params["destination-ip"] != '':
                          dest_ip = params["destination-ip"]
                      else:
                          dest_ip = gateway
                  size    =  params["size"]
                  timeout = params["timeout"]
                  seqno   = params["sequence"]
                  router  = entry["router/name"]
                  node    = entry["node_name"]
                  identifier = params["identifier"]

                  total_response_time   = float(0)
                  average_response_time = float(0)
                  ping_success_count    = 0
                  ping_fail_count       = 0

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
                      now_message=f"NI {entry[ni_name_key]}: ping {gateway} {ping_count}/{params['iterations']} tmo={params['timeout']}s"
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
                          if json_ping_reply['status'] == "0" or \
                             json_ping_reply['status'] == "SUCCESS":
                              ping_success_count   += 1
                              total_response_time  += float(json_ping_reply['responseTime'])
                              average_response_time = total_response_time / float(ping_success_count)
                          else:
                              ping_fail_count      += 1
                      except (KeyError, TypeError) as e:
                          self.output.proc_no_data_in_reply(entry, ni_name_key, gateway)
                          ping_fail_count += 1
                          gateway_count += 1
                          continue

                  if ping_count == ping_success_count:
                      # fix this for multiple matching entries
                      gateway_success_count += 1
                      self.output.proc_ping_result_pass(entry, ni_name_key, 
                                                        ping_count, ping_success_count, 
                                                        target, average_response_time)             
                  else:
                      gateway_fail_count += 1
                      self.output.proc_ping_result_fail(entry, ni_name_key, 
                                                        ping_count, ping_fail_count, 
                                                        target, average_response_time)             
              gateway_count += 1

          except (TypeError) as e:
              self.output.proc_no_address_in_reply(entry, ni_name_key);
              continue
      
      status = self.output.status
      if gateway_count == 0:
          status = Output.Status.WARN
      if gateway_count != gateway_success_count:
          status = Output.Status.FAIL

      self.output.proc_test_result(status, gateway_count, 
                                   gateway_success_count, 
                                   gateway_fail_count, params)
      return self.output.test_end(fp)


