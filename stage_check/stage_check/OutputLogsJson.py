"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputLogs
except ImportError:
    import OutputLogs


def create_instance():
    return OutputT1DetailJson()


class OutputLogsJson(OutputT1Detail.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()

