###############################################################################
#   ___        _               _   ____                 _           _     _ _ _ _         
#  / _ \ _   _| |_ _ __  _   _| |_|  _ \ ___  __ _  ___| |__   __ _| |__ (_) (_) |_ _   _ 
# | | | | | | | __| '_ \| | | | __| |_) / _ \/ _` |/ __| '_ \ / _` | '_ \| | | | __| | | |
# | |_| | |_| | |_| |_) | |_| | |_|  _ <  __/ (_| | (__| | | | (_| | |_) | | | | |_| |_| |
#  \___/ \__,_|\__| .__/ \__,_|\__|_| \_\___|\__,_|\___|_| |_|\__,_|_.__/|_|_|_|\__|\__, |
#                 |_|                                                               |___/ 
#  _____                    ____                                  
# |  ___| __ ___  _ __ ___ |  _ \ ___  ___ _ __ ___   _ __  _   _ 
# | |_ | '__/ _ \| '_ ` _ \| |_) / _ \/ _ \ '__/ __| | '_ \| | | |
# |  _|| | | (_) | | | | | |  __/  __/  __/ |  \__ \_| |_) | |_| |
# |_|  |_|  \___/|_| |_| |_|_|   \___|\___|_|  |___(_) .__/ \__, |
#                                                    |_|    |___/ 
#
# OutputPeerReachability Base Class.
#
# This should only be inherited from.  Attempts to use this class
# directly, or failure to overload the Base class will result in 
# an Output.MissingOverload exception
#
###############################################################################

try:
    from stage_check import Output
except ImportError:
    import Output


class Base(Output.Base):
  def __init__(self):
      super().__init__()
      self.__full_name = "OutputReachabilityFromPeers.Base"

  def proc_no_peers(
          self
      ):
      """
      test remote peer path to this router
      """
      self.amend_no_peers(
      )
      return self.status
      

  def amend_no_peers(
          self
      ):
      """
      Override in derived classes if required
      """
      return True

  def proc_path_result(
          self, 
          result,
          path,
          params
      ):
      """
      test remote peer path to this router
      """
      self.amend_path_result(
          result,
          path,
          params
      )
      return self.status
      

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

  def proc_test_result(
          self,
          path_tests,
          stats
      ):
      """
      test_result_ok
      """
      self.amend_test_result(
          path_tests,
          stats
      )
      return self.status

  def amend_test_result(
          self, 
          path_tests,
          stats
      ):
      """
      Override in derived classes if required
      """
      return True
