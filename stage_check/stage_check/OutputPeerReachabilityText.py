"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputPeerReachability
except ImportError:
    import OutputPeerReachability


def create_instance():
    return OutputPeerReachabilityText()

class OutputPeerReachabilityText(OutputPeerReachability.Base, Output.Text):
  def __init__(self):
      super().__init__()

  def amend_failed_peer(
          self, 
          path,
          peer_name
      ):
      self.message_list.append(f"Peer {peer_name}:")
      return True

  def amend_failed_path(
          self,
          path
      ):
      return self.entry_result_to_text(path)

  def amend_test_result(
          self, 
          entry_tests,
          stats
      ):
      return self.test_result_to_text(entry_tests, stats)


