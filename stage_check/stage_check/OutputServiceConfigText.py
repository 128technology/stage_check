"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputServiceConfig
except ImportError:
    import OutputServiceConfig


def create_instance():
    return OutputServiceConfigText()

class OutputServiceConfigText(OutputServiceConfig.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()
      self.message = ''

  def amend_test_match(self, entry):
      """
      @status
      @entry
      """
      return self.entry_result_to_text(entry)

  def amend_config_error(self, params, message):
      """
      @params
      @message
      """
      self.message = message
      return True

  def amend_entry_count(self, params, stats):
      """
      @params
      @stats
      """
      message = f"{stats['total_count']} entries returned; expected {params['expected_count']}"
      self.message_list.append(message)
      return True

  def amend_test_result(self, entry_tests, stats):
      """
      @count
      """
      self.test_result_to_text(entry_tests, stats)
      return True




