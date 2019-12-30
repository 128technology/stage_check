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
      self.__full_name = "OutputDeviceState.Base"
      self.status = Output.Status.OK

  """
  test_match
  """

  def proc_dev_result(self, status, entry):
      """
      @status
      @entry
      """
      self.amend_dev_result(status, entry)
      return self.status

  def amend_dev_result(self, status, entry):
      """
      @status
      @entry
      """
      return True

  """
  test_result
  """

  def proc_test_result(self, entry_tests, stats):
      """
      @status
      @entry
      """
      self.amend_test_result(entry_tests, stats)
      return self.status

  def amend_test_result(
          self, 
          entry_tests,
          stats
      ):
      return True 


