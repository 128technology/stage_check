"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputIPSecStatus
except ImportError:
    import OutputIPSecStatus


def create_instance():
    return OutputIPSecStatusText()

class OutputIPSecStatusText(OutputIPSecStatus.Base, Output.Text):
  def __init__(self):
      super().__init__()

  def amend_result(
          self, 
          path,
          entry
      ):
      return self.entry_result_to_text(entry)

  def amend_errors(
          self,
          entry
      ):
      self.message_list.extend(entry["errors"])
      return True

  def amend_test_result(
          self, 
          entry_tests,
          stats
      ):
      return self.test_result_to_text(entry_tests, stats)


