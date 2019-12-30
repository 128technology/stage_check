"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputNodeConectivity
except ImportError:
    import OutputNodeConnectivity


def create_instance():
    return OutputNodeConnectivityJson()


class OutputNodeConnectivityJson(OutputNodeConnectivity.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()

