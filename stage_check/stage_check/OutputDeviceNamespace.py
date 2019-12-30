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
      self.__full_name = "OutputDeviceNamespace.Base"

  """
  namespace_match
  """

  def proc_namespace_match(self,
                           status,
                           message,
                           list_message):
      """
      @status
      @message
      @list_message
      """
      if status is not None:
          self.status = status
      self.amend_namespace_match(
          message,
          list_message
      )
      return self.status

  def amend_namespace_match(self,
                            message,
                            list_message):
      """
      Derived classes should overload this method if necessary      

      @message
      @list_message
      """
      return True

  """
  run_linux_error 
  """ 

  def proc_run_linux_error(self,
                           return_status,
                           error_string):
      """
      @return_status
      @error_string
      """
      self.status  = Output.Status.FAIL
      self.amend_run_linux_error(
          return_status,
          error_string
      )
      return self.status

  def amend_run_linux_error(self,
                            return_status,
                            error_string):
      """
      @return_status
      @error_string
      """
      return True
    
  """
  test_result
  """

  def proc_test_result(self,
                       status,
                       ns_line_count,
                       line_count,
                       test_params):
      """
      @ns_line_count  - Matching line count, specified namespace
      @line_count     - Matching line count, global namespace
      @test_params    - Test parameters
      """
      if status is not None:
          self.status = status
      self.amend_test_result(
          ns_line_count,
          line_count,
          test_params
       )
      return self.status
      

  def amend_test_result(self,
                        ns_line_count,
                        line_count,
                        test_params):
      """
      @ns_line_count  - Matching line count, specified namespace
      @line_count     - Matching line count, global namespace
      @test_params    - Test parameters
      """
      return True

