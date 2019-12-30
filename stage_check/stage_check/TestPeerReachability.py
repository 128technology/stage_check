"""
"""
import pprint

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

try:
    from stage_check import EntryTester
except ImportError:
    import EntryTester


def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance
   
    @test_id - test index number
    @config  - test parameters from, config 
    @args    - command line args
    """
    return TestPeerReachability(test_id, config, args)


class TestPeerReachability(AbstractTest.GraphQL):
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
      expected_entries shoudl fail schema validation if
      missing from the parameters
      """
      default_params = {
         "test_value"    : "UP",
         "test_equality" : True,
         "exclude_tests" : [],
         "include_list"  : []
      }

      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      """
      This test uses the gql engine to get peer reachability status
      """
      path_fields = [
          "node",
          "adjacentNode",
          "deviceInterface",
          "networkInterface",
          "adjacentAddress",
          "status"
      ]
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      params = self.get_params()
      # TODO figure out what the include_list is, a list of peers?
      include_list  = params["include_list"]
      exclusions    = params["exclude_tests"]
      entry_tests   = params["entry_tests"]
      """
      API    = allNodes
      Fields = name
      """
      """
      qr = gql_helper.NodeGQL("allRouters", ['name'], [ router_context.get_router() ], debug=self.debug)
      qp = gql_helper.NodeGQL("peers", [ 'name', 'paths { node adjacentNode deviceInterface networkInterface adjacentAddress status }' ],
                              include_list)
      qr.add_node(qp)

      json_reply={}
      if not self.send_query(qr, gql_token, json_reply):
          return self.output.test_end(fp)
      """

      qr = gql_helper.NewGQL(
          api_name = "allRouters", 
          api_args = { "name" : router_context.get_router() }, 
          api_fields = [ "name" ],
          api_has_edges = True,
          debug=self.debug
          )
      peers_args = None
      if len(include_list) == 1:
         peers_args = { "name" : include_list[0] }
      elif len(include_list) > 1:
         peers_args = { "names" : include_list }
      qp = gql_helper.NewGQL(
          api_name = "peers", 
          api_args = peers_args,
          api_fields = [ 
               "name", 
               "paths { " + " ".join(path_fields) + " }" ],
           api_has_edges=True
         )
      qr.add_node(qp)

      flatter_json = []
      qr.api_flat_key = "allRouters/peers/paths"
      if not self.send_query(qr, gql_token, flatter_json):
          return self.output.test_end(fp)

      router_context.set_allRouters_node_type(flatter_json, 'node')

      """
      # this query is not working correctly unfortunately... even UP is returned
      flatter_json = qr.flatten_json(json_reply, 'allRouters/peers/paths')

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)
      """

      paths_per_peer = {}
      failed_peer_paths = {}
      stats = {}
      Output.init_result_stats(stats)
      stats["total_count"] = len(flatter_json) 
      stats["failed_peer_count"] = 0
      stats["tested_peer_count"] = 0

      engine = EntryTester.Parser(self.debug)
      for path in flatter_json:
          try:
              if engine.exclude_entry(path, exclusions):
                  stats["exclude_count"] += 1
                  continue
              peer_name = path['allRouters/peers/name']
              test_result = engine.eval_entry_by_tests(
                  path,
                  entry_tests
              )
              Output.update_stats(stats, test_result)
              if peer_name in paths_per_peer:
                  paths_per_peer[peer_name] += 1
              else:
                  paths_per_peer[peer_name] = 1
                  stats["tested_peer_count"] += 1
              if test_result == Output.Status.FAIL:
                  if peer_name in failed_peer_paths:
                      failed_peer_paths[peer_name] += 1
                  else:
                      failed_peer_paths[peer_name] = 1
                      stats["failed_peer_count"] += 1
                      self.output.proc_failed_peer(path, peer_name)
                  self.output.proc_failed_path(path)
          except KeyError:
              pass

      status = Output.Status.OK
      if stats["FAIL"] > 0:
          status = Output.Status.FAIL
          
      self.output.proc_test_result(entry_tests, stats, status=status)
      return self.output.test_end(fp)


