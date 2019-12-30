"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output


class Base(Output.Base):
  def __init__(self):
      super().__init__()
      self.__full_name = 'OutputFib.Base'

  """
  too_few_entries 
  """

  def proc_too_few_entries(
          self, 
          params, 
          stats
      ):
      self.status = Output.Status.FAIL
      self.amend_too_few_entries(
          params,
          stats
      )
      return self.status

  def amend_too_few_entries(
          self, 
          params, 
          stats
      ):
      return True

  """
  too_many_entries
  """

  def proc_too_many_entries(
          self, 
          params, 
          stats
      ):
      self.status = Output.Status.FAIL
      self.amend_too_many_entries(
          params,
          stats
      )
      return self.status

  def amend_too_many_entries(
          self, 
          params, 
          stats
      ):
      return True

  """
  test_match
  """

  def proc_test_match(
          self, 
          entry
      ):
      if "test_status" in entry and \
         entry["test_status"] == Output.Status.FAIL:
          self.status = entry["test_status"]
      self.amend_test_match(
          entry
      )

  def amend_test_match(
          self, 
          entry
      ):
      return True

  """
  test_result
  """

  def proc_test_result(
          self,
          params, 
          stats
      ):
      if not "fail_count" in stats:
         self.status = Output.Status.OK
      self.amend_test_result(
          params, 
          stats
      )
      
  def amend_test_result(
          self,
          params, 
          stats
      ):
      return True

