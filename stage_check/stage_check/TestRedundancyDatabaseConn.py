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
         "test_value"       : 0,
         "test_equality"    : True,
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
      test_value       = params["test_value"]
      test_equality    = params["test_equality"]
      expected_entries = params["expected_entries"]

      operation = '==' if (test_equality) else '!='

      # This API doesn't allow a list of nodes to query, so get everything and
      # then use router_context.nodes()
      qm = gql_helper.RawGQL('metrics { redundancy { databaseConnection { activeConnections(router: "%s") { node value } } } }' % \
                                                  router_context.get_router(), debug=self.debug)
      json_reply={}
      if not self.send_query(qm, gql_token, json_reply):
          return self.output.test_end(fp)

      match_string = "metrics.redundancy.databaseConnection.activeConnections[]"
      matching_json = jmespath.search(match_string, json_reply)

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(matching_json)

      if matching_json is None:
          self.output.proc_no_node_data(local_info)
          return self.output.test_end(fp)

      entry_count = 0
      fail_count = 0
      for entry in matching_json:
          try:
              # conversion of graphl reply yields a json string, not a int...
              entry_value = int(entry['value'])
              self.output.proc_metric(entry, entry_value)
              if entry_value != test_value:
                  fail_count += 1
                  self.output.set_status(Output.Status.FAIL)
          except KeyError:
              self.output.proc_missing_data()
              fail_count += 1
              pass
          entry_count += 1

      status = self.output.status
      if status == Output.Status.OK:
          if entry_count != expected_entries:
              status = Output.Status.FAIL
          self.output.proc_test_result(status, entry_count, test_value, fail_count, expected_entries)
      else:
          self.output.proc_test_result_bad_values(entry_count, test_value, fail_count, expected_entries)
          self.message = f'Bad/missing values on {fail_count}/{entry_count} nodes'

      return self.output.test_end(fp)

