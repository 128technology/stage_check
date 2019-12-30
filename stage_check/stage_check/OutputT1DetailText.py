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
          all_entries, 
          matching_entries,
          params
      ):
      """
      """
      if len(matching_entries) > 0:
           exception_count = 0
           for entry in matching_entries:
               if "result_text" in entry:
                   self.message_list.extend(entry["result_text"])
               exception_count += len(entry["result_text"]) - 1
           self.status = Output.Status.FAIL
           self.message = f"{exception_count} exceptions detected for {len(matching_entries)}/{len(all_entries)} interfaces(s)"

      else:
           self.message = f"All {len(all_entries)} interfaces(s) within parameters"
           self.status = Output.Status.OK
      return self.status


