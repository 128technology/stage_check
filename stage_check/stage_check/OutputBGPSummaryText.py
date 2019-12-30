"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputBGPSummary
except ImportError:
    import OutputBGPSummary


def create_instance():
    return OutputBGPSummaryText()

class OutputBGPSummaryText(OutputBGPSummary.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()
      self.message = 'No Test Headline Provided'


  def amend_inactive_routing_manager(self,
                                     local_info,
                                     router_context):
      """
      @local_info
      @router_context
      """
      self.message = f'{local_info.get_node_name()} - No active RouteManager ' \
                     f'for router {router_context.get_router()}'
      return True


  def amend_run_linux_error(self,
                            return_status,
                            error_string):
      """
      @return_status
      @error_string
      """
      self.message = error_string
      return True

  def amend_too_few_peers(
          self,
          stats, 
          params
  ):
      self.message = f"Only {stats['total_count']} / {params['minimum_count']} BGP peers reported" 
      return True
  

  def amend_entry_result(self, 
                         entry
                         ):
      """
      *entry* - test + results to convert to text
      """
      return self.entry_result_to_text(entry)


  def amend_test_result(self, 
                        active_node_id, 
                        entry_tests,
                        stats):
      """
      @active_node_id
      @entry_tests
      @stats
      """
      # hackish
      stats["active_node_id"] = active_node_id
      return self.test_result_to_text(entry_tests, stats)

