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
      self.__full_name = "OutputServicePing.Base"
      self.status = Output.Status.OK

  def proc_no_data_in_reply(self, 
                            entry): 
      """
      Invoked when a ping has been issued and here is missing address
      data in the ping reply.

      @entry
      """
      self.status = Output.Status.FAIL
      self.amend_no_data_in_reply(
          entry
      )
      return self.status

  def amend_no_data_in_reply(self, 
                             entry):
      """
      Invoked when a ping has been issued and here is missing address
      data in the ping reply.

      @entry
      """
      return True

  def proc_ping_error(self, 
                       entry,
                       error_message): 
      """
      Invoked when a ping has been issued and an error is returned

      @entry
      @error_message
      """
      self.status = Output.Status.FAIL
      self.amend_ping_error(
          entry,
          error_message
      )
      return self.status

  def amend_ping_error(self, 
                       entry,
                       error_message):
      """
      Invoked when a ping has been issued and an error reason is returned

      @entry
      @error_message
      """
      return True

  def proc_ping_result_pass(self, 
                            entry, 
                            ping_count, 
                            ping_success_count, 
                            average_reply_time):
       """
       Invoked when all ping_count pings for a network interface receive responses

       @entry,
       @ping_count, 
       @ping_success_count, 
       @average_reply_time
       """
       self.amend_ping_result_pass(              
           entry, 
           ping_count, 
           ping_success_count, 
           average_reply_time
       )
       return self.status


  def amend_ping_result_pass(self, 
                             entry, 
                             ping_count, 
                             ping_success_count, 
                             average_reply_time):
       """
       Invoked when all ping_count pings for a network interface receive responses

       @entry,
       @ping_count, 
       @ping_success_count, 
       @average_reply_time
       """
       return True

  """
  ping_result_fail
  """

  def proc_ping_result_fail(self, 
                            entry, 
                            ping_count, 
                            ping_fail_count, 
                            average_reply_time):
       """
       Invoked when some of the pings for a network interface receive no response

       @entry, 
       @ping_count, 
       @ping_success_count, 
       @average_reply_time
       """
       self.amend_ping_result_fail(              
           entry, 
           ping_count, 
           ping_fail_count, 
           average_reply_time
       )
       return self.status

  def amend_ping_result_fail(self, 
                             entry, 
                             ping_count, 
                             ping_success_count, 
                             average_reply_time):
       """
       Invoked when all ping_count pings for a network interface receive responses

       @entry,
       @ping_count, 
       @ping_success_count, 
       @average_reply_time
       """
       return True

  """
  test_result
  """

  def proc_test_result(self, 
                       status,
                       entry_count,
                       entry_success_count,
                       entry_fail_count,
                       entry):
      """ 
      @gateway_count
      @gateway_success_count
      """
      self.status = status
      self.amend_test_result(
          status,
          entry_count,
          entry_success_count,
          entry_fail_count,
          entry
      )
      return self.status

  def amend_test_result(self,
                        status,
                        entry_count,
                        entry_success_count,
                        entry_fail_count,
                        entry):
      """ 
      @gateway_count
      @gateway_success_count
      """
      return True
