###############################################################################
#   ____             __ _ _                
#  |  _ \ _ __ ___  / _(_) | ___  ___      
#  | |_) | '__/ _ \| |_| | |/ _ \/ __|     
#  |  __/| | | (_) |  _| | |  __/\__ \     
#  |_|   |_|  \___/|_| |_|_|\___||___/____ 
#                                    |_____|
#   ____             _            __  __                          
#  |  _ \ ___  _   _| |_ ___ _ __|  \/  | __ _ _ __   _ __  _   _ 
#  | |_) / _ \| | | | __/ _ \ '__| |\/| |/ _` | '_ \ | '_ \| | | |
#  |  _ < (_) | |_| | ||  __/ |  | |  | | (_| | |_) || |_) | |_| |
#  |_| \_\___/ \__,_|\__\___|_|  |_|  |_|\__,_| .__(_) .__/ \__, |
#                                             |_|    |_|    |___/ 
#
#  This profile manager uses a simple mape of key to test profile name
#  
###############################################################################

import os
import json
import jsonschema

import pprint

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
    Manage map of router names to test profile.
    Returns a specified default if no other profiles are found.
    """
    KEY_ROUTER_WILDCARD = "*"
    KEY_ROUTER_MAP = "RouterMap"
    MAP_FILE_NAME  = "profile_map"
    MAP_FILE_SCHEMA = """
    {
        "$schema": "http://json-schema.org/draft-06/schema#",
        "id": "https://128technology.com/schemas/stage_check/loader_map.json#",
        "title": "Test Loader Map Schema",
        "description": "Refine Idle Sesssion Detection",
        "type" : "object",
        "properties" : {
            "KeyType" : { 
                "type" : "string", 
                "enum" : [
                    "router"
                ]
            },
            "RouterMap" : {
                "type" : "object",
                "patternProperties" : {
                    "^[a-zA-Z0-9_-]+" :  { "type" : "string" } 
                 }
            }
        },
        "required" : [ "KeyType", "RouterMap" ]
    }
    """

    def __init__(self, paths, args):
        super().__init__(paths, args)
        self.__profile_map = { }
        
        self.__name = "RouterMap"
        self._load_map()

        self.__debug = True

    def _load_map(self):
        map_schema = json.loads(self.MAP_FILE_SCHEMA)
        map_path = os.path.join(self.paths.base_path, self.MAP_FILE_NAME + ".json")
        if self.debug:
             print(f"Profiles_RouterMap._load_map: loading {map_path}")
        with open(map_path, "r") as fp:
            profile_map = json.load(fp)
        if self.debug:
             print(f"Profiles_RouterMap._load_map: validate {map_path}")
        jsonschema.validate(profile_map, map_schema)
        if self.debug:
            print(f"Profiles_RouterMap._load_map: validated {map_path}")
        self.__profile_map = profile_map

    def _router_to_profile_name(self, router_context):
        """
        Overidden
        """
        if self.debug:
            print(f"{self.__class__.__name__}: load tests for {router_context.get_router()}")
        try:
            key_type = self.__profile_map["KeyType"]
            if key_type == "router": 
                key = router_context.get_router()
            else:
                raise ValueError
        except KeyError:
            if self.debug:
                print(f"{self.__class__.__name__}: no KeyType specified")

        profile_name = None

        try:
           profile_name = self.__profile_map[self.KEY_ROUTER_MAP][key]
        except KeyError:
            if self.debug:
                print(f"{self.__class__.__name__}: no profile name for {router_context.get_router()}")
                print(f"{self.__class__.__name__}: Look for wildcard: {self.KEY_ROUTER_WILDCARD}")
            try:
                profile_name = self.__profile_map[self.KEY_ROUTER_MAP][self.KEY_ROUTER_WILDCARD]    
            except KeyError:
                if self.debug:
                    print(f"{self.__class__.__name__}: no wildcard for {router_context.get_router()}")

        return profile_name

