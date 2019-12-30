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

  def proc_metric(self, entry, entry_value):
      """
      """
      self.amend_metric(entry, entry_value)
      return self.status


  def amend_metric(self, entry, entry_value):
      """
      """
      return True

  """
  missing_data
  """

  def proc_missing_data(self):
      """
      """
      self.status = Output.Status.FAIL
      self.amend_missing_data() 
      return self.status

  def amend_missing_data(self):
      """
      """
      return True

  """
  """

  def proc_test_result(self, 
                       status,
                       entry_count, 
                       test_value, 
                       fail_count, 
                       expected_entries):
      """
      @entry_count
      @test_value 
      @fail_count 
      @expected_entries
      """
      if status is not None:
          self.status = status
      self.amend_test_result(
          entry_count, 
          test_value, 
          fail_count, 
          expected_entries
      )
      return self.status

  def amend_test_result(self, 
                        entry_count, 
                        test_value, 
                        fail_count, 
                        expected_entries):
      """
      @entry_count
      @test_value 
      @fail_count 
      @expected_entries
      """
      return True

  """
  """

  def proc_test_result_bad_values(self, 
                                  entry_count, 
                                  test_value, 
                                  fail_count, 
                                  expected_entries):
      """
      @entry_count
      @test_value 
      @fail_count 
      @expected_entries
      """
      self.amend_test_result_bad_values(
          entry_count, 
          test_value, 
          fail_count, 
          expected_entries
      )
      return self.status

  def amed_test_result_bad_values(self, 
                                  entry_count, 
                                  test_value, 
                                  fail_count, 
                                  expected_entries):
      """
      @entry_count
      @test_value 
      @fail_count 
      @expected_entries
      """
      return True


