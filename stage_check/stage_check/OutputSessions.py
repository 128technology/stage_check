"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output


class Base(Output.Base):
  def __init__(self):
      super().__init__()
      self.__full_name = "OutputSessions.Base"

  """
  test_result
  """
  def proc_test_result(
          self, 
          status,
          matching_flows,
          stats,
          params
      ):
      """
      """
      if status is not None:
          self.status = status
      self.amend_test_result(
          matching_flows,
          stats,
          params
      )
      return self.status

  def amend_test_result(
          self, 
          matching_flows,
          stats,
          params
      ):
      """
      """
      return True
