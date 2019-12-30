"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputDeviceState
except ImportError:
    import OutputDeviceState


def create_instance():
    return OutputDeviceStateText()

class OutputDeviceStateText(OutputDeviceState.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_dev_result(self, status, entry):
      """
      @status
      @entry
      """
      return self.entry_result_to_text(entry)

  def amend_test_result(
          self, 
          entry_tests,
          stats
      ):
      return self.test_result_to_text(entry_tests, stats)




