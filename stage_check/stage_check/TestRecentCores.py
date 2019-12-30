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

  def get_params(self):
      # apply defaults
      default_params = {
          "node_type"      : "primary",
          "service"        : "128T",
          "exclude_tests"  : []
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

      uptime_data = {}
      service_data = {}
      cores_data = []

      # Ugly....
      self.fp = fp
      error_lines = []
      uptime = Linux.Uptime(self.debug, progobj=self)
      shell_status = uptime.run_linux_args(
          local_info, 
          router_context, 
          params['node_type'], 
          error_lines,
          uptime_data
      )

      if len(error_lines) > 0:
          # Ugly...
          self.fp = None
          self.output.proc_run_linux_error(shell_status, error_lines[0])
          return self.output.test_end(fp)

      if self.debug:
          print('........ uptime flattened list ..........')
          pprint.pprint(uptime_data)

      error_lines = []
      sys_status = Linux.SystemctlStatus(self.debug, progobj=self)
      shell_status = sys_status.run_linux_args(
          local_info, 
          router_context, 
          params['node_type'], 
          params['service'], 
          error_lines,
          service_data
      )

      if len(error_lines) > 0:
          # Ugly...
          self.fp = None
          self.output.proc_run_linux_error(shell_status, error_lines[0])
          return self.output.test_end(fp)

      if self.debug:
          print('........ systemctl flattened list ..........')
          pprint.pprint(service_data)

      error_lines = []
      cores = Linux.Coredumpctl(self.debug, progobj=self)
      shell_status = cores.run_linux_args(
          local_info, 
          router_context, 
          params['node_type'], 
          error_lines,
          cores_data
      )
      # Ugly...
      self.fp = None

      if len(error_lines) > 0:
          self.output.proc_run_linux_error(shell_status, error_lines[0])
          return self.output.test_end(fp)

      if self.debug:
          print('........ cores flattened list ..........')
          pprint.pprint(cores_data)

      status = Output.Status.OK
      uptime_cores = cores.cores_newer_than_secs(
          uptime_data['uptime_as_seconds']
      )
      if len(uptime_cores) > 0:
         self.output.proc_uptime_match(uptime_cores)
         status = Output.Status.WARN

      # TODO -- add error if epoch_time does not exist???
      service_cores = []
      if 'epoch_time' in service_data:
          service_cores = cores.cores_newer_than_epoch(
              service_data['epoch_time']
          )
      if len(service_cores) > 0:
         self.output.proc_service_match(params['service'], service_cores)
         status = Output.Status.WARN

      node_name = router_context.get_node_by_type(params['node_type'])
      message = f"{node_name}:  Uptime OS: {uptime_data['uptime_days']}d " + \
                f"{uptime_data['uptime_hours']}h {uptime_data['uptime_minutes']}m  " + \
                " 128T: "
      if service_data["uptime_days"] > 0:
          message += f"{service_data['uptime_days']}d "
      message += f"{service_data['uptime_hours']}h " 
      message += f"{service_data['uptime_minutes']}m"
      if service_data["uptime_days"] == 0:
          message += f" {service_data['uptime_seconds']}s"   

      self.output.proc_test_result(message, status)
      self.output.test_end(fp)
