"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputT1Detail
except ImportError:
    import OutputT1Detail


def create_instance():
    return OutputT1DetailText()


class OutputT1DetailText(OutputT1Detail.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_test_result(
          self, 
          results, 
          params, 
          command
      ):
      """
      """
      if len(results) > 0:
           self.status = Output.Status.FAIL
           self.message = f"{len(results)} exceptions detected for {params['linux_device']}"
           for text in results:
               self.message_list.append(text)
           self.message_list.append(f"For more info: {command}")
      else:
           self.message = f"Interface {params['linux_device']} within parameters"
           self.status = Output.Status.OK
      return self.status


