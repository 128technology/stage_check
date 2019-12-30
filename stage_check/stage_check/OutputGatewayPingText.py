"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputGatewayPing
except ImportError:
    import OutputGatewayPing


def create_instance():
    return OutputGatewayPingText()

import pprint

class OutputGatewayPingText(OutputGatewayPing.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()
      self.message = "No Results to display..."

  def amend_cannot_ping_no_gateway(
      self,
      net_entry,
      addr_entry
      ):
      """
      Invoked if no gateway can be found for the network interface

      net_entry --
      addr_entry --
      """
      self.message_list.append(f"Cannot ping via NI {net_entry['name']}, No Gateway!")
      return True
      

  def amend_cannot_ping_dev_status(
      self,
      net_entry,
      addr_entry,
      intf_status
      ):
      """
      Invoked when ping cannot be completed due to the device interface 
      having oper status != OPER_UP or admin status != ADMIN_UP

      net_entry --
      addr_entry --
      intf_status --
      """
      message = f"Cannot ping via NI {net_entry['name']}, device status: {intf_status}"
      self.message_list.append(message)     
      return True


  def amend_no_data_in_reply(
      self, 
      net_entry, 
      addr_entry
      ):
      """
      Invoked when a ping has been issued and here is missing address
      data in the ping reply.

      net_entry  -- network interface
      addr_entry -- Pinging to/via this address's Gateway   
      """
      error_msg = f"{net_entry['name']} -> {addr_entry['test_gateway']}: " + \
                   "No address info in reply"
      if not error_msg in self.message_list:
           self.message_list.append(error_msg)
      return True

     
  def amend_no_address_in_reply(
      self,
      net_entry
      ):
      """
      Invoked when no address or gateway data is available for
      a network interface, and thus ping cannot be issued

      @net_entry  - Interface entry being processed
      """
      self.message_list.append(f"Skipping NI {net_entry['name']}: No address info in reply")
      return True


  def amend_ping_result_pass(
      self, 
      net_entry, 
      addr_entry,
      params
      ):
      """
      Invoked when all ping_count pings for a network interface receive responses
      
      net_entry --
      addr_entry --
      params --
      """
      if not params['omit_text_on_passing']:
          self.message_list.append(f"NI {net_entry['name']}: {addr_entry['ping_success_count']}/" +
                                   f"{addr_entry['ping_count']} replies from " +
                                   f"{addr_entry['target']}; " + 
                                   f"average latency {addr_entry['average_response_time']:.2f}ms")
      return True


  def amend_ping_result_fail(
      self, 
      net_entry, 
      addr_entry,
      params
      ):
      """
      Invoked when some of the pings for a network interface receive no response

      net_entry  -- 
      addr_entry --
      params --
      """
      fail_prefix = ''
      fail_suffix = ''
      if "red_text_for_ping_fails" in params and \
         params["red_text_for_ping_fails"]:
          fail_prefix = Output.Text.AnsiColors.red
          fail_suffix = Output.Text.AnsiModes.reset
      if addr_entry['ping_fail_count'] == 0:
          fail_prefix = ''
          fail_suffix = ''
      prefix = f"NI {net_entry['name']}"
      pad = ' ' * (len(prefix) + 1)
      string = f"{prefix}: {fail_prefix}{addr_entry['ping_fail_count']}/" + \
               f"{addr_entry['ping_count']}{fail_suffix} fails to {addr_entry['target']}; " + \
               f"average latency {addr_entry['average_response_time']:.2f}ms"
      self.message_list.append(string)
      if addr_entry['response_time_overages'] > 0:
          string = f"{pad} {addr_entry['response_time_overages']} pings"
          string += f" with latency > {params['max_single_response_time']}ms"
          self.message_list.append(string)
      if params['max_average_response_time'] > 0.0 and \
         addr_entry['average_response_time'] > params['max_average_response_time']:
          string = f"{pad}: average latency exceeds" 
          string += f" {params['max_average_response_time']}ms"
          self.message_list.append(string)
      return True


  def amend_test_result(
      self, 
      stats,
      params
      ):
      """ 
      @stats,
      @params
      """
      iterations = params['iterations']

      if stats["entry_count"] == 0:
          self.message = "No matching Network Interfaces!"
      elif stats["address_count"] == 0:
          self.message = "No matching Network Interfaces!"

      if len(self.message_list) > 1:
          if self.status == Output.Status.OK:
              self.message = f"Received {iterations}/{iterations} replies from" \
                             f" all {stats['address_pass']} matching GWs" \
                             f" ({stats['exclude_count']},{stats['address_exclude_count']} excluded)" 
          else:
              self.message = f"Issues detected for {stats['address_fail']}/" \
                             f"{stats['address_count']} interfaces ({stats['address_exclude_count']} excluded)"
              #assert False, pprint.pformat(self.message_list)
      elif len(self.message_list) == 1:
          self.message = self.message_list.pop()

      #assert False, 'stats: ' + pprint.pformat(stats) + '\nmsg: ' + self.message + '\nmsglist: ' + \
      #       pprint.pformat(self.message_list) + '\nstatus: ' + str(self.status)

      return True
