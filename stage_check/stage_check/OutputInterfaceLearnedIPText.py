"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputInterfaceLearnedIP
except ImportError:
    import OutputInterfaceLearnedIP


def create_instance():
    return OutputInterfaceLearnedIPText()

class OutputInterfaceLearnedIPText(OutputInterfaceLearnedIP.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_empty_address(self, entry):
      """
      @entry
      """
      message_string = f"Node {entry['node_name']} Interface {entry['name']} has empty address"
      if self.empty_message():
          self.message = message_string
      else:
          self.message_list.append(message_string)
      return True

  def amend_address_type(self, entry, address, iptype):
      """
      @entry
      @address
      @iptype
      """
      message_string =f"Node {entry['node_name']} Interface {entry['name']}: {address} is {iptype}"
      if self.empty_message():
          self.message = message_string
      else:
          self.message_list.append(message_string)
      return True

  def amend_address_missing(self, entry):
      """
      @entry
      """
      message_string = f"Node {entry['node_name']} Interface {entry['name']}: No Address Data"
      if self.empty_message():
          self.message = message_string
      else:
          self.message_list.append(message_string)
      return True

  def amend_no_interfaces_found(self, include_list):
      """
      @include_list
      """
      if len(include_list) > 0:
          list_as_string = ",".join(include_list)
          self.message = f"No interfaces named: {list_as_string}"
      else:
          self.message = "No interfaces found"
      return True

  def amend_test_result(self, address_list, not_excluded_count):
      """
      @address_list
      @not_excluded_count
      """
      if self.status == Output.Status.OK:
          if not_excluded_count > 0:
              if self.empty_message():
                   self.message = f'Public IP(s) found: {",".join(address_list)}'
          else:
              self.message = f'No interfaces processed...'
      return True
