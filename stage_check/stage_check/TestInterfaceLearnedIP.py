"""
"""
import pprint
import ipaddress

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


def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance
   
    @test_id - test index number
    @config  - test parameters from, config 
    @args    - command line args
    """
    return TestInterfaceLearnedIP(test_id, config, args)


class TestInterfaceLearnedIP(AbstractTest.GraphQL):
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
      """
      default_params = {
         "network-interfaces" : [],
         "exclude_tests"      : [],
         "skip_no_address"    : True
      }

      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      """
      This test uses the gql engine to get device state state

      Sample data returned by query:
      [{'name': 'ha-fabric', 'state': None},
       {'name': 'DIA', 'state': {'addresses': [{'ipAddress': '172.16.4.103'}]}},
       {'name': 'mpls-t1', 'state': {'addresses': [{'ipAddress': '<empty>'}]}}]
      """
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      params = self.get_params()
      include_list = params["network-interfaces"]
      exclude_list = params["exclude_tests"]
      
      # Kind of a hack as we suggest that its OK for an address to be missing
      # Theoretically this is an error condition, but currently it is normal
      # that GraphQL will sort of arbitrarily pick a node's L2 HA interfaces
      # to place state information in.
      skip_if_address_missing = params["skip_no_address"]

      ni_args = None
      if len(include_list) > 0:
          ni_args = {"names" : include_list}

      stats = self.init_stats()

      """
      API    = allRouters
      Fields = name
      """
      """
      qr = gql_helper.NodeGQL("allRouters", ['name'], [ router_context.get_router() ], debug=self.debug)
      qn = gql_helper.NodeGQL("nodes", ['name'])
      qd = gql_helper.NodeGQL("deviceInterfaces", [ 'name', 'sharedPhysAddress', 'state { operationalStatus }' ])
      qi = gql_helper.NodeGQL("networkInterfaces", ['name', 'state { addresses { ipAddress } }'], include_list)
      qr.add_node(qn)
      qn.add_node(qd)
      qd.add_node(qi)

      json_reply={}
      if not self.send_query(qr, gql_token, json_reply):
          return self.output.test_end(fp)

      flatter_json = qr.flatten_json(json_reply, '/allRouters/nodes/deviceInterfaces/networkInterfaces', '/')
      """

      qr = gql_helper.NewGQL(
         api_name = "allRouters", 
         api_args = {"name" : router_context.get_router()}, 
         api_fields = ["name"], 
         api_has_edges=True,
         debug=self.debug
         )
      qn = gql_helper.NewGQL(
         api_name = "nodes",
         api_fields = ["name"],
         api_has_edges=True
         )
      qd = gql_helper.NewGQL(
         api_name = "deviceInterfaces", 
         api_fields =  ["name", "sharedPhysAddress", "state { operationalStatus }"] ,
         api_has_edges=True
         )
      qi = gql_helper.NewGQL(
         api_name = "networkInterfaces",
         api_args = ni_args,
         api_fields = ["name", "state { addresses { ipAddress } }"],
         api_has_edges=True
        )
      qr.add_node(qn)
      qn.add_node(qd)
      qd.add_node(qi)

      flatter_json = []
      qr.api_flat_key = "/allRouters/nodes/deviceInterfaces/networkInterfaces"
      if not self.send_query(qr, gql_token, flatter_json):
          return self.output.test_end(fp)

      router_context.set_allRouters_node_type(flatter_json)
 
      # do not work around the grapqhl api for now...
      # self._workaround_graphql_api(flatter_json)
      """
      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)
      """

      address_list=[]
      not_excluded_count = 0
      if len(flatter_json) > 0:
          for entry in flatter_json:
              try:
                  if_name = None
                  if_name = entry['name']
              except KeyError:
                  pass
              if len(include_list) > 0 and \
                  not if_name in include_list:
                  continue
              if len(exclude_list) > 0 and \
                  if_name in exclude_list:
                  continue
              address=None
              if if_name is not None:
                  if self.exclude_flat_entry(entry, exclude_list):
                      continue
                  #if entry['/allRouters/nodes/deviceInterfaces/state/operationalStatus'] != "OPER_UP"
                  try:
                      address = entry['state']['addresses'][0]['ipAddress']
                  except (KeyError, IndexError, TypeError) as e:
                      # TODO: Report Exception {e.__class__.__name__} {e}
                      if not skip_if_address_missing:
                          self.output.proc_address_missing(None, entry)
                      continue
                  if address is not None:
                      #  address='1.1.1.1'
                      if address == '<empty>':
                          self.output.proc_empty_address(entry)
                      else:  
                          ip_address = ipaddress.ip_address(address)
                          status = self.output.status
                          if ip_address.is_private:
                              status = Output.Status.FAIL
                              iptype = 'Private'
                          else:
                              iptype = 'Public'
                              address_list.append(address)
                          self.output.proc_address_type(status, entry, address, iptype)
                  else:
                      if skip_if_address_missing:
                         continue
                      self.output.proc_address_missing(None, entry)
                  not_excluded_count += 1
      else:
          self.output.proc_no_interfaces_found(include_list)

      status = self.output.status
      if status == Output.Status.OK and \
         not_excluded_count == 0:
          status = Output.Status.FAIL

      self.output.proc_test_result(status, address_list, not_excluded_count)
      return self.output.test_end(fp)

