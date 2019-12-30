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
    return TestEthtool(test_id, config, args)


class TestEthtool(AbstractTest.Linux, EntryTester.MatchFunction):
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
          "node_type"              : "secondary",
          "linux_device"           : {},
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

      if self.check_user() != Output.Status.OK:
          return self.output.test_end(fp)

      self.output.progress_start(fp)

      json_data   = {}
      error_lines = []
      ethtool = Linux.Ethtool(
          devmap = params['linux_device'],
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

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(json_data)

      engine = EntryTester.Parser(debug=self.debug)
      engine.eval_entry_by_tests(
          json_data, 
          params["entry_tests"]
      )
      
      self.output.proc_test_result(json_data)
      return self.output.test_end(fp)
