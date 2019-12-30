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
      self.__full_name = "OutputServiceConfig.Base"
      self.status = Output.Status.OK

  """
  config_error
  """

  def proc_config_error(self, params, message):
      """
      @params
      @message
      """
      self.amend_config_error(params, message)
      return self.status

  def amend_config_error(self, params, message):
      """
      @params
      @message
      """
      return True

  """
  test_match
  """

  def proc_test_match(self, entry):
      """
      @status
      @entry
      """
      self.amend_test_match(entry)
      return self.status

  def amend_test_match(self, entry):
      """
      @entry
      """
      return True

  """
  entry_count
  """

  def proc_entry_count(self, params, stats):
      """
      @params
      @stats
      """
      self.amend_entry_count(params, stats)
      return self.status

  def amend_entry_count(self, params, stats):
      """
      @params
      @stats
      """
      return True

  """
  test_result
  """

  def proc_test_result(self, entry_tests, stats):
      """
      stats
      """
      self.amend_test_result(entry_tests, stats)
      return self.status

  def amend_test_result(self, entry_tests, stats):
      """
      stats
      """
      return True


