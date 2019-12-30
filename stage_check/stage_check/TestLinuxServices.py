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
    return TestLinuxServices(test_id, config, args)


class TestLinuxServices(AbstractTest.Linux):
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
          "services"      : [ "128T" ],
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

      if self.check_user() != Output.Status.OK:
          return self.output.test_end(fp)

      params = self.get_params()
      exclude_tests = params["exclude_tests"]
      entry_tests = params["entry_tests"]
      no_match = {}
      if "no_match" in entry_tests:
          no_match = entry_tests["no_match"]

      services = params['services']
      service_data = []
      error_lines = []
      sys_status = Linux.SystemctlStatus(self.debug, progobj=self)
      shell_status = sys_status.run_linux_args(
          router_context, 
          params['node_type'], 
          services, 
          error_lines,
          service_data
      )

      if len(error_lines) > 0:
          # Ugly...
          self.fp = None
          self.output.proc_run_linux_error(shell_status, error_lines[0])
          return self.output.test_end(fp)

      router_context.set_allRouters_node_type(service_data, node_name_key="nodeName")

      if self.debug:
          print('........ systemctl flattened list ..........')
          pprint.pprint(service_data)

      stats = {}
      Output.init_result_stats(stats)
      stats["total_count"] = len(services)

      engine = EntryTester.Parser(debug=self.debug)
      for entry in service_data:
          if engine.exclude_entry(entry, exclude_tests):
              stats["exclude_count"] += 1
              continue
          test_status = engine.eval_entry_by_tests(entry, params["entry_tests"])
          Output.update_stats(stats, test_status)
          if test_status != None:
              self.output.proc_interim_result(entry, status=test_status)

      #########################################################################
      # v1.8.3: This is a workaround for Linux module command output not 
      #         returning all results (suspect python subprocess module).
      #########################################################################
      for service in services:
          service_present = False
          for entry in service_data:
              if service == entry["service"]:
                  service_present = True
                  break
          if service_present == False:
              faux_entry = sys_status.new_entry(service)
              faux_entry["test_format"] = "Service {service} not found"
              stats["FAIL"] += 1
              stats["match_count"] += 1
              self.output.proc_interim_result(faux_entry, status=Output.Status.FAIL)

      # All pass versus fail decisions belong outside of the output module
      if stats["FAIL"] > 0:
          self.output.proc_test_result(entry_tests, stats, status=Output.Status.FAIL)
      else:
          self.output.proc_test_result(entry_tests, stats, status=Output.Status.OK)

      return self.output.test_end(fp)

