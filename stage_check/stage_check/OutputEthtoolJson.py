"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputEthtool
except ImportError:
    import OutputEthtool


def create_instance():
    return OutputEthtoolJson()


class OutputEthtoolJson(OutputEthtool.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()

