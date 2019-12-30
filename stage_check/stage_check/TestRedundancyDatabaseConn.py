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
    return TestRedundancyDatabaseConn(test_id, config, args)


class TestRedundancyDatabaseConn(AbstractTest.GraphQL):
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
      expected_entries should fail schema validation if
      missing from the parameters
      """
      default_params = {
         "exclude_tests" : [],
         "expected_entries" : 2
      }

      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      """
      This test uses the gql engine to get redundancy metrics
      """
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info, status=Output.Status.OK)
      params = self.get_params()
      self.init_stats()
      entry_tests = params["entry_tests"]
      expected_entries = params["expected_entries"]

      # This API doesn't allow a list of nodes to query, so get everything and
      # then use router_context.nodes()
      qm = gql_helper.RawGQL('metrics { redundancy { databaseConnection { activeConnections(router: "%s") { node value } } } }' % \
                              router_context.get_router(), debug=self.debug)
      json_reply={}
      if not self.send_query(qm, gql_token, json_reply):
          return self.output.test_end(fp)

      # TODO: replace with the latest flattening algorithm
      match_string = "metrics.redundancy.databaseConnection.activeConnections[]"
      matching_json = jmespath.search(match_string, json_reply)

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(matching_json)

      if matching_json is None:
          self.output.proc_no_node_data(local_info)
          return self.output.test_end(fp)

      self.stats['excluded'] = 0
      self.stats['total_count'] = len(matching_json)
      engine = EntryTester.Parser(debug=self.debug) 
      for entry in matching_json:
          if engine.exclude_entry(entry, params["exclude_tests"]):
              self.stats['excluded'] += 1
              continue
          test_status = engine.eval_entry_by_tests(entry, entry_tests)
          router_context.add_entry_tags(test_status, entry)
          Output.update_stats(self.stats, test_status)
          self.output.proc_entry_result(entry_tests, entry)

      if self.stats["tested_count"] == expected_entries:
          self.output.proc_test_result(entry_tests, self.stats)
          status = self.output.stats_to_status_value(self.stats)
          self.output.status = status
      else:
          self.output.status = Output.Status.FAIL
          self.output.proc_unexpected_count(self.stats, expected_entries)

      return self.output.test_end(fp)

