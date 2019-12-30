"""
"""
import pprint

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
    from stage_check import EntryTest
except ImportError:
    import EntryTest


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
      fib_table_fields=[
          "totalCount"
      ]
      fib_route_fields=[
          "serviceName " 
          "route { " 
          "ipPrefix "
          "l4Port "
          "l4PortUpper "
          "protocol " 
          "tenant "
          "nextHops { devicePort gateway nodeId vlan deviceInterface networkInterface } "
          "}" 
      ]
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      
      params = self.get_params()
      exclude_tests = params["exclude_tests"]

      fib_entry_suffix=''
      if params["filter_string"] != "" or \
         params["maximum_query_count"] > 0:
          fib_entry_suffix = '('
          if params["maximum_query_count"] > 0:
              fib_entry_suffix += f"first: {params['maximum_query_count']}"
          if params["filter_string"] != "":
              if len(fib_entry_suffix) > 1:
                 fib_entry_suffix += ','
              fib_entry_suffix += f'filter: "\\"\\"~\\"{params["filter_string"]}\\""'
          fib_entry_suffix += ')'

      if local_info.get_router_name() == router_context.get_router() and \
         local_info.get_node_type() == 'conductor':
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
      qR = gql_helper.NodeGQL("allRouters", ["name"], [router_context.get_router()], debug=self.debug)
      qn = gql_helper.NodeGQL("nodes", ["name"], node_names)
      qf = gql_helper.NodeGQL(f"fibEntries{fib_entry_suffix}", fib_route_data)
      #qr = gql_helper.NodeGQL("route",  fib_route_data)
      qR.add_node(qn)
      qn.add_node(qf)
      #qf.add_node(qr)

      json_reply={}
      if not self.send_query(qR, gql_token, json_reply):
          return self.output.test_end(fp)

      flatter_json = qR.flatten_json(json_reply, 'router/nodes/fibEntries/route', '/')

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)

      stats = {}
      Output.init_result_stats(stats)
      stats["total_count"] = len(flatter_json)

      if params["minimum_threshold"] > 0 and \
         total_count < params["minimumm_threshold"]:
          self.output.add_too_few_entries(params)
          return self.output.test_end(fp)

      if params["maximum_threshold"] > 0 and \
         total_count > params["maximum_threshold"]:
          self.output.add_too_man_entries_parameters(params)
          return self.output.test_end(fp)

      engine = EntryTest.Parser(self.debug)
      for entry in flatter_json:
          if engine.exclude_entry(entry, exclude_tests):
              stats["exclude_count"] += 1
              continue
          test_status = engine.eval_entry_by_tests(
              entry, 
              params["entry_tests"]
          )
          if test_status == Output.Status.FAIL:
              test.output.proc_test_match(entry)
              stats["fail_count"] += 1 
          if test_status == Output.Status.WARN:
              test.output.proc_test_match(entry)
              stats["warn_count"] += 1

      self.output.proc_test_result(params, stats)
      return self.output.test_end(fp)
