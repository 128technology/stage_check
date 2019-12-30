"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputInterfaceLearnedIP
except ImportError:
    import OutputInterfaceLearnedIP


def create_instance():
    return OutputInterfaceLearnedIPJson()

class OutputInterfaceLearnedIPJson(OutputInterfaceLearnedIP.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()
