"""
"""
import pprint
import re

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
    @config  - test parameters from configuration 
    @args    - command line args
    """
    return TestDeviceNamespace(test_id, config, args)


class TestDeviceNamespace(AbstractTest.Linux):
  """
  Tests to see if the requested device pattern matches in the 
  global namespace and/or the specified namespaces(s)
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)

  def get_params(self):
      # apply defaults
      default_params = {
          "node_type"              : "primary",
          "namespace-filter-regex" : "",
          "namespace-patterns"     : [],
          "global-filter-regex"    : "",
          "global-patterns"        : [],
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

      # First look in the requested namespace
      namespace_match_lines = []
      error_lines = []
      command = 'ip netns exec ' + params['namespace'] + ' ip a'
      shell_status = self.run_linux(local_info, router_context, params['node_type'], 
                                    command, params['namespace-filter-regex'],
                                    namespace_match_lines, error_lines, fp)
      #pprint.pprint(namespace_match_lines)
      ns_line_count = 0
      if len(error_lines) == 0:
          for line in namespace_match_lines:
              ns_line_count += 1

              if self.debug:
                  print(f'{ns_line_count}: {line}')

              patterns = params['namespace-patterns']
              for pattern in patterns:
                  #pprint.pprint(pattern)
                  matches = re.search(pattern['regex'], line, re.MULTILINE|re.DOTALL)
                  if matches is not None:
                      message = None
                      if 'banner' in pattern:
                          message = pattern['banner']
                      status = Output.text_to_status(pattern['status'])
                      list_message = self.line_to_message(line,
                          regex = pattern['regex'],
                          message_format = pattern['format'])
                      self.output.proc_namespace_match(status, message, list_message)
      else:
          self.output.progress_end()
          self.output.proc_run_linux_error(shell_status, error_lines[0])

      # Next look in the global namespace (for failures)
      line_count = 0
      if len(error_lines) == 0 and \
         self.output.is_status_ok():
          global_match_lines = []
          command = 'ip a'
          shell_status = self.run_linux(local_info, router_context, params['node_type'], 
                                        command, params['global-filter-regex'],
                                        global_match_lines, error_lines, fp)
          #pprint.pprint(global_match_lines)
          if len(error_lines) == 0:
              for line in global_match_lines:
                  line_count += 1
                  if self.debug:
                      print(f'{line_count}: {line}')
                  
                  patterns = params['global-patterns']
                  for pattern in patterns:
                      #pprint.pprint(pattern)
                      matches = re.search(pattern['regex'], line, re.MULTILINE|re.DOTALL)
                      if matches is not None:
                          if self.debug:
                              print(f"- Pattern {pattern['regex']} matches")
                          message = None
                          if 'banner' in pattern:
                              message = pattern['banner']
                          status = Output.text_to_status(pattern['status'])
                          list_message = self.line_to_message(line,
                              regex = pattern['regex'],
                              message_format = pattern['format'])
                          self.output.proc_namespace_match(status, message, list_message)
          else:
              self.output.progress_end()
              self.output.proc_run_linux_error(shell_status, error_lines[0])
  
      status = self.output.status
      if line_count == 0 and \
          ns_line_count == 0:
          status = Output.Status.FAIL
      
      self.output.proc_test_result(
          status, 
          ns_line_count, 
          line_count, 
          params
      )
      return self.output.test_end(fp)
