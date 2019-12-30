"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputServiceConfig
except ImportError:
    import OutputServiceConfig


def create_instance():
    return OutputServiceConfigJson()

class OutputServiceConfigJson(OutputServiceConfig.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()


