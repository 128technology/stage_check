"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

class Base(Output.Base):
  def __init__(self, fullName='OutputLteLinux.Base'):
      super().__init__()
      self.__full_name = fullName

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


  def proc_exception(
      self, 
      dev_linux, 
      dev_128, 
      exception
      ): 
     return self.amend_exception(
        dev_linux, 
        dev_128, 
        exception
     )

  def amend_exception(
      self, 
      dev_128, 
      dev_linux, 
      exception
      ):
      return True

  def proc_missing_json(
      self, 
      json_data 
      ): 
     return self.amend_missing_json(
        json_data
     )

  def amend_missing_json(
      self, 
      json_data 
      ):
      return True

  def proc_no_128_config(
      self,
      linux_info
      ):
      self.status = Output.Status.FAIL
      self.amend_no_128_config(linux_info)
      return self.status

  def amend_no_128_config(
      self, 
      linux_info, 
      ):
      return True

  def proc_no_linux_device(
      self,
      t128_info
      ):
      self.status = Output.Status.FAIL
      self.amend_no_linux_device(t128_info)
      return self.status

  def amend_no_linux_device(
      self, 
      t128_info, 
      ):
      return True

  """
  amend_test_result
  """
  def proc_test_result(
      self, 
      status,
      all_linux,
      matching_linux,
      t128_entries,
      stats
      ):
      self.status = status
      self.amend_test_result(
          all_linux,
          matching_linux, 
          t128_entries,
          stats
          )
      return self.status

  def amend_test_result(
      self, 
      all_entries,
      matching_linux, 
      t128_entries,
      stats
      ):
      return True

