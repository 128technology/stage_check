"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputLinuxServices
except ImportError:
    import OutputLinuxServices


def create_instance():
    return OutputLinuxServicesText()


class OutputLinuxServicesText(OutputLinuxServices.Base, Output.Text):
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
      return True      

  def amend_test_result(
          self,
          entry_tests,
          stats) :
      return self.test_result_to_text(entry_tests, stats)

  
