"""
"""
import pprint
import re

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import EntryTest
except ImportError:
    import EntryTest

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
    return TestT1Detail(test_id, config, args)


class TestT1Detail(AbstractTest.Linux, EntryTest.MatchFunction):
  """
  Tests to see if the requested device pattern matches in the 
  global namespace and/or the specified namespaces(s)
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)
      self.results = []

  def process_match(
      self,
      entry, 
      test_index, 
      test, 
      defaults
      ):
      """
      Invoked every time an entry_test sucessfully then entry. See
      test_json_values()
      """
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
      self.results.append(out_string)

  def get_params(self):
      # apply defaults
      default_params = {
          "node_type"              : "secondary",
          "namespace"              : "",
          "linux-device"           : "",
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

      if self.check_user("root") != Output.Status.OK:
          return self.output.test_end(fp)

      self.output.progress_start(fp)
      router_context.query_node_info()

      json_data   = {}
      error_lines = []

      t1_detail = Linux.T1Detail(
          debug=self.debug, 
          progobj=self
      )

      # Ugly....
      self.fp = fp
      shell_status = t1_detail.run_linux_args(
          local_info, 
          router_context, 
          params['node_type'], 
          params['namespace'], 
          params['linux_device'], 
          error_lines,
          json_data
      )
      # Ugly...
      self.fp = None

      # reset results for multi-router invocation
      self.results = []

      if len(error_lines) == 0:
          # This should return a list of all entry_test entries which FAIL
          # These will be passed to test.output
          engine = EntryTest.Parser(debug=False)
          engine.eval_tests_by_entry(json_data, params['entry_tests'], self)
      else:
          self.output.proc_run_linux_error(shell_status, error_lines[0])
          return self.output.test_end(fp)

      command = t1_detail.get_command(params['namespace'], params['linux_device'])
      self.output.proc_test_result(self.results, params, command)
      return self.output.test_end(fp)
