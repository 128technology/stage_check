"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputServicePing
except ImportError:
    import OutputServicePing


def create_instance():
    return OutputServicePingText()


class OutputServicePingText(OutputServicePing.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()
      self.message = "No Results to display..."


  def amend_no_data_in_reply(self, 
                             entry):
      """
      Invoked when a ping has been issued and here is missing address
      data in the ping reply.

      @entry
      @gateway - Pinging to/via this Service   
      """
      error_msg = f"{entry['tenant']}->{entry['service']}: No address info in reply"
      if not error_msg in self.message_list:
           self.message_list.append(f"{entry['tenant']}->{entry['service']}: No address info in reply")
      return True

  def amend_ping_error(self, 
                       entry,
                       error_message):
      """
      Invoked when a ping has been issued and an error reason is returned

      @entry
      @error_message
      """
      message = f"{entry['tenant']}->{entry['service']}: '{error_message}'"
      if not message in self.message_list:
          self.message_list.append(message)
      return True
     
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
      self.message_list.append(f"{entry['tenant']}->{entry['service']}: {ping_success_count}/{ping_count} " +
                               f"replies from {entry['destination-ip']}; " + 
                               f"average latency {average_reply_time:.2f}ms")
      return True


  def amend_ping_result_fail(self, 
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
       try:
           target = entry['destination-ip']
       except KeyError:
           target = entry['service']
       message = f"{entry['tenant']}->{entry['service']}: {ping_fail_count}/{ping_count} " +\
                 f"fails from {target}"
       if ping_fail_count != ping_count:
           message += f"; average latency xxx {average_reply_time:.2f}ms"
       self.message_list.append(message)
       return True


  def amend_test_result(self,
                        status,
                        entry_count,
                        entry_success_count,
                        entry_fail_count,
                        entry):
      """ 
      @status
      @entry_count
      @entry_success_count
      @entry_fail_count
      @entry
      """
      iterations = entry['iterations']

      if entry_count == 0:
          self.message = "No matching sevice entries!"

      if len(self.message_list) > 1:
          if self.status == Output.Status.OK:
              max_fail = iterations - entry["max_ping_failures"] 
              if max_fail > 0:
                  threshold_string = f"> {max_fail}/"
              else:
                  threshold_string = ""
              self.message = f"All {entry_success_count} service permutations received" \
                             f" {threshold_string}{iterations} replies"
          else:
              self.message = f"{entry_fail_count}/{entry_count} service permutations received < {iterations} replies"
      elif len(self.message_list) == 1:
          self.message = self.message_list.pop()
      return True
