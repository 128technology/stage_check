"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output


class Base(Output.Base):
  def __init__(self):
      super().__init__()
      self.__full_name = 'OutputProcessStates.Base'

  """
  interim_result
  """

  def proc_interim_result(self, entry, status=None):
      if status is not None:
          self.status = status
      self.amend_interim_result(
          entry, 
          status=status
      )
      return self.status

  def amend_interim_result(self, entry, status=None):
      """
      Override this method if necessary
      """
      return True

  """
  test_result
  """

  def proc_test_result(self, 
                       entry_test,
                       stats,
                       status=None):
      if status is not None:
          self.status = status
      self.amend_test_result(
          entry_test,
          stats
      )
      return self.status

  def amend_test_result(
          self, 
          no_match, 
          stats) : 
      """
      Override this method if necessary
      """
      return True      

