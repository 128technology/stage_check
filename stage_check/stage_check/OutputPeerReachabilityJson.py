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
    return OutputPeerReachabilityJson()

class OutputPeerReachabilityJson(OutputPeerReachability.Base, Output.Json):
  def __init__(self):
      super().__init__()



