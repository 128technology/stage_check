###############################################################################
#  _____         _   _____ _       _   _           _                     
# |_   _|__  ___| |_| ____| |_ ___| | | | ___  ___| |_ ___   _ __  _   _ 
#   | |/ _ \/ __| __|  _| | __/ __| |_| |/ _ \/ __| __/ __| | '_ \| | | |
#   | |  __/\__ \ |_| |___| || (__|  _  | (_) \__ \ |_\__ \_| |_) | |_| |
#   |_|\___||___/\__|_____|\__\___|_| |_|\___/|___/\__|___(_) .__/ \__, |
#                                                           |_|    |___/ 
################################################################################                   
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
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest

try:
    from stage_check import Linux
except ImportError:
    import Linux


def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance
   
    @test_id - test index number
    @config  - test parameters from configuration 
    @args    - command line args
    """
    return TestEtcHosts(test_id, config, args)


class TestEtcHosts(AbstractTest.Linux, EntryTester.MatchFunction):
  """
  Tests to see if the requested device pattern matches in the 
  global namespace and/or the specified namespaces(s)
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)
      self.matching_tests = []
      self.test_output = []

  def __reset_test_state(self):
      self.matching_tests.clear()
      self.test_output.clear()

  def process_match(
      self,
      entry, 
      test_index, 
      test, 
      defaults
      ):
      """
      Invoked every time an entry_test sucessfully matches an entry. 
      """
      #assert False, pprint.pformat(test) + pprint.pformat(entry)
      format_string = ''
      if "test_exception" in entry and \
          entry["test_exception"] is not None:
          out_string = entry["test_exception"]
      else:
          if "format" in test:
             format_string = test["format"]
          elif "format" in defaults:
             format_string = defaults["format"]
          else:
             return 
          out_string = Output.populate_format(entry, format_string)

      self.matching_tests.append(test)
      self.test_output.append(out_string)


  def get_params(self):
      # apply defaults
      default_params = {
          "node_type"              : "all",
          "find_devices"           : False,
          "namespace"              : "",
          "linux_device"           : "",
          "entry_tests"            : [],
          "error-no-data"          : "Error no data found"
      }
     
      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      """
      """
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info,  status=Output.Status.OK)
      params = self.get_params()

      if self.check_user() != Output.Status.OK:
          return self.output.test_end(fp)

      self.output.progress_start(fp)
      router_context.query_node_info()

      hosts_command = Linux.HostsFile(
          debug=self.debug, 
          progobj=self
      )

      json_data   = []
      error_lines = []

      # Ugly....
      self.fp = fp
      shell_status = hosts_command.run_linux_args(
          router_context, 
          params["node_type"], 
          error_lines, 
          json_data
      )
      # Ugly...
      self.fp = None

      # populate test expressions with router-specific variables...
      router_context._populate_entry_tests(params['entry_tests'])
      if self.debug:
          print("@@@@@@@@@@@@@@@@@@@@@")
          pprint.pprint(params['entry_tests'])
          print("@@@@@@@@@@@@@@@@@@@@@")

      # reset results for multi-router invocation
      self.__reset_test_state()

      if self.debug:
          print("%%%%%%%%%%%%%%%%%%%%%%")
          pprint.pprint(self.test_output)
          pprint.pprint(self.matching_tests)
          print("%%%%%%%%%%%%%%%%%%%%%%")

      for hosts_entry in json_data:
          if len(error_lines) == 0:
              # This should return a list of all entry_test entries which FAIL
              # These will be passed to test.output
              engine = EntryTester.Parser(debug=False)
              engine.eval_tests_by_entry(hosts_entry, params['entry_tests'], self)
          else:
              self.output.proc_run_linux_error(shell_status, error_lines[0])
              return self.output.test_end(fp)

      if self.debug:
          print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
          print(f"output: {self.output.__class__.__name__}") 
          print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        
      self.output.proc_test_result(json_data, self.matching_tests, self.test_output, params)
      return self.output.test_end(fp)
