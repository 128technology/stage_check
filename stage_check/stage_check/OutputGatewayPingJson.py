"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputGatewayPing
except ImportError:
    import OutputGatewayPing


def create_instance():
    return OutputGatewayPingJson()


class OutputGatewayPingJson(OutputGatewayPing.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()


