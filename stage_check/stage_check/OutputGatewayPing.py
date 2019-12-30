"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

class Base(Output.Base):
  """
  """
  def __init__(self):
      super().__init__()
      self.__full_name = "OutputGatewayPing.Base"
      self.status = Output.Status.OK

  """
  cannot_ping_no_gateway
  """

  def proc_cannot_ping_no_gateway(self,
                                 entry,
                                 ni_key):
      """
      Invoked if no gateway can be found for the network interface

      @entry
      @ni_key
      """
      self.amend_cannot_ping_no_gateway(
          entry, 
          ni_key
      )
      return self.status


  def amend_cannot_ping_no_gateway(self,
                                   entry,
                                   ni_key):
      """
      Invoked if no gateway can be found for the network interface

      @entry
      @ni_key
      """
      return True

  """
  cannot_ping_dev_status
  """

  def proc_cannot_ping_dev_status(self,
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
      self.amend_cannot_ping_dev_status(
          entry,
          ni_key,
          status
      )
      return self.status

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
      return True

  """
  no_data_in_reply
  """

  def proc_no_data_in_reply(self, 
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
      self.status = Output.Status.FAIL
      amend_no_data_in_reply(
          entry, 
          ni_key,
          gateway
      )
      return self.status

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
      return True

  """
  no_address_in_reply
  """
     
  def proc_no_address_in_reply(self,
                               entry,
                               ni_key):
      """
      Invoked when no address or gateway data is available for
      a network interface, and thus ping cannot be issued

      @entry  - Interface entry being processed
      @ni_key - Key used to get interface name from entry   
      """
      self.status = Output.Status.FAIL
      self.amend_no_address_in_reply(entry, ni_key)
      return self.status

  def amend_no_address_in_reply(self,
                                entry,
                                ni_key):
      """
      @entry  - Interface entry being processed
      @ni_key - Key used to get interface name from entry   
      """
      return True

  """
  ping_result_pass
  """

  def proc_ping_result_pass(self, 
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
       self.amend_ping_result_pass(              
           entry, 
           ni_key,
           ping_count, 
           ping_success_count, 
           target, 
           average_reply_time
       )
       return self.status


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
       return True

  """
  ping_result_fail
  """

  def proc_ping_result_fail(self, 
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
       self.amend_ping_result_fail(              
           entry, 
           ni_key,
           ping_count, 
           ping_fail_count, 
           target, 
           average_reply_time
       )
       return self.status

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
       return True

  """
  test_result
  """

  def proc_test_result(self, 
                       status,
                       gateway_count,
                       gateway_success_count,
                       gateway_fail_count,
                       params):
      """ 
      @gateway_count
      @gateway_success_count
      """
      self.status = status
      self.amend_test_result(
          gateway_count,
          gateway_success_count,
          gateway_fail_count,
          params
      )
      return self.status

  def amend_test_result(self, 
                        gateway_count,
                        gateway_success_count,
                        gateway_fail_count,
                        params):
      """ 
      @gateway_count
      @gateway_success_count
      """
      return True
