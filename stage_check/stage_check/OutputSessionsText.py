"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputSessions
except ImportError:
    import OutputSessions


def create_instance():
    return OutputSessionsText()

class OutputSessionsText(OutputSessions.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_test_result(
          self, 
          matching_flows,
          stats,
          params
      ):

      # Output info for each session flow of interest
      for session_id in matching_flows:
          flow = matching_flows[session_id]
          if isinstance(flow, dict):
             if "test_exception" in flow and \
                 flow["test_exception"] is not None:
                  if not flow["test_exception"] in self.message_list:
                      self.message_list.append(flow["test_exception"])
             elif "test_format" in flow:
                  msg = Output.populate_format(flow, flow["test_format"])
                  self.message_list.append(msg)
          else:
              msg = f"Bad flowtype {flow.__class__.__name__} for session {session_id}"
              self.message_list.append(msg) 

      # TODO
      stats["idle_threshold_seconds"] = params["idle_threshold_seconds"]
      stats["filter_string"]          = params["filter_string"]

      if self.status == Output.Status.OK:
          try:
              sformat = params["entry_tests"]["result"]["PASS"]
          except KeyError:
              sformat = "Missing output format"
      else:
          try:
              sformat = params["entry_tests"]["result"]["FAIL"]
          except KeyError:
              sformat = "Missing output format"

      self.message = Output.populate_format(stats, sformat)
      return True


