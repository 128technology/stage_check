"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputBGPSummary
except ImportError:
    import OutputBGPSummary


def create_instance():
    return OutputBGPSummaryJson()

class OutputBGPSummaryJson(OutputBGPSummary.Base, Output.Json):
  """
  The base class Output.Json requires no changes...
  """
  def __init__(self):
      super().__init__()



