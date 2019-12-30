"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputLinuxServices
except ImportError:
    import OutputLinuxServices


def create_instance():
    return OutputLinuxServicesJson()

class OutputLinuxServicesJson(OutputLinuxServices.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()


