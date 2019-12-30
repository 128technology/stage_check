"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputEtcHosts
except ImportError:
    import OutputEtcHosts


def create_instance():
    return OutputEtcHostsJson()


class OutputEtcHostsJson(OutputEtcHosts.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()

