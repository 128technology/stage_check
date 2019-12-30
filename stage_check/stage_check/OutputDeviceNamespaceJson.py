"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output


try:
    from stage_check import OutputDeviceNamespace
except ImportError:
    import OutputDeviceNamespace


def create_instance():
    return OutputDeviceNamespaceJson()


class OutputDeviceNamespaceJson(OutputDeviceNamespace.Base, Output.Json):
  """
  No changes to the Output.Json class required at this time
  """
  def __init__(self):
      super().__init__()

