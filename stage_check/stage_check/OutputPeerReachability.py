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
      self.__full_name = "OutputPeerReachability.Base"

  """
  matching (unreachable) peer 
  """

  def proc_failed_peer(
          self,
          path, 
          peer_name
      ):
      self.amend_failed_peer(path, peer_name)
      return self.status

  def amend_failed_peer(
          self,
          path,
          peer_name
      ):
      """
      Override in derived classes if required
      """
      return True

  """
  matching (unreachable) path
  """

  def proc_failed_path(
          self, 
          path
      ):
      self.amend_failed_path(
          path
      )
      return self.status
      

  def amend_failed_path(
          self, 
          path
      ):
      """
      Override in derived classes if required
      """
      return True

  """
  test_result_ok
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
