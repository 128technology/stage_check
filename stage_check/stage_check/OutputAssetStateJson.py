"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputAssetState
except ImportError:
    import OutputAssetState


def create_instance():
    return OutputAssetStateJson()


class OutputAssetStateJson(OutputAssetState.Base, Output.Json):
  """
  No changes to the Output.Json class required at this time
  """
  def __init__(self):
      super().__init__()
