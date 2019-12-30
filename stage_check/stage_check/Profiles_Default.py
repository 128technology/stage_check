###############################################################################
#   ____             __ _ _                
#  |  _ \ _ __ ___  / _(_) | ___  ___      
#  | |_) | '__/ _ \| |_| | |/ _ \/ __|     
#  |  __/| | | (_) |  _| | |  __/\__ \     
#  |_|   |_|  \___/|_| |_|_|\___||___/____ 
#                                   |_____|
#   ____        __             _ _                 
#  |  _ \  ___ / _| __ _ _   _| | |_   _ __  _   _ 
#  | | | |/ _ \ |_ / _` | | | | | __| | '_ \| | | |
#  | |_| |  __/  _| (_| | |_| | | |_ _| |_) | |_| |
#  |____/ \___|_|  \__,_|\__,_|_|\__(_) .__/ \__, |
#                                     |_|    |___/ 
#
#  The default test profile loader uses config.json to load the same test 
#  test profile for every router...
###############################################################################
import os

try:
    from stage_check import profiles
except ImportError:
    import profiles

try:
    from stage_check import paths
except ImportError:
    import paths

try:
    from stage_check import RouterContext
except ImportError:
    import RouterContext


class Manager(profiles.Base):
    """
    Used for backwards compatibility
    """
    CONFIG_FILE_BASE = "config"

    def __init__(self, paths, args):
        super().__init__(paths, args)
        self.__name = "Default"

    def load_router(self, router_context):
        """
        router_to_profile_name() is not required to be overriden as
        load_router itself is overridden...
        """
        if not router_context.profile_name_defined():
            base_path = self.paths.base_path
            dirname = os.path.dirname(self.paths.config_file)
            if dirname != '' and \
               dirname != self.paths.base_path:
               base_path = dirname
            tests = self._get_test_profile(
                self.CONFIG_FILE_BASE, 
                search_path=base_path
            )
            router_context.set_tests("<config.json>", tests)
