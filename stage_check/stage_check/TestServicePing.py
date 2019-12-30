"""
"""
import pprint
import ipaddress

try:
    from stage_check import gql_helper
except ImportError:
    import gql_helper

try:
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest

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


def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance
   
    @test_id - test index number
    @config  - test parameters from, config 
    @args    - command line args
    """
    return TestServicePing(test_id, config, args)


class TestServicePing(AbstractTest.GraphQL, AbstractTest.Linux, EntryTester.MatchFunction):
  """
  This test first performs a Linux command to get /etc/hosts content and
  then issues a GraphQL command to peform the ServicePing, so it is a hybrid 
  of both test types...
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)
      self._hostsCommand = None

  def __clear_state(self):
      self._hostsCommand = None

  def requires_grapqhl(self):
      """
      Override
      """
      return True

  def get_params(self):
      """
      Some of these defaults (e.g. node_type) should be caught in
      the schema check, if they are missing...
      """
      default_params = {
         "node_type"             : "",
         "sequence"              : 1,
         "size"                  : 100,
         "timeout"               : 2,
         "iterations"            : 10,
         "dont-fragment"         : False,
         "service-ip-from-hosts" : False,
         "origin-router"         : "",
         "origin-node"           : "",
         "origin-service"        : "",
         "max_ping_failures"     : 0,
         "fail_status"           : "FAIL"
      }

      params = self.apply_default_params(default_params)
      return params

  def get_entry_params(self, entry, params):
      entry_defaults = params.copy()
      del entry_defaults["service-list"]
      adjusted_entry = entry.copy()
      for key in entry_defaults:
          if not key in adjusted_entry:
              adjusted_entry[key] = entry_defaults[key]
      return adjusted_entry

  def _update_entry_dest_ip(
          self, 
          local_info, 
          router_context, 
          node_type, 
          entry,
          fp=None
      ):
      """
      """
      if entry["service-ip-from-hosts"] == True and \
         not "destination-ip" in entry:
          if self._hostsCommand is None:
              self._hostsCommand = Linux.HostsFile(
                  debug=self.debug,
                  progobj=self
              )
              #json_data = {}
              json_data = []
              error_lines = []
              self.fp = fp
              status = self._hostsCommand.run_linux_args(
                  router_context, 
                  node_type, 
                  error_lines, 
                  json_data
              )
              self.fp = None
          addr = self._hostsCommand.get_first_address(entry["service"])
          if addr is not None:
              entry["destination-ip"] = addr

  def run(self, local_info, router_context, gql_token, fp):
      """
      Reads in a list of service information and  
      """
      self.__clear_state()
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      params = self.get_params()
      self.output.progress_start(fp)

      # This must be incremented with every request sent...
      identifier = 100
      entry_count = 0
      entry_fail_count = 0
      entry_success_count = 0

      # these do not change from query to query...
      gql_fields = [
          "status",
          "statusReason",
          "reachable",
          "sequence",
          "ttl",
          "responseTime" 
      ]

      for entry in params["service-list"]:
          ping_count = 0
          total_response_time   = float(0)
          average_response_time = float(0)
          ping_success_count    = 0
          ping_fail_count       = 0

          # apply defaults to each entry if not specified...
          entry = self.get_entry_params(entry, params)

          # populate router info if requested
          router_context._populate_config_fields(entry)

          seqno = entry["sequence"]
          self._update_entry_dest_ip(
              local_info, 
              router_context, 
              params["node_type"], 
              entry,
              fp
          )

          mandatory_keys = [ "tenant", "service", "destination-ip" ]
          failed_entry = False
          for key in mandatory_keys:
              if not key in entry:
                  failed_entry = True
                  self.output.proc_ping_error(entry, f"missing {key} parameter")  
          if failed_entry == True:
              entry_fail_count += 1
              self.output.proc_ping_result_fail(entry, 
                                                params["iterations"], 
                                                params["iterations"], 
                                                0.0)             
              continue


          router_name  = router_context.get_router()
          router_node  = router_context.get_node_name(entry["node_type"])
          service_name = entry["service"],
          if entry["origin-router"]  != "" and \
             entry["origin-node"] != "" and \
             router_context.local_role == "conductor":
              router_name = entry["origin-router"]
              router_node = entry["origin-node"]
              if entry["origin-service"] != "":
                  # ensures the correct service name is displayed
                  entry["service"] = entry["origin-service"]

          while ping_count < entry["iterations"]:
              identifier += 1

              api_name = "servicePing"
              gql_args = {
                   "routerName"    : router_name,
                   "nodeName"      : router_node,
                   "tenant"        : entry["tenant"],
                   "serviceName"   : entry["origin-service"],
                   "destinationIp" : entry["destination-ip"],
                   "identifier"    : identifier,
                   "sequence"      : seqno,
                   "size"          : entry["size"],
                   "dontFragBit"   : entry["dont-fragment"],
                   "timeout"       : entry["timeout"]
              }

              try:
                  gql_args["sourceIp"] = entry["sourceIp"]
              except KeyError:
                  pass
              
              now_message = f"Tenant {entry['tenant']}: ping {entry['service']} {ping_count}/{entry['iterations']} " + \
                            f"tmo={entry['timeout']}s"
              self.output.progress_display(now_message, fp)

              qsp = gql_helper.NewGQL(
                  api_name=api_name, 
                  api_args=gql_args, 
                  api_fields=gql_fields,
                  api_has_edges=False,
                  debug=self.debug
                  )
              json_ping_reply = {}
              qsp.api_flat_key = "/servicePing"
              qsp.single_entry_to_dict = True

              ping_count += 1
              seqno += 1

              if not self.send_query(qsp, gql_token, json_ping_reply):
              # standard graphql error processing may not be appropriate here as a failure can
              # be part of the test process w/o ruining the test.
                  ping_fail_count += 1
                  continue

              try:
                  # assert False, pprint.pformat(json_ping_reply)
                  # json_ping_reply = json_ping_reply[api_name]
                  # json_ping_reply = json_ping_reply[0]
                  status = json_ping_reply["status"]
                  if json_ping_reply['reachable'] == True and \
                     (status == "0" or \
                      status == "SUCCESS"):
                      ping_success_count   += 1
                      total_response_time  += float(json_ping_reply['responseTime'])
                      average_response_time = total_response_time / float(ping_success_count)
                  else:
                      if status == "ERROR" and \
                         len(json_ping_reply["statusReason"]) > 0:
                          self.output.proc_ping_error(entry, json_ping_reply["statusReason"])
                      ping_fail_count      += 1
              except (KeyError, TypeError, IndexError) as e:
                  self.output.proc_no_data_in_reply(entry)
                  ping_fail_count += 1
                  continue
                     
          #assert False, f"fails: {ping_fail_count} successes: {ping_success_count} cfg: {params['max_ping_failures']}"
          if ping_fail_count <= params["max_ping_failures"]:
               # fix this for multiple matching entries
               #assert False, f"fails: {ping_fail_count} successes: {ping_success_count} cfg: {params['max_ping_failures']}"
               entry_success_count += 1
               self.output.proc_ping_result_pass(entry,
                                                 ping_count, 
                                                 ping_success_count, 
                                                 average_response_time)             
          else:
               entry_fail_count += 1
               self.output.proc_ping_result_fail(entry, 
                                                 ping_count, 
                                                 ping_fail_count, 
                                                 average_response_time)             
      
      entry_count = len(params["service-list"])
      status = self.output.status
      if entry_count == 0:
          status = Output.Status.WARN
      elif entry_count != entry_success_count:
          status = Output.text_to_status(params["fail_status"])
      else:
          status = Output.Status.OK
          
      #assert False, f"OK? fails: {entry_fail_count} successes: {entry_success_count} " +\
      #              f"total: {entry_count} status: {status} {Output.status_to_text(status)}"

      self.output.proc_test_result(status, entry_count, 
                                   entry_success_count, 
                                   entry_fail_count, entry)
      return self.output.test_end(fp)


