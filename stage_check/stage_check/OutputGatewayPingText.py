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


class OutputGatewayPingText(OutputGatewayPing.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()
      self.message = "No Results to display..."

  def amend_cannot_ping_no_gateway(self,
                                   entry,
                                   ni_key):
      """
      Invoked if no gateway can be found for the network interface

      @entry
      @ni_key
      """
      self.message_list.append(f'Cannot ping via NI {entry[ni_key]}, No Gateway!')
      return True
      

  def amend_cannot_ping_dev_status(self,
                                   entry,
                                   ni_key,
                                   status):
      """
      Invoked when ping cannot be completed due to the device interface 
      having status != OPER_UP

      @entry
      @ni_key
      @status
      """
      self.message_list.append(f'Cannot ping via NI {entry[ni_key]}, device status: {status}')     
      return True


  def amend_no_data_in_reply(self, 
                             entry, 
                             ni_key,
                             gateway):
      """
      Invoked when a ping has been issued and here is missing address
      data in the ping reply.

      @entry
      @ni_key  - Key used to get interface name from entry   
      @gateway - Pinging to/via this Gateway   
      """
      error_msg = f"{entry[ni_key]} -> {gateway}: No address info in reply"
      if not error_msg in self.message_list:
           self.message_list.append(f"{entry[ni_key]} -> {gateway}: No address info in reply")
      return True

     
  def amend_no_address_in_reply(self,
                                entry,
                                ni_key):
      """
      Invoked when no address or gateway data is available for
      a network interface, and thus ping cannot be issued

      @entry  - Interface entry being processed
      @ni_key - Key used to get interface name from entry   
      """
      self.message_list.append(f"Skipping NI {entry[ni_key]}: No address info in reply")
      return True


  def amend_ping_result_pass(self, 
                             entry, 
                             ni_key,
                             ping_count, 
                             ping_success_count, 
                             target, 
                             average_reply_time):
      """
      Invoked when all ping_count pings for a network interface receive responses
      
      @entry,
      @ni_key,
      @ping_count, 
      @ping_success_count, 
      @target, 
      @average_reply_time
      """
      self.message_list.append(f"NI {entry[ni_key]}: {ping_success_count}/{ping_count} replies from {target}; " + 
                                f"average latency {average_reply_time:.2}ms")
      return True


  def amend_ping_result_fail(self, 
                             entry, 
                             ni_key,
                             ping_count, 
                             ping_fail_count, 
                             target, 
                             average_reply_time):
       """
       Invoked when some of the pings for a network interface receive no response

       @entry, 
       @ni_key,
       @ping_count, 
       @ping_success_count, 
       @target, 
       @average_reply_time
       """
       self.message_list.append(f"NI {entry[ni_key]}: {ping_fail_count}/{ping_count} fails to {target}; " +
                                f"average latency {average_reply_time:.2}ms")
       return True


  def amend_test_result(self, 
                        gateway_count,
                        gateway_success_count,
                        gateway_fail_count,
                        params):
      """ 
      @gateway_count
      @gateway_success_count
      @gateway_fail_count
      @params
      """
      iterations = params['iterations']

      if gateway_count == 0:
          self.message = "No matching Network Interfaces!"

      if len(self.message_list) > 1:
          if self.status == Output.Status.OK:
              self.message = f"All {gateway_success_count} matching NIs received" \
                             f" {iterations}/{iterations} replies"
          else:
              self.message = f"Some matching NIs received < {iterations} replies"
      elif len(self.message_list) == 1:
          self.message = self.message_list.pop()
      return True
