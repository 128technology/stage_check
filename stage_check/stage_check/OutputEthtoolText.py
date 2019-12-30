###############################################################################
#   ___        _               _   _____ _   _     _              _ _____
#  / _ \ _   _| |_ _ __  _   _| |_| ____| |_| |__ | |_ ___   ___ | |_   _|__
# | | | | | | | __| '_ \| | | | __|  _| | __| '_ \| __/ _ \ / _ \| | | |/ _ \
# | |_| | |_| | |_| |_) | |_| | |_| |___| |_| | | | || (_) | (_) | | | |  __/
#  \___/ \__,_|\__| .__/ \__,_|\__|_____|\__|_| |_|\__\___/ \___/|_| |_|\___|
#                 |_|
###############################################################################

import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputEthtool
except ImportError:
    import OutputEthtool


def create_instance():
    return OutputEthtoolText()


class OutputEthtoolText(OutputEthtool.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_test_result(
          self,
          entry
      ):
      message = "No message format found..."
      if "test_exception" in entry and \
          entry["test_exception"] is not None:
          message = entry["test_exception"]
      elif "test_format" in entry: 
          message = Output.populate_format(entry, entry["test_format"])
      self.message = message
      return True


  
