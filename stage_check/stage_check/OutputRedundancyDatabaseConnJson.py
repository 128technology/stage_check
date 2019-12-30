"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputRedundancyDatabaseConn
except ImportError:
    import OutputRedundancyDatabaseConn


def create_instance():
    return OutputRedundancyDatabaseConnJson()

class OutputRedundancyDatabaseConnJson(OutputRedundancyDatabaseConn.Base, Output.Json):
  """
  """
  def __init__(self):
      super().__init__()
