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

  def amend_metric(self, entry, entry_value):
      self.message_list.append(f"{entry['node']}: Active DB Connections = {entry_value}")
      return True

  def amend_missing_data(self):
      """
      """
      self.message_list.append('No Node Name or Active DB Connections')
      return True

  def amend_test_result(self, 
                        entry_count, 
                        test_value, 
                        fail_count, 
                        expected_entries):
      """
      @entry_count
      @test_value 
      @fail_count 
      @expected_entries
      """
      self.message = f'Active DB Connections = {test_value} on {entry_count} / {expected_entries} nodes'            
      if self.status != Output.Status.FAIL:
          self.message_list = []

      return True

  def amend_test_result_bad_values(self, 
                                   entry_count, 
                                   test_value, 
                                   fail_count, 
                                   expected_entries):
      """
      @entry_count
      @test_value 
      @fail_count 
      @expected_entries
      """
      self.message = f'Bad/missing values on {fail_count}/{entry_count} nodes'
      if self.status != Output.Status.FAIL:
          self.message_list = []

      return True

