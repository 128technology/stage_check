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
    @config  - test parameters from, config 
    @args    - command line args
    """
    return TestFib(test_id, config, args)


class TestFib(AbstractTest.GraphQL):
  """
  Filtering of the session table is performed in highwayManager by 
  taking all fields, concatenating into a string and matching the
  filter against this string to match the flow. 
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
      Apply defaults (some of these are non-sensical
      and absense should be caught during schema
      validation
      """
      default_params = {
          "entry_level"           : "routes",
          "maximum_query_count"   : 0,
          "minimum_threshold"     : 0,
          "maximum_threshold"     : 0,
          "filter_string"         : "",
          "entry_tests"           : {},
          "exclude_tests"         : []
      }
     
      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      fib_route_fields=[
          "serviceName", 
          "route", 
          "ipPrefix",
          "l4Port",
          "l4PortUpper",
          "protocol", 
          "tenant"
      ]
      fib_nexthop_fields = [
          "devicePort",
          "gateway",
          "nodeId", 
          "vlan", 
          "deviceInterface", 
          "networkInterface"
      ]
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      
      params = self.get_params()
      exclude_tests = params["exclude_tests"]

      fib_args = {}
      if params["maximum_query_count"] > 0:
          fib_args["first"] = f"{params['maximum_query_count']}" 
      if params["filter_string"] != "":
          fib_args["filter_string"] = f'\\"\\"~\\"{params["filter_string"]}\\"'
      if len(fib_args) == 0:
          fib_args = None

      if router_context.is_conductor:
          self.output.unsupported_node_type(local_info)
          return Output.Status.WARN

      fib_route_data = []
      if len(params["entry_tests"]) > 0:
          fib_route_data = fib_route_fields

      node_names = []
      if 'node_type' in params:
          node_name = router_context.get_node_by_type(params['node_type'])
          if node_name is not None and \
             node_name != '':
              node_names.append(node_name)

      # This query is run against all nodes for the router
      qR = gql_helper.NewGQL(
          api_name = "allRouters", 
          api_args = {"name" : router_context.get_router()}, 
          api_fields = ["name"], 
          api_has_edges = True,
          debug=self.debug
          )
      qN = gql_helper.NewGQL(
          api_name = "nodes", 
          api_args = { "names" : node_names },
          api_fields =  ["name"],
          api_has_edges = True
          )
      qf = gql_helper.NewGQL(
          api_name = "fibEntries",
          api_fields = [ "serviceName" ],
          api_has_edges = True
          )
      qr = gql_helper.NewGQL(
          api_name = "route",
          api_fields = fib_route_fields
      )
      qn = gql_helper.NewGQL(
          api_name = "nextHops",
          api_fields = fib_nexthop_fields
      )
      qR.add_node(qn)
      qN.add_node(qf)
      qf.add_node(qr)
      qr.add_node(qn)

      flatter_json = []
      qR.api_flat_key = "allRouters/nodes/fibEntries/route/nextHops"
      qR.api_key_prefix = ""
      if not self.send_query(qR, gql_token, flatter_json):
          return self.output.test_end(fp)

      stats = self.init_stats()
      stats["total_count"] = len(flatter_json)

      if params["minimum_threshold"] > 0 and \
         total_count < params["minimumm_threshold"]:
          self.output.add_too_few_entries(params)
          return self.output.test_end(fp)

      if params["maximum_threshold"] > 0 and \
         total_count > params["maximum_threshold"]:
          self.output.add_too_many_entries_parameters(params)
          return self.output.test_end(fp)

      #assert False, f"{json.dumps(flatter_json, indent=2)}" 

      engine = EntryTester.Parser(self.debug)
      for entry in flatter_json:
          if engine.exclude_entry(entry, exclude_tests):
              stats["exclude_count"] += 1
              continue
          test_status = engine.eval_entry_by_tests(
              entry, 
              params["entry_tests"]
          )
          Output.update_stats(self.stats, test_status)
          self.output.proc_test_match(entry)

      self.output.proc_test_result(params, stats)
      return self.output.test_end(fp)
