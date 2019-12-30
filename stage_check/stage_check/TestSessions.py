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
    return TestSessions(test_id, config, args)


class TestSessions(AbstractTest.GraphQL):
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
          "idle_theshold_seconds"  : 0,
          "idle_maximum_seconds"   : 0, 
          "max_sessions_to_query"  : 0,
          "filter_string"          : "",
          "match_port"             : 0,
          "exclude_tests"          : []
      }
     
      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      flowEntryFields = [ \
          'sourceIp',
          'destIp',
          'sourcePort',
          'destPort',
          'vlan',
          'devicePort',
          'protocol',
          'sessionUuid',
          'natIp',
          'natPort',
          'serviceName',
          'tenant',
          'encrypted',
          'inactivityTimeout',
          'deviceInterfaceName',
          'networkInterfaceName',
          'startTime',
          'forward'
        ]

      test_info = self.test_info(local_info, router_context)
      stats = self.init_stats()
      self.output.test_start(test_info)
      
      params = self.get_params()
      try:
          idle_threshold_seconds = params["idle_threshold_seconds"]
          idle_maximum_seconds   = params["idle_maximum_seconds"]
          max_sessions           = params["max_sessions_to_query"]
          filter_string          = params["filter_string"]
          match_port             = params["match_port"]
      except Exception as e:
          # TODO: Improve error handling
          print(f"CONFIG ERROR {e} {e.__class__.__name__}\n")
          return Output.Status.FAIL

      exclude_tests = []
      if "exclude_tests" in params:
          exclude_tests = params["exclude_tests"]
      
      flow_entry_suffix=f'(first: {max_sessions}, filter: "\\"\\"~\\"{filter_string}\\"")'

      if router_context.is_conductor:
         # Check Error output
         self.output.unsupported_node_type(local_info)
         return Output.Status.WARN

      """
      qr = gql_helper.NodeGQL("allRouters", ['name'], [ router_context.get_router() ], debug=self.debug)
      qn = gql_helper.NodeGQL("nodes", ['name'])
      qf = gql_helper.NodeGQL(f"flowEntries{flow_entry_suffix}", flowEntryFields)
      """
      qr = gql_helper.NewGQL(
           api_name="allRouters", 
           api_args={"name" : router_context.get_router()},
           api_fields=[ "name" ], 
           api_has_edges=True, 
           debug=self.debug
      )
      qn = gql_helper.NewGQL(
           api_name="nodes",
           api_fields="name",
           api_has_edges=True,
           debug=self.debug
      )
      qf = gql_helper.NewGQL(
           api_name=f"flowEntries",
           api_args={"first" : max_sessions, "filter" : f'\\"\\"~\\"{filter_string}\\"'},
           api_fields=flowEntryFields, 
           api_has_edges=True, 
           debug=self.debug
      )
      qr.add_node(qn)
      qn.add_node(qf)

      json_reply={}
      
      #if not self.send_query(qr, gql_token, json_reply):
      flatter_json=[]
      #qr.assert_post_flat = True
      qr.api_flat_key="/allRouters/nodes/flowEntries"
      if not self.send_query(qr, gql_token, flatter_json):
          return self.output.test_end(fp)

      # Unfortunately jmespath is buggy and does not work well for integers :-(
      # This is unforunate as the hope was to use a jmespath expression
      # to eliminate all valid sessions (however that might be defined)
      #flatter_json = qr.flatten_json(json_reply, '/allRouters/nodes/flowEntries')

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)

      matching_flows = {}
      session_flow_counts = {}
      stats["total_count"] = len(flatter_json)
      stats["session_flow_count"] = 0
      stats["session_fail_count"]  = 0
      stats["session_bad_info"] = 0

      engine = EntryTester.Parser(debug=self.debug)
      for flow in flatter_json:
          if not isinstance(flow, dict):
              stats["session_bad_info"] += 1
              continue
          try:
              uuid = flow['sessionUuid']
              if engine.exclude_entry(flow, exclude_tests):
                  stats["exclude_count"] += 1
                  continue
              if not uuid in session_flow_counts:
                  session_flow_counts[uuid] = 1
              else:
                  session_flow_counts[uuid] += 1
              test_status = engine.eval_entry_by_tests(flow, params["entry_tests"])
              Output.update_stats(stats, test_status)
              if test_status == Output.Status.FAIL:
                  # Note that this must be configured in the parameters just so the value can
                  # be used in this calculation
                  delta = idle_maximum_seconds - flow['inactivityTimeout']
                  flow["test_idle_duration"] = delta
                  if not uuid in matching_flows:
                      stats["session_fail_count"] += 1
                      matching_flows[uuid] = flow

          except (KeyError, TypeError) as e:
              flow["test_exception"] = f"Flow Exception: {e}"
              continue

      stats["session_flow_count"] = len(session_flow_counts)      

      status = Output.Status.FAIL
      if len(matching_flows) == 0:
          status = Output.Status.OK
          if stats["gql_errors"] > 0:
              status = Output.Status.WARN

      self.output.proc_test_result(status, matching_flows, stats, params)
      return self.output.test_end(fp)
