"""
OutputPeerReachability Base Class.

This should only be inherited from.  Attempts to use this class
directly, or failure to overload the Base class will result in 
an Output.MissingOverload exception
"""

try:
    from stage_check import Output
except ImportError:
    import Output


class Base(Output.Base):
  def __init__(self):
      super().__init__()
      self.__full_name = "OutputIPSecStatus.Base"

  """
  process test rule matching data 
  """

  def proc_result(
          self,
          status,
          entry
      ):
      self.amend_result(status, entry)
      return self.status

  def amend_result(
          self,
          status,
          entry
      ):
      """
      Override in derived classes if required
      """
      return True

  """
  process errors returned in data
  """

  def proc_errors(
          self,
          entry
      ):
      self.amend_errors(entry)
      return Output.Status.NONE

  def amend_errors(
          self,
          entry
      ):
      """
      Override in derived classes if required
      """
      return True

  """
  overall test_result
  """

  def proc_test_result(
          self,
          entry_tests,
          stats,
          status = None
      ):
      if status is not None:
          self.status = status
      self.amend_test_result(
          entry_tests,
          stats
      )
      return self.status

  def amend_test_result(
          self, 
          entry_tests,
          stats
      ):
      """
      Override in derived classes if required
      """
      return True
