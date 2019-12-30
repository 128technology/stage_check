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
      self.message = 'All required network devices In Service'

  def amend_test_match(self, entry):
      """
      @status
      @entry
      """
      return self.entry_result_to_text(entry)

  def amend_test_fail_result(self, count):
      """
      @count
      """
      self.message = f"{count} required network devices are not LINK UP"
      self.message_list.append("Use PCLI 'show device-interfaces' for more information")
      return True

  def amend_test_warn_result(self, count):
      """
      @count
      """
      self.message = f"Incorrect state for {count} device interfaces"
      self.message_list.append("Use PCLI 'show device-interfaces' for more information")
      return True


