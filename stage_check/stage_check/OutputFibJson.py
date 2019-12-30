"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputFib
except ImportError:
    import OutputFib


def create_instance():
    return OutputFibJson()


class OutputFibJson(OutputFib.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()

