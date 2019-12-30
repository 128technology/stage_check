"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputEtcHosts
except ImportError:
    import OutputEtcHosts


def create_instance():
    return OutputEtcHostsText()


class OutputEtcHostsText(OutputEtcHosts.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_test_result(
          self,
          all_entries,
          matching_tests,
          test_output,
          params
      ):
      """
      """
      if self.debug:
           print(f"OutputEtcHostsText::amend_test_result")
      try:
          test_count = len(params["entry_tests"]["tests"]) * len(all_entries)
      except KeyError:
          test_count = 0
      dont_count_keys = [
          "result_text",
          "test_exception",
          "test_format",
          "test_index",
          "test_matched",
          "test_status"
      ]
      if self.debug:
          print(f"+++++++++++++++++ messages_list> ++++++++++++++++")
          pprint.pprint(self.message_list)
          print(f"+++++++++++++++++ <messages_list ++++++++++++++++")
      dont_count = 0
      total_len = 0
      for entry in all_entries:
          total_len += len(entry)
          for key in dont_count_keys:
              if key in all_entries:
                  dont_count += 1
      all_count = total_len - dont_count
      matching_count = len(matching_tests)
      if matching_count > 0:
           self.message_list.extend(test_output)
           self.status = Output.Status.FAIL
           self.message = f"Missing {matching_count}/{test_count} service entries"
           #assert False, pprint.pformat(all_entries)
      else:
           self.message = f"All {test_count} service entries present"
           self.status = Output.Status.OK
      return self.status
