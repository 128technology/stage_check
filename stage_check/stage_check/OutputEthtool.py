"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output


class Base(Output.Base):
  def __init__(self):
      super().__init__()
      self.__full_name = 'OutputEthtool.Base'

  """
  test_result
  """

  def proc_test_result(
          self,
          entry
      ):
      if "test_status" in entry:
          self.status = entry["test_status"]
      self.amend_test_result(
          entry
      )
      
  def amend_test_result(
          self,
          entry
      ):
      return True

