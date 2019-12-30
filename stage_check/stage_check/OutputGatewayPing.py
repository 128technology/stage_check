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

  def proc_cannot_ping_no_gateway(
      self,
      net_entry,
      address_entry,
      ):
      """
      Invoked if no gateway can be found for the network interface

      net_entry:
      address_entry:
      """
      self.amend_cannot_ping_no_gateway(
          net_entry,
          address_entry
      )
      return self.status


  def amend_cannot_ping_no_gateway(
      self,
      net_entry,
      address_entry
      ):
      """
      Invoked if no gateway can be found for the network interface

      net_entry:
      address_entry:
      """
      return True

  """
  cannot_ping_dev_status
  """

  def proc_cannot_ping_dev_status(
      self,
      net_entry,
      address_entry,
      intf_status
      ):
      """
      Invoked when ping cannot be completed due to the device interface 
      having operational status != OPER_UP or admin status != ADMIN_UP

      net_entry     --
      address_entry -- Can be None if interface is assigned a dynamic address
      intf_status   -- Problematic interface status
      """
      self.amend_cannot_ping_dev_status(
          net_entry,
          address_entry,
          intf_status
      )
      return self.status

  def amend_cannot_ping_dev_status(
      self,
      net_entry,
      address_entry,
      intf_status
      ):
      """
      Invoked when ping cannot be completed due to the device interface 
      having status != OPER_UP

      net_entry --
      address_entry -- Can be None if interface is assigned a dynamic address
      intf_status --
      """
      return True

  """
  no_data_in_reply
  """

  def proc_no_data_in_reply(
      self, 
      net_entry, 
      address_entry
      ):
      """
      Invoked when a ping has been issued and here is missing address
      data in the ping reply.

      net_entry --
      address_entry -- 
      """
      self.status = Output.Status.FAIL
      self.amend_no_data_in_reply(
          net_entry, 
          address_entry
      )
      return self.status

  def amend_no_data_in_reply(
      self, 
      net_entry, 
      address_entry
      ):
      """
      Invoked when a ping has been issued and here is missing address
      data in the ping reply.

      net_entry --
      address_entry --
      """
      return True

  """
  no_address_in_reply
  """
     
  def proc_no_address_in_reply(
      self,
      net_entry
      ):
      """
      Invoked when no address or gateway data is available for
      a network interface, and thus ping cannot be issued

      @net_entry  - Interface entry being processed
      """
      self.status = Output.Status.FAIL
      self.amend_no_address_in_reply(net_entry)
      return self.status

  def amend_no_address_in_reply(
      self,
      net_entry
      ):
      """
      @entry  - Interface entry being processed
      @ni_key - Key used to get interface name from entry   
      """
      return True

  """
  ping_result_pass
  """

  def proc_ping_result_pass(
      self, 
      net_entry, 
      address_entry,
      params
      ):
      """
      Invoked when all ping_count pings for a network interface receive responses

      net_entry --
      address_entry --
      """
      self.amend_ping_result_pass(              
          net_entry, 
          address_entry,
          params
      )
      return self.status


  def amend_ping_result_pass(
      self, 
      net_entry, 
      address_entry,
      params
      ):
      """
      Invoked when all ping_count pings for a network interface receive responses

      net_entry --
      address_entry --
      """
      return True

  """
  ping_result_fail
  """

  def proc_ping_result_fail(
      self, 
      net_entry, 
      address_entry,
      params
      ):
      """
      Invoked when some of the pings for a network interface receive no response

      net_entry, 
      address_entry,
      """
      self.amend_ping_result_fail(              
           net_entry, 
           address_entry,
           params
      )
      return self.status

  def amend_ping_result_fail(
      self, 
      net_entry,
      address_entry,
      params 
      ):
      """
      Invoked when all ping_count pings for a network interface receive responses

      net_entry --
      address_entry --
      """
      return True

  """
  test_result
  """

  def proc_test_result(self, 
                       status,
                       stats,
                       params):
      """ 
      @gateway_count
      @gateway_success_count
      """
      self.status = status
      self.amend_test_result(
          stats,
          params
      )
      return self.status

  def amend_test_result(self, 
                        stats,
                        params):
      """ 
      @gateway_count
      @gateway_success_count
      """
      return True
