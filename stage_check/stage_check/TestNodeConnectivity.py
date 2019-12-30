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


def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance

    @test_id - test index number
    @config  - test parameters from, config
    @args    - command line args
    """
    return TestNodeConnectivity(test_id, config, args)


class TestNodeConnectivity(AbstractTest.GraphQL):
  """
  Test node connectivity
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
         "expected_entries" : 0,
         "exclude_tests"    : [],
      }

      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      """
      This test usess the gql engine to get node connectivity status
      """
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      params = self.get_params()
      exclude_list     = params["exclude_tests"]
      expected_entries = params["expected_entries"]

      if expected_entries == 0:
          expected_entries = router_context.get_expected_connections()

      qr = gql_helper.NodeGQL("allRouters", ['name'], [ router_context.get_router() ], debug=self.debug)
      qn = gql_helper.NodeGQL("nodes", ['name', 'connectivity { status remoteRouterName remoteNodeName remoteNodeRole}' ])

      qr.add_node(qn)

      json_reply={}
      query_status = AbstractTest.GraphQL.ReplyStatus()
      if not self.send_query(qr, gql_token, json_reply, query_status):
          return self.output.test_end(fp)

      flatter_json = qr.flatten_json(json_reply, 'allRouters/nodes/connectivity', prefix='')
      router_context.set_allRouters_node_type(flatter_json)

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)

      entry_count = 0
      fail_count  = 0
      for entry in flatter_json:
          entry_count += 1
          if entry is None:
              # In the past this happens when a node fails to register the 'show
              # system connectivity' command for itself
              self.output.proc_empty_reply(status=Output.Status.FAIL)
              fail_count += 1
              continue
          if self.exclude_flat_entry(entry, exclude_list):
              continue
          self.output.proc_node_status_mismatch(entry)
          fail_count += 1

      status = self.output.status
      if query_status.server_code == 200:
          if entry_count < expected_entries:
              self.output.proc_test_result_too_few(entry_count, fail_count, params)
          elif status == Output.Status.FAIL:
              self.output.proc_test_result_wrong_state(fail_count, expected_entries, params)
          else:
              self.output.proc_test_result_all_ok(entry_count, expected_entries, params)
      else:
          self.output.proc_test_result_bad_query(query_status.server_code)

      return self.output.test_end(fp)

