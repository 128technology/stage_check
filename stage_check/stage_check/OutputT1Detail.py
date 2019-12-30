"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

class Base(Output.Base):
  def __init__(self):
      super().__init__()
      self.__full_name = 'OutputT1Detail.Base'

  def proc_run_linux_error(self, 
                           shell_status, 
                           error_line):
      self.status  = Output.Status.FAIL
      self.amend_run_linux_error(
          shell_status, 
          error_line
          )
      return self.status

  def amend_run_linux_error(self, 
                            shell_status, 
                            error_line):
      return True

  """
  amend_test_result
  """

  def proc_test_result(
      self, 
      results, 
      params, 
      command
      ):
      if len(results) > 0:
          self.status = Output.Status.FAIL
      else:
          self.status = Output.Status.OK
      self.amend_test_result(
          results, 
          params, 
          command
          )
      return self.status

  def amend_test_result(
      self, 
      results, 
      params, 
      command
      ):
      return True

