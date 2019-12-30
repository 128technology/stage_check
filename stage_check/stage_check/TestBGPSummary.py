"""
"""
import re
import pprint

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
    @config  - test parameters from, config 
    @args    - command line args
    """
    return TestBGPSummary(test_id, config, args)

class TestBGPSummary(AbstractTest.Linux):
  """
  FRR BGP Summary is not likely to be available in GRAPHQL (or NETCONF
  for that matter) anytime soon.

  Instead this test can be run only as user root in Linux, either
  using t128-salt from the conductor, or urunning the command
  vtysh -c 'show ip bgp summary' directly from the Linux shell.
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)

  def get_params(self):
      """
      The default is nonsensical, if this parameter is
      not provided it ought to be caught by the schema
      """
      default_params = {
         "minimum_count" : 0,
         "exclude_tests" : [],
         "entry_tests" : {}
      }
     
      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      status = Output.Status.OK

      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info, status=status)      
      params = self.get_params()

      self.output.progress_start(fp)

      if self.check_user() != Output.Status.OK:
          return self.output.test_end(fp)

      router_context.query_node_info()

      # find the node with the active RouteManager and its primary etc.
      active_node_id   = router_context.active_process_node('routingManager')
      if active_node_id == '':
          self.output.proc_inactive_routing_manager(local_info, router_context)
          return self.output.test_end(fp)
              
      active_node_type = router_context.node_type(active_node_id)
      if router_context.local_role != 'conductor' and \
         local_info.get_node_name() != active_node_id:
          self.output.proc_inactive_routing_manager(local_info, router_context)
          return self.output.test_end(fp)

      error_lines = []
      json_data   = []
      bs = Linux.BGPSummary(self.debug, progobj=self)
      # ugly..
      self.fp = fp
      retval = bs.run_linux_args(
          router_context, 
          active_node_type, 
          error_lines, 
          json_data
       )
      # ugly...
      self.fp = None
 
      # Lame, but currently the only way to detect an error...
      if len(error_lines) > 0:
          self.output.proc_run_linux_error(retval, error_lines[0])
          return self.output.test_end(fp)

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(json_data)

      stats = {}
      Output.init_result_stats(stats)
      stats["total_count"] = len(json_data) 

      if params["minimum_count"] > 0 and \
         stats["total_count"] < params["minimum_count"]:
          self.output.proc_too_few_peers(stats, params)
          return self.output.test_end(fp)     

      engine = EntryTester.Parser(self.debug)
      for entry in json_data:
          if engine.exclude_entry(entry, params["exclude_tests"]):
              stats["exclude_count"] += 1
              continue
          test_result = engine.eval_entry_by_tests(
              entry,
              params["entry_tests"]
          )
          Output.update_stats(stats, test_result)
          self.output.proc_entry_result(entry)

      if stats["FAIL"] > 0:
         status = Output.Status.FAIL
      elif stats["WARN"] > 0: 
         status = Output.Status.WARN
      elif stats["PASS"] == stats["total_count"]:
         status = Output.Status.OK

      self.output.proc_test_result(
          active_node_id, 
          params["entry_tests"],
          stats,
          status=status
      )
      return self.output.test_end(fp)


