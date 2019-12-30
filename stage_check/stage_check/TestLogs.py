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
    return TestLogs(test_id, config, args)


class TestLogs(AbstractTest.Linux, EntryTester.MatchFunction):
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
          "node_type"         : "primary",
          "log_path"          : "",
          "log_glob"          : "",
          "past_hours"        : 0,
          "extra_granularity" : False,
          "excludes"          : [],
          "patterns"          : [],
          "result"            : {}
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

      uptime_data = {}
      service_data = {}
      cores_data = []

      # Ugly....
      self.fp = fp
      error_lines = []
      logs_since_data = []
      logs_since = Linux.LogFilesSince(self.debug, progobj=self)
      shell_status = logs_since.run_linux_args(
          router_context, 
          params['node_type'], 
          params['log_path'],
          params['log_glob'],
          params['past_hours'],
          error_lines,
          logs_since_data
      )

      if len(error_lines) > 0:
          # Ugly...
          self.fp = None
          self.output.proc_run_linux_error(shell_status, error_lines[0])
          return self.output.test_end(fp)

      if self.debug:
          print('........ logs_since_data  ..........')
          pprint.pprint(logs_since_data)

      file_list = []
      for entry in logs_since_data:
          file_list.append(entry["file"])

      include_patterns = []
      for entry in params["patterns"]:
          include_patterns.append(entry["regex"])
      exclude_patterns = []
      for entry in params["excludes"]:
          exclude_patterns.append(entry)

      match_data = {}
      error_lines = []
      log_matches = Linux.LogFileMatches(
          self.debug, 
          progobj=self, 
          past_hours=params['past_hours'],
          extra_granularity=params['extra_granularity']
      )
      shell_status = log_matches.run_linux_args(
          router_context, 
          params['node_type'], 
          params['log_path'],
          file_list,
          include_patterns,
          exclude_patterns,
          error_lines,
          match_data
      )

      if len(error_lines) > 0:
          # Ugly...
          self.fp = None
          self.output.proc_run_linux_error(shell_status, error_lines[0])
          return self.output.test_end(fp)

      if self.debug:
          print('........ match_data flattened list ..........')
          pprint.pprint(match_data)

      # process json data
      match_data["total_patterns"] = 0
      if "patterns" in params:
          match_data["total_patterns"] = len(params["patterns"])
      for match in match_data["matches"]:
          for key in match_data:
              if key == "matches":
                  continue
              match[key] = match_data[key]
          match["past_hours"] = params["past_hours"]
          self.output.proc_pattern_matched(params, match)

      self.output.proc_test_result(params, match_data)
      self.output.test_end(fp)
