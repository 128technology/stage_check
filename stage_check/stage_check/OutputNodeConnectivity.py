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
      self.__full_name = "OutputNodeConnectivity.Base"
      self.status = Output.Status.OK

  """
  empty_reply
  """

  def proc_empty_reply(self, status=None):
      if status is not None:
          self.status = status
      self.amend_empty_reply()
      return self.status

  def amend_empty_reply(self, status=None):
      return True

  """
  node_status_mismatch
  """

  def proc_node_status_mismatch(self, entry):
      self.status = Output.Status.FAIL
      self.amend_node_status_mismatch(entry)
      return self.status

  def amend_node_status_mismatch(self, entry):
      return True

  """
  test_result_too_few
  """

  def proc_test_result_too_few(self, entry_count, fail_count, params):
      self.status = Output.Status.FAIL
      self.amend_test_result_too_few(
           entry_count,
           fail_count,
           params
      )
      return self.status

  def amend_test_result_too_few(self, entry_count, fail_count, params):
      return True

  """
  test_result_wrong_state
  """

  def proc_test_result_wrong_state(self, fail_count, expected_entries, params):
      self.amend_test_result_wrong_state(
          fail_count, 
          expected_entries,
          params
      )
      return self.status

  def amend_test_result_wrong_state(self, fail_count, expected_entries, params):
      return True

  """
  test_result_all_ok
  """

  def proc_test_result_all_ok(self, entry_count, expected_entries, params):
      self.amend_test_result_all_ok(
          entry_count, 
          expected_entries,
          params
      )
      return self.status

  def amend_test_result_all_ok(self, entry_count, expected_entries, params):
      return True

  """
  test_result_bad_query
  """

  def proc_test_result_bad_query(self, query_status):
      self.status = Output.Status.WARN      
      self.amend_test_result_bad_query(query_status)
      return self.status

  def amend_test_result_bad_query(self, query_status):
      return True




