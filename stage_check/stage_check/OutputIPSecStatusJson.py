"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputIPSecStatus
except ImportError:
    import OutputIPSecStatus


def create_instance():
    return OutputIPSecStatusJson()

class OutputIPSecStatusJson(OutputIPSecStatus.Base, Output.Json):
  def __init__(self):
      super().__init__()



