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
      self.__full_name = "OutputBGPSummary.Base"

  """
  inactive_routing_manager
  """

  def proc_inactive_routing_manager(self,
                                   local_info,
                                   router_context):
      """
      @local_info
      @router_context
      """
      self.status = Output.Status.WARN
      self.amend_inactive_routing_manager(
          local_info,
          router_context
      )
      return self.status

  def amend_inactive_routing_manager(self,
                                     local_info,
                                     router_context):
      """
      Derived classes should override this method (if required)

      @local_info
      @router_context
      """
      return True


  """
  run_linux_error
  """
  def proc_run_linux_error(self,
                          return_status,
                          error_string):
      """
      @return_status
      @error_string
      """
      self.status  = Output.Status.FAIL
      self.amend_run_linux_error(
          return_status,
          error_string
      )
      return self.status

  def amend_run_linux_error(self,
                          return_status,
                          error_string):
      """
      Derived classes should override this method (if required)

      @return_status
      @error_string
      """
      return True

  """
  too few peers
  """

  def proc_too_few_peers(
          self,
          stats, 
          params
  ):
      self.status = Output.Status.FAIL
      self.amend_too_few_peers(
          stats,
          params
      )
      return self.status

  def amend_too_few_peers(
          self,
          stats, 
          params
  ):
      return True
      

  """
  Entry result 
  """

  def proc_entry_result(
          self, 
          entry
      ) :
      """
      *entry* - Matching entry
      """
      self.amend_entry_result(
          entry
      )
      return self.status

  def amend_entry_result(
           self, 
           entry
      ) :
      """
      Derived classes should override this method (if required)

      *entry* - Matching entry
      """
      return True

  def proc_test_result(self,
                     active_node_id, 
                     entry_tests,
                     stats,
                     status=None):
      """
      *active_node_id*
      *params*
      *stats*
      *status*
      """
      self.amend_test_result(
          active_node_id, 
          entry_tests, 
          stats
      )
      if status is not None:
          self.status = status
      return self.status


  def amend_test_result(self, 
                        active_node_id, 
                        entry_tests,
                        stats):
      """
      Derived classes should override this method (if required)

      @active_node_id
      @params,
      @stats
      """
      return True
