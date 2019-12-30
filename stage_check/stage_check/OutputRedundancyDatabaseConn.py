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
      self.__full_name = "OutputRedundancyDatabaseConn.Base"
      self.status = Output.Status.OK

  """
  no_node_data
  """

  def proc_no_node_data(self, local_info):
      """
      """
      self.status = Output.Status.WARN
      self.amend_no_node_data(local_info)
      return self.status

  def amend_no_node_data(self, local_info):
      """
      """
      return True

  """
  metric
  """

  def proc_entry_result(self, entry_tests, entry):
      """
      """
      self.amend_entry_result(entry_tests, entry)
      return self.status


  def amend_entry_result(self, entry_tests, entry):
      """
      """
      return True

  """
  missing_data
  """

  def amend_missing_data(self):
      """
      """
      self.amend_missing_data()
      return self.status

  def amend_missing_data(self):
      """
      """
      return True


  def proc_test_result(self, 
                       entry_tests,
                       stats,
                        status=None):
      if status is not None:
          self.status = status
      self.amend_test_result(
          entry_tests,
          stats
      )
      return self.status

  def amend_test_result(self, 
                        entry_tests, 
                        stats):
      return True


  def proc_unexpected_count(self, stats, expected_count):
      """
      """
      self.amend_unexpected_count(stats, expected_count)
      return self.status

  def amend_unexpected_count(self, stats, expected_count):
      """
      """
      return True



