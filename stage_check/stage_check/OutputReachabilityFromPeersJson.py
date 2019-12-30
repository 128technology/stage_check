##########################################################################################
#   ___        _               _   ____                 _           _     _ _ _ _         
#  / _ \ _   _| |_ _ __  _   _| |_|  _ \ ___  __ _  ___| |__   __ _| |__ (_) (_) |_ _   _ 
# | | | | | | | __| '_ \| | | | __| |_) / _ \/ _` |/ __| '_ \ / _` | '_ \| | | | __| | | |
# | |_| | |_| | |_| |_) | |_| | |_|  _ <  __/ (_| | (__| | | | (_| | |_) | | | | |_| |_| |
#  \___/ \__,_|\__| .__/ \__,_|\__|_| \_\___|\__,_|\___|_| |_|\__,_|_.__/|_|_|_|\__|\__, |
#                 |_|                                                               |___/ 
#  _____                    ____                        _                               
# |  ___| __ ___  _ __ ___ |  _ \ ___  ___ _ __ ___    | |___  ___  _ __    _ __  _   _ 
# | |_ | '__/ _ \| '_ ` _ \| |_) / _ \/ _ \ '__/ __|_  | / __|/ _ \| '_ \  | '_ \| | | |
# |  _|| | | (_) | | | | | |  __/  __/  __/ |  \__ \ |_| \__ \ (_) | | | |_| |_) | |_| |
# |_|  |_|  \___/|_| |_| |_|_|   \___|\___|_|  |___/\___/|___/\___/|_| |_(_) .__/ \__, |
#                                                                          |_|    |___/ 
##########################################################################################
try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputReachabilityFromPeers
except ImportError:
    import OutputReachabilityFromPeers


def create_instance():
    return OutputReachabilityFromPeersJson()

class OutputReachabilityFromPeersJson(OutputReachabilityFromPeers.Base, Output.Json):
  def __init__(self):
      super().__init__()

  def amend_no_peers(
          self
      ):
      """
      Override in derived classes if required
      """
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
      return True

  def amend_test_result(
          self, 
          path_tests,
          stats
      ):
      """
      Override in derived classes if required
      """
      return True

