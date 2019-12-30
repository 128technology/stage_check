"""
"""

import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputRedundancyDatabaseConn
except ImportError:
    import OutputRedundancyDatabaseConn


def create_instance():
    return OutputRedundancyDatabaseConnText()

class OutputRedundancyDatabaseConnText(OutputRedundancyDatabaseConn.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_no_node_data(self, local_info):
      self.message = f'No data for node {local_info.get_node_name()} type {Output.Text.AnsiColors.red}{local_info.get_node_type()}'
      return True

  def amend_entry_result(self, entry_tests, entry):
      return self.entry_result_to_text(entry)

  def amend_missing_data(self):
      """
      """
      self.message_list.append('No Node Name or Active DB Connections')
      return True

  def amend_test_result(self, 
                        entry_tests, 
                        stats):
      """
      """
      return self.test_result_to_text(entry_tests, stats)

  def amend_unexpected_count(self, 
                             stats, 
                             expected_count):
      """
      """
      self.message = f"Data included {stats['tested_count']} nodes; expected {expected_count}"
      if self.status != Output.Status.FAIL:
          self.message_list = []
      return True

