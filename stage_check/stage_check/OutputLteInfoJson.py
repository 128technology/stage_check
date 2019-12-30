"""
"""
import pprint

try:
    from stage_check import OutputLteLinuxJson
except ImportError:
    import OutputLteLinuxJson


def create_instance():
    return OutputLteInfoJson()


class OutputLteInfoJson(OutputLteLinuxJson.Base):
  """
  """
  def __init__(self):
      super().__init__(fullName="OutputLteInfo.Base")

