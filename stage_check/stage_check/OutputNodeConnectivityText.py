"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputNodeConectivity
except ImportError:
    import OutputNodeConnectivity


def create_instance():
    return OutputNodeConnectivityText()


class OutputNodeConnectivityText(OutputNodeConnectivity.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_empty_reply(self, status=None):
      self.message_list.append(f"Empty connectivity reply entry...")
      return True

  def amend_node_status_mismatch(self, entry):
       self.message_list.append(f"Node {entry['node_name']}: {entry['remoteNodeName']} is {entry['status']}")
       return True

  def amend_test_result_too_few(self, entry_count, fail_count, params):
       expected_entries = params["expected_entries"]
       self.message = f'{entry_count} / {expected_entries} expected connections present'
       return True

  def amend_test_result_wrong_state(self, fail_count, expected_entries, params):
      # This is a hack, but its better than what was there before...
      values={}
      for entry in params["exclude_tests"]:
         for key in entry:
             if not key in values:
                 values[key]=[]
             if not entry[key] in values[key]:
                 values[key].append(entry[key])
      output_text=''
      list_as_string=''
      for key in values:
          list_as_string = key + "=" + ",".join(values[key])
          if output_text == '':
              output_text = list_as_string
          else:
              output_text = output_text + " " + list_as_string
      self.message = f'{fail_count} / {expected_entries} connections are not {output_text}'
      return True

  def amend_test_result_all_ok(self, entry_count, expected_entries, params):
      self.message = f'{entry_count} / {expected_entries} connections OK'
      return True

  def amend_test_result_bad_query(self, query_status):
      self.message = f'Invalid Query (status={query_status})'
      return True
