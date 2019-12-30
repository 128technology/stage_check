"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputDeviceState
except ImportError:
    import OutputDeviceState


def create_instance():
    return OutputDeviceStateJson()

class OutputDeviceStateJson(OutputDeviceState.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()


