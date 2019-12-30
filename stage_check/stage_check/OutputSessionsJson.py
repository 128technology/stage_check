"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputSessions
except ImportError:
    import OutputSessions


def create_instance():
    return OutputSessionsJson()

class OutputSessionsJson(OutputSessions.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()


