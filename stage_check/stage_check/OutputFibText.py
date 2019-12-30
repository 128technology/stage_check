"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputFib
except ImportError:
    import OutputFib


def create_instance():
    return OutputFibText()


class OutputFibText(OutputFib.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_too_few_entries(
          self, 
          params, 
          stats
      ):
      self.message = f"FIB size = {entry['total_count']} < {minimum_threshold}"
      return True

  def amend_too_many_entries(
          self, 
          params, 
          stats
      ):
      self.message = f"FIB size = {entry['total_count']} > {maximum_threshold}"
      sel.message_list.append(f"Node {entry['node_name']} FIB size = {entry['totalCount']}")
      return True

  def amend_test_match(
          self, 
          entry
      ):
      return self.entry_result_to_text(entry)
      
  def amend_test_result(
          self,
          params, 
          stats
      ):
      if "fail_count" in stats:
          self.message = f"{stats['fail_count']} / {stats['total_count']} FIB entries FAIL ({stats['exclude_count']} excluded)"
      else:                   
          self.message = f"{stats['total_count'] - stats['exclude_count']} FIB entries PASS ({stats['exclude_count']} excluded)"
      return True


  
