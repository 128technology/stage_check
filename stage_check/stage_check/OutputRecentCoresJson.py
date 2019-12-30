"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputRecentCores
except ImportError:
    import OutputRecentCores


def create_instance():
    return OutputRecentCoresJson()


class OutputRecentCoresJson(OutputRecentCores.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()

