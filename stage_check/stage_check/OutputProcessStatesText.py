"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputProcessStates
except ImportError:
    import OutputProcessStates

import json

def create_instance():
    return OutputProcessStatesText()


class OutputProcessStatesText(OutputProcessStates.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_interim_result(self, entry, status=None):
      message = self.entry_result_to_string(entry)
      if message is not None:
          self.message_list.append(message)
      return True      

  def amend_test_result(
          self,
          entry_tests,
          stats) :
      return self.test_result_to_text(entry_tests, stats)

  
