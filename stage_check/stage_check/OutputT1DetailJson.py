"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputT1Detail
except ImportError:
    import OutputT1Detail


def create_instance():
    return OutputT1DetailJson()


class OutputT1DetailJson(OutputT1Detail.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()

