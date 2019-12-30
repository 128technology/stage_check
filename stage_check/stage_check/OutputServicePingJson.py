"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputServicePing
except ImportError:
    import OutputServicePing


def create_instance():
    return OutputServicePingJson()


class OutputServicePingJson(OutputServicePing.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()


