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

  def proc_test_match(self, status, entry):
      """
      @status
      @entry
      """
      self.amend_test_match(entry)
      return self.status

  def amend_test_match(self, entry):
      """
      @status
      @entry
      """
      return True

  """
  test_fail_result
  """

  def proc_test_fail_result(self, count):
      """
      @count
      """
      self.status = Output.Status.FAIL
      self.amend_test_fail_result(count)
      return self.status

  def amend_test_fail_result(self, count):
      """
      @count
      """
      return True

  """
  test_warn_result
  """

  def proc_test_warn_result(self, count):
      """
      @count
      """
      self.status = Output.Status.WARN
      self.amend_test_warn_result(count)
      return self.status

  def amend_test_warn_result(self, count):
      """
      @count
      """
      return True

