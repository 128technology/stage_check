"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputLogs
except ImportError:
    import OutputLogs


def create_instance():
    return OutputLogsText()


class OutputLogsText(OutputLogs.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_pattern_matched(
          self,
          params, 
          pattern
      ):
      format_str = "Missing format string..." 
      try:
          index = int(pattern["pindex"])
      except (KeyError, ValueError) as e:
          self.message_list.append(f"No pattern index available!")
          return True 
      try:           
          patterns = params["patterns"]
      except KeyError:
          self.message_list.append(f"Pattern List missing from config.json")
          return True
      try:      
          config = patterns[index]
      except IndexError:
          self.message_list.append(f"No config for pattern index={index}!")
          return True            
      try:
          format_str = config["format"]
      except KeyError:
          pass
      output_str = Output.populate_format(pattern, format_str);
      self.message_list.append(output_str)
      return True

  def amend_test_result(
          self, 
          params,
          stats
      ):
      """
      """
      format_str="Missing format..."
      if self.status == Output.Status.FAIL:
          try:
              format_str = params["result"]["FAIL"]
          except KeyError:
              pass
      else:
          try:
              format_str = params["result"]["PASS"]
          except KeyError:
              pass
      stats["past_hours"] = params["past_hours"]
      self.message = Output.populate_format(stats, format_str)
      return self.status


