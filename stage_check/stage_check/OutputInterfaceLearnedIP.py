"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output


class Base(Output.Base):
  """
  """
  def __init__(self):
      super().__init__()
      self.__full_name = "OutputInterfaceLearnedIP.Base"
      self.status = Output.Status.OK

  """
  empty_address
  """

  def proc_empty_address(self, entry):
      """
      @entry
      """
      self.status = Output.Status.FAIL
      self.amend_empty_address(entry)
      return self.status

  def amend_empty_address(self, entry):
      """
      @entry
      """
      return True

  """
  address_type
  """

  def proc_address_type(self, status, entry, address, iptype):
      """
      @entry
      @address
      @iptype
      """
      if status is not None:
          self.status = status
      self.amend_address_type(entry, address, iptype)
      return self.status

  def amend_address_type(self, entry, address, iptype):
      """
      @entry
      @address
      @iptype
      """
      return True

  """
  address_missing
  """

  def proc_address_missing(self, status, entry):
      """
      @entry
      """
      if status is not None:
          self.status = Output.Status.FAIL
      self.amend_address_missing(entry)
      return self.status

  def amend_address_missing(self, entry):
      """
      @entry
      """
      return True

  """
  no_interfaces_found
  """

  def proc_no_interfaces_found(self, include_list):
      """
      @include_list
      """
      self.status = Output.Status.FAIL
      self.amend_no_interfaces_found(include_list)
      return self.status

  def amend_no_interfaces_found(self, include_list):
      """
      @include_list
      """
      return True

  """
  test_result
  """

  def proc_test_result(self, status, address_list, not_excluded_count):
      """
      @address_list
      @not_excluded_count
      """
      # TODO: This logic is hackish and needs to be fixed to be
      #       more generic...
      self.amend_test_result(
          address_list, 
          not_excluded_count
      )
      if status is not None:
          self.status = status
      return self.status

  def amend_test_result(self, address_list, not_excluded_count):
      """
      @address_list
      @not_excluded_count
      """
      return True

