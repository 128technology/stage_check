"""
"""
import pprint
import re

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

try:
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest


def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance
   
    @test_id - test index number
    @config  - test parameters from configuration 
    @args    - command line args
    """
    return TestIPSecStatus(test_id, config, args)


class TestIPSecStatus(AbstractTest.Linux, EntryTester.MatchFunction):
  """
  Tests to see if the requested device pattern matches in the 
  global namespace and/or the specified namespaces(s)
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)
      self.results = []

  def get_params(self):
      # apply defaults
      default_params = {
          "node_type"              : "all",
          "exclude_tests"          : [],
          "entry_tests"            : {},
      }
     
      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      """
      """
      # Ugly!
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info,  status=Output.Status.OK)
      params = self.get_params()
      self.init_stats()

      if self.check_user() != Output.Status.OK:
          return self.output.test_end(fp)

      self.output.progress_start(fp)

      json_data   = []
      error_lines = []
      ethtool = Linux.IPSecStatus(
          debug=self.debug, 
          progobj=self
      )
      # Ugly....
      self.fp = fp
      shell_status = ethtool.run_linux_args(
          router_context, 
          params['node_type'],
          error_lines,
          json_data
      )
      # Ugly...
      self.fp = None

      if len(error_lines) > 0:
          if self.debug:
              print("-------- TestIPSecStatus Shell Error Lines ---------")
              pprint.pprint(error_lines)
          self.output.proc_run_linux_error(shell_status, error_lines[0])
          return self.output.test_end(fp)

      #assert False, pprint.pformat(json_data)
      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(json_data)

      engine = EntryTester.Parser(debug=self.debug)
      for entry in json_data:
          if engine.exclude_entry(entry, params["exclude_tests"]):
              self.stats["exclude_count"] += 1
              continue
          test_status = engine.eval_entry_by_tests(
              entry, 
              params["entry_tests"]
          )
          Output.update_stats(self.stats, test_status)
          self.output.proc_result(test_status, entry)

          if len(entry["errors"]) > 0:          
              if test_status != Output.Status.FAIL:
                  self.stats["FAIL"] += 1
              self.output.proc_errors(entry)
      
      self.output.proc_test_result(params["entry_tests"], self.stats)
      status = self.output.stats_to_status_value(self.stats)
      self.output.status = status
      return self.output.test_end(fp)
