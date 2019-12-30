"""
"""
import pprint

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
    from stage_check import EntryTest
except ImportError:
    import EntryTest


def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance
   
    @test_id - test index number
    @config  - test parameters from configuration 
    @args    - command line args
    """
    return TestDeviceState(test_id, config, args)


class TestDeviceState(AbstractTest.GraphQL):
  """
  Test device interface state
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
          "status_tests"      : [],
          "default_status"    : Output.Status.OK,
          "exclude_tests"     : [],
          "device-interfaces" : []
      }
     
      params = self.apply_default_params(default_params)
      return params

  def run(self, local_info, router_context, gql_token, fp):
      """
      This test uses the gql engine to get device state state
      """
      # Process test parameters
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      params = self.get_params()

      # TODO either keep and implement as a parameter or toss
      include_list = params["device-interfaces"]

      # GraophQL Preperation
      qr = gql_helper.NodeGQL("allRouters", ['name'], [ router_context.get_router() ], debug=self.debug)
      qn = gql_helper.NodeGQL("nodes", ['name'])
      qd = gql_helper.NodeGQL("deviceInterfaces", [ 'name', 'state { operationalStatus }' ],
                                                    include_list)
      qr.add_node(qn)
      qn.add_node(qd)

      json_reply={}
      if not self.send_query(qr, gql_token, json_reply):
          return self.output.test_end(fp)

      flatter_json = qr.flatten_json(json_reply, 'router/nodes/deviceInterfaces', '/')

      router_context.set_allRouters_node_type(flatter_json)

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)

      # Run test / process results
      fail_count = 0
      warn_count = 0
      engine = EntryTest.Parser()
      for entry in flatter_json:
          try:
              if self.exclude_flat_entry(entry, params["exclude_tests"]):
                  continue
          except KeyError:
              pass
          
          test_status = engine.eval_entry_by_tests(entry, params["entry_tests"])
          if test_status == Output.Status.FAIL:
              self.output.proc_test_match(test_status, entry)
              fail_count += 1

          if test_status == Output.Status.WARN:
              self.output.proc_test_match(test_status, entry)
              warn_count += 1

      if fail_count > 0:
          self.output.proc_test_fail_result(fail_count)
      elif warn_count > 0:
          self.output.proc_test_warn_result(warn_count)

      return self.output.test_end(fp)

