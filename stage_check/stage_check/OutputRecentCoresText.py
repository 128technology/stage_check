###############################################################################
#
###############################################################################

import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputRecentCores
except ImportError:
    import OutputRecentCores


def create_instance():
    return OutputRecentCoresText()


class OutputRecentCoresText(OutputRecentCores.Base, Output.Text):
  """
  """
  def __init__(self):
      super().__init__()

  def amend_uptime_match(
          self,
          cores
      ):
      exec_counts = {}
      for core in cores:
         exec_name = core["EXE"]
         exec_name = exec_name.split('/')[-1]
         try:
             exec_counts[exec_name] += 1
         except KeyError:
             exec_counts[exec_name] = 1
      for exec_name in exec_counts:
          self.message_list.append(f"{exec_counts[exec_name]} {exec_name} crashes since OS boot")
      return True

  def amend_service_match(
          self,
          service,
          cores
      ):
      exec_counts = {}
      for core in cores:
         exec_name = core["EXE"]
         exec_name = exec_name.split('/')[-1]
         try:
             exec_counts[exec_name] += 1
         except KeyError:
             exec_counts[exec_name] = 1
      for exec_name in exec_counts:
          self.message_list.append(f"{exec_counts[exec_name]} {exec_name} crashes since {service} start")
      return True

  def amend_test_result(
          self,
          message
      ):
      self.message = message
      


  
