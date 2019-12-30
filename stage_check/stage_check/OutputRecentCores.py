"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output


class Base(Output.Base):
  def __init__(self):
      super().__init__()
      self.__full_name = 'OutputRecentCores.Base'

  """
  test_result
  """
  def proc_uptime_match(
          self,
          cores
      ):
      self.amend_uptime_match(
          cores
      )
      
  def amend_uptime_match(
          self,
          cores
      ):
      return True

  """
  service_match
  """

  def proc_service_match(
          self,
          service,
          cores
      ):
      self.amend_service_match(
          service,
          cores
      )
      
  def amend_service_match(
          self,
          service,
          cores
      ):
      return True

  """
  test_result
  """

  def proc_test_result(
          self,
          message,
          status = None
      ):
      if status is not None:
          self.status = status
      self.amend_test_result(
          message
      )
      
  def amend_test_result(
          self,
          message
      ):
      return True


