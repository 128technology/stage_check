"""
"""
import pprint

try:
    from stage_check import OutputLteLinuxText
except ImportError:
    import OutputLteLinuxText


def create_instance():
    return OutputLteInfoText()


class OutputLteInfoText(OutputLteLinuxText.Base):
  """
  """
  def __init__(self):
      super().__init__(fullName="OutputLteInfo.Base")



