"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputAssetState
except ImportError:
    import OutputAssetState


def create_instance():
    return OutputAssetStateText()


class OutputAssetStateText(OutputAssetState.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_interim_result(self, entry, status=None):
      try:
          message = Output.populate_format(entry, entry["test_format"])
      except KeyError:
          message = "NO FORMAT PROVIDED..."
      if status != Output.Status.OK:
          self.message_list.append(message)
          self.message_list.append(f"     text: {entry['text']}")
      return True      

  def amend_test_result(
          self,
          entry_tests,
          stats) :
      return self.test_result_to_text(entry_tests, stats)

  
