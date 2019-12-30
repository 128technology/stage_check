"""
"""
import pprint

try:
    from stage_check import OutputLteLinuxText
except ImportError:
    import OutputLteLinuxText


def create_instance():
    return OutputLteIfConfigText()


class OutputLteIfConfigText(OutputLteLinuxText.Base):
  """
  """
  def __init__(self):
      super().__init__(fullName="OutputLteIfConfig.Base")



