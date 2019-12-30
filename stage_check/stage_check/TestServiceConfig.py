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

try:
    from stage_check import EntryTester
except ImportError:
    import EntryTester

try:
    from stage_check import Linux
except ImportError:
    import Linux


def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance
   
    @test_id - test index number
    @config  - test parameters from, config 
    @args    - command line args
    """
    return TestServiceConfig(test_id, config, args)


class TestServiceConfig(AbstractTest.GraphQL, EntryTester.MatchFunction):
  """
  This test first performs a Linux command to get /etc/hosts content and
  then issues a GraphQL command to peform the ServicePing, so it is a hybrid 
  of both test types...
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)
      self._hostsCommand = None

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
         "exclude_tests" : [],
         "flatten_path"  : None,
         "expected_count" : 0,      
      }

      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      """
      Reads in a list of service information and  
      """
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      params = self.get_params()
      self.output.progress_start(fp)

      exclude_tests = params["exclude_tests"]
      params["query"] = router_context.populate_items(params["query"])
      params["entry_tests"] = router_context.populate_items(params["entry_tests"])

      # TODO: Can a reasonable / useful set of default fields be establihed?
      gql_args = {}
      gql_fields = []
      if "query" in params:
          if "arguments" in params["query"]:
              gql_args   = params["query"]["arguments"]
          if "fields" in params["query"]:
              gql_fields = params["query"]["fields"]
          else:
              self.output.proc_config_error(
                  params, 
                  "Missing Parameters['query']['fields']"
              )
              return self.output.test_end(fp)
      else:
          self.output.proc_config_error(
              params, 
              "Missing Parameters['query']"
          )
          return self.output.test_end(fp)
                    
      qs = gql_helper.NewGQL(
          api_name="allServices", 
          api_args=gql_args, 
          api_fields=gql_fields,
          api_has_edges=True,
          debug=self.debug
      )

      json_reply = []
      qs.api_flat_key = "/allServices"
      self.send_query(qs, gql_token, json_reply)
      #assert False, "allServices: " + pprint.pformat(json_reply)

      stats = {}
      Output.init_result_stats(stats);
      stats["total_count"] = len(json_reply)

      engine = EntryTester.Parser(debug=self.debug)
      for entry in json_reply:
          if engine.exclude_entry(entry, exclude_tests):
              stats["exclude_count"] += 1
              continue
          status = engine.eval_entry_by_tests(entry, params["entry_tests"])
          if status is None:
              assert False, "NONE STATUS DETECTED"
          Output.update_stats(stats, status, entry)
          self.output.proc_test_match(entry)

      if params["expected_count"] > 0 and \
         stats["total_count"] != params["expected_count"]:
          stats["FAIL"] += 1
          self.output.proc_entry_count(params, stats)

      self.output.status = Output.stats_to_status(stats)
      self.output.proc_test_result(params["entry_tests"], stats)
      return self.output.test_end(fp)


