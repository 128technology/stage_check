"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputDeviceNamespace
except ImportError:
    import OutputDeviceNamespace


def create_instance():
    return OutputDeviceNamespaceText()

class OutputDeviceNamespaceText(OutputDeviceNamespace.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def add_namespace_match(self,
                          status,
                          message,
                          list_message):
      """
      @status
      @message
      @list_message
      """
      self.status = status
      if message is not None and message != '':
          self.message = message
      if list_message is not None and list_message != '':
          self.message_list.append(list_message)
      return self.status

  def amend_namespace_match(self,
                            message,
                            list_message):
      """
      @message
      @list_message
      """
      if message is not None and message != '':
          self.message = message
      if list_message is not None and list_message != '':
          self.message_list.append(list_message)
      return True

  def amend_run_linux_error(self,
                            return_status,
                            error_string):
      """
      @return_status
      @error_string
      """
      self.message = error_string
      return True
    
  def amend_test_result(self,
                        ns_line_count,
                        line_count,
                        params):
    """
    @ns_line_count  - Matching line count, specified namespace
    @line_count     - Matching line count, global namespace
    @test_params    - Test parameters
    """
    if self.message is None:
        if line_count == 0 and ns_line_count == 0:
            self.message = params['error-no-data']
        elif len(self.message_list) > 0:
            self.message = self.message_list.pop(0)
    return True

