"""
"""
import pprint

try:
    from stage_check import OutputLinuxJson
except ImportError:
    import OutputLteLinuxJson


def create_instance():
    return OutputLteIfConfigJson()


class OutputLteIfConfigJson(OutputLteLinuxJson.Base):
  """
  """
  def __init__(self):
      super().__init__(fullName="OutputLteIfConfig.Base")

