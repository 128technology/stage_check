##########################################################################################
#   ___        _               _   ____                 _           _     _ _ _ _         
#  / _ \ _   _| |_ _ __  _   _| |_|  _ \ ___  __ _  ___| |__   __ _| |__ (_) (_) |_ _   _ 
# | | | | | | | __| '_ \| | | | __| |_) / _ \/ _` |/ __| '_ \ / _` | '_ \| | | | __| | | |
# | |_| | |_| | |_| |_) | |_| | |_|  _ <  __/ (_| | (__| | | | (_| | |_) | | | | |_| |_| |
#  \___/ \__,_|\__| .__/ \__,_|\__|_| \_\___|\__,_|\___|_| |_|\__,_|_.__/|_|_|_|\__|\__, |
#                |_|                                                                |___/ 
#  _____                    ____                   _____         _                 
# |  ___| __ ___  _ __ ___ |  _ \ ___  ___ _ __ __|_   _|____  _| |_   _ __  _   _ 
# | |_ | '__/ _ \| '_ ` _ \| |_) / _ \/ _ \ '__/ __|| |/ _ \ \/ / __| | '_ \| | | |
# |  _|| | | (_) | | | | | |  __/  __/  __/ |  \__ \| |  __/>  <| |_ _| |_) | |_| |
# |_|  |_|  \___/|_| |_| |_|_|   \___|\___|_|  |___/|_|\___/_/\_\\__(_) .__/ \__, |
#                                                                     |_|    |___/ 
##########################################################################################

import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputReachabilityFromPeers
except ImportError:
    import OutputReachabilityFromPeers


def create_instance():
    return OutputReachabilityFromPeersText()

class OutputReachabilityFromPeersText(OutputReachabilityFromPeers.Base, Output.Text):
  def __init__(self):
      super().__init__()
      self.paths_by_key = {}      
      self.truncate_message = None

  def amend_no_peers(
          self
      ):
      """
      Override in derived classes if required
      """
      self.message_list.append("No peer routers found!")
      return True

  def amend_path_result(
          self, 
          result,
          path,
          params
      ):
      """
      Override in derived classes if required
      """
      display_max_paths = 0
      if "display_max_paths" in params and \
         params["display_max_paths"] > 0:
          display_max_paths = params["display_max_paths"]
      key = None
      if params["peer_header"] is not None:
          key = Output.populate_format(path, params["peer_header"])
          msg = self.entry_result_to_string(path)
          if msg is not None:
              if display_max_paths > 0:
                  if len(self.paths_by_key) < display_max_paths:
                      if not key in self.paths_by_key:
                          self.paths_by_key[key] = [ key ]
                      self.paths_by_key[key].append(msg)
                  elif self.truncate_message is None:
                      self.truncate_message = f"Output truncated at {display_max_paths} entries"
              else:
                  if not key in self.paths_by_key:
                      self.paths_by_key[key] = [ key ]
                  self.paths_by_key[key].append(msg)
      else:
          if display_max_paths > 0:
              if len(self.message_list) < display_max_paths:
                  self.entry_result_to_text(path)
              elif self.truncate_message is None:
                  self.truncate_message = f"Output truncated at {display_max_paths} entries"
          else:
              self.entry_result_to_text(path)

      return True

  def amend_test_result(
          self, 
          path_tests,
          stats
      ):
      """
      Override in derived classes if required
      """
      if len(self.paths_by_key) > 0:
          for key in self.paths_by_key:
             self.message_list.extend(self.paths_by_key[key])
      if self.truncate_message is not None:
          self.message_list.append(self.truncate_message)
      self.test_result_to_text(path_tests, stats)
      return True


