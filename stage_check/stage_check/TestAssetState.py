"""
"""
import pprint
import jmespath

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
    @config  - test parameters from configuration 
    @args    - command line args
    """
    return TestAssetState(test_id, config, args)


class TestAssetState(AbstractTest.GraphQL):
  """
  Lists all assets which are not in the state(s)
  specified in the "exlude_tests" parameter
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
          "exlude_tests"  : []
      }
     
      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      """
      This test uses the gql engine to get asset state

      This query only works on the conductor (why? the
      conductor learns asset state from the managed nodes
      so why show it only on the conductor?

      This test will have to include a local node role
      test, which can be checked for 'conductor' and
      return status WARN otherwise...
      """
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info, status=Output.Status.OK)
      params = self.get_params()
      exclude_tests = params["exclude_tests"]
      entry_tests = params["entry_tests"]
      no_match = {}
      if "no_match" in entry_tests:
          no_match = entry_tests["no_match"]

      if local_info.get_node_type() != 'conductor':
          self.output.unsupported_node_type(local_info)
          return self.output.test_end(fp)

      qn = gql_helper.NodeGQL("allAuthorities", [ 'assets { assetId routerName nodeName t128Version status assetIdConfigured ' +
                                                  'text failedStatus }' ], [ ], top_level=True, debug=self.debug)
      json_reply={}
      if not self.send_query(qn, gql_token, json_reply):
          return self.output.test_end(fp)

      #flatter_json = self.flatten_json(json_reply, 'node/assets', '/', prefix='')
      match_string=f"node.assets[*] | [?routerName=='{router_context.get_router()}']"
      flatter_json = jmespath.search(match_string, json_reply)

      router_context.set_allRouters_node_type(flatter_json, node_name_key="nodeName")

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)

      stats = {}
      Output.init_result_stats(stats)
      stats["total_count"] = len(flatter_json)

      engine = EntryTest.Parser()
      for entry in flatter_json:
          if engine.exclude_entry(entry, exclude_tests):
              stats["exclude_count"] += 1
              continue
          test_status = engine.eval_entry_by_tests(entry, params["entry_tests"])
          Output.update_stats(stats, test_status)
          if test_status != None:
              self.output.proc_interim_result(entry, status=test_status)

      # All pass versus fail decisions belong outside of the output module
      if stats["FAIL"] > 0:
          self.output.proc_test_result(entry_tests, stats, status=Output.Status.FAIL)
      else:
          self.output.proc_test_result(entry_tests, stats, status=Output.Status.OK)

      return self.output.test_end(fp)

