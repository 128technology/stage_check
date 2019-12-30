###############################################################################
#   ____             __ _ _                
#  |  _ \ _ __ ___  / _(_) | ___  ___      
#  | |_) | '__/ _ \| |_| | |/ _ \/ __|     
#  |  __/| | | (_) |  _| | |  __/\__ \     
#  |_|   |_|  \___/|_| |_|_|\___||___/____ 
#                                    |_____|
#   ____           _   _                _                             
#  |  _ \ ___  ___| |_| |    ___   ___ | | ___   _ _ __   _ __  _   _ 
#  | |_) / _ \/ __| __| |   / _ \ / _ \| |/ / | | | '_ \ | '_ \| | | |
#  |  _ <  __/\__ \ |_| |__| (_) | (_) |   <| |_| | |_) || |_) | |_| |
#  |_| \_\___||___/\__|_____\___/ \___/|_|\_\\__,_| .__(_) .__/ \__, |
#                                                 |_|    |_|    |___/ 
#
#  This profile manager uses a simple mape of key to test profile name
#  
###############################################################################

import os
import json
import jsonschema
import requests
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

    MASTER_DB_BY_STORE_URL = 'http://localhost:3000/api?storeNumber={}'
    req = requests.get(MASTER_DB_BY_STORE_URL.format(store_number))
    store_data = req.json() (edited) 
    """
    KEY_REPLY_WILDCARD = "*"
    KEY_REPLY_MAP = "Map"
    KEY_REPLY_PROFILE_FIELDS = "ProfileKeys"
    KEY_REPLY_ENTRY = "EntryKey"
    KEY_REST_URL = "URL"
    KEY_REST_URLS = "URLs"
    KEY_DEFAULT_ON_URL_FAILS = "DefaultOnURLFailure"
    KEY_REST_VARIABLE = "URLSiteVariable"
    MAP_FILE_NAME  = "rest_map"
    MAP_FILE_SCHEMA = """
    {
        "$schema": "http://json-schema.org/draft-06/schema#",
        "id": "https://128technology.com/schemas/stage_check/rest_map.json#",
        "title": "REST Profile Map Schema",
        "description": "REST Lookups determine profile to use",
        "type" : "object",
        "properties" : {
            "URL" : { "type" : "string" },
            "URLs" : {
                "type" : "array",
                "items" : {
                    "type" : "string"
                }
            },
            "URLSiteVariable" : { "type" : "string" },
            "EntryKey" : { "type" : "string" },
            "ProfileKeys"    : { 
                "type" : "array",
                "items" : {
                     "type" : "string"
                 }
            },
            "Map" : {
                "type" : "object",
                "patternProperties" : {
                   "^[a-zA-Z0-9_-]+" :  { "type" : "string" } 
               }
            }
        },
        "required" : [ "Map", "ProfileKeys" ],
        "oneOf" : [
            { "required" : [ "URL" ] },
            { "required" : [ "URLs" ] }
        ]
    }
    """    

    def __init__(self, paths, args):
        super().__init__(paths, args)
        self.__rest_info = { }
        
        self.__name = "RestLookup"
        self._load_map()

        self.__debug = True

    def _find_entry(self, key_string, data):
        """
        KeyError or IndexError is raised if the entry is not found 
        """
        entry = data
        key_parts = key_string.split('.')
        for part in key_parts:
            entry = entry[part]
        return entry

    def _load_map(self):
        map_schema = json.loads(self.MAP_FILE_SCHEMA)
        map_path = os.path.join(self.paths.base_path, self.MAP_FILE_NAME + ".json")
        if self.debug:
             print(f"Profiles_{self.name}._load_map: loading {map_path}")
        with open(map_path, "r") as fp:
            rest_info = json.load(fp)
        if self.debug:
             print(f"Profiles_{self.name}._load_map: validate {map_path}")
        jsonschema.validate(rest_info, map_schema)
        if self.debug:
            print(f"Profiles_{self.name}._load_map: validated {map_path}")
        self.__rest_info = rest_info

    def _bail_on_url_failures(self):
        return (not self.KEY_DEFAULT_ON_URL_FAILS in self.__rest_info or \
                not self.__rest_info[self.KEY_DEFAULT_ON_URL_FAILS] or \
                not self.KEY_REPLY_MAP in self.__rest_info or \
                not self.KEY_REPLY_WILDCARD in self.__rest_info[self.KEY_REPLY_MAP])

    def _router_to_profile_name(self, router_context):
        """
        """
        url_list = []
        sn = router_context.get_site_id()
        if self.debug:
            print(f"{self.__class__.__name__}: site number = {sn}")
        if sn is None:
            # Unable to extract site number from router name...
            if self.debug:
                print(f"{self.__class__.__name__}: Unable to extract site number for router {router_context.get_router()}")
            return None
        if self.debug:
            print(f"{self.__class__.__name__}: site number for router {router_context.get_router()} is {sn}")

        try:
            url_list.append(self.__rest_info[self.KEY_REST_URL])
        except KeyError:
            if self.debug:
                print(f"{self.__class__.__name__}: Missing rest_info key {self.KEY_REST_URL}; check urls key")
            pass
        try:
            for url in self.__rest_info[self.KEY_REST_URLS]:
               url_list.append(url)
        except KeyError:
            if self.debug:
                print(f"{self.__class__.__name__}: Missing rest_info key {self.KEY_REST_URLS}")
            pass

        success = False
        for url in url_list:
            full_url = router_context.populate_items(url)
            if self.debug:
                print(f"{self.__class__.__name__}: Trying URL {full_url}")

            try:
                reply = requests.get(full_url, verify=False);
            except Exception as e:
                # REST exception of some sort
                if self._bail_on_url_failures():
                    print(f"{self.__class__.__name__}: {e.__class__.__name__} - {full_url}")
                continue
            
            if reply.status_code != 200:
                # Bad status
                if self._bail_on_url_failures():
                    print(f"{self.__class__.__name__}: REST API ERROR {reply.status_code} - {full_url}")
                continue

            try:
                reply_json = reply.json()
            except json.decoder.JSONDecodeError:
                if self._bail_on_url_failures():
                    print(f"{self.__class__.__name__}: JSON Parse ERROR - {full_url}")
                continue

            if self.debug:
                print(f"--------- {self.__class__.__name__} REST REPLY -----------")
                pprint.pformat(reply_json)
            success = True
            break

        if not success:
            if self._bail_on_url_failures():
                print(f"{self.__class__.__name__}: Tried all URLs and failed...")
                return None
            else:
                if self.KEY_REPLY_MAP in self.__rest_info and \
                   self.KEY_REPLY_WILDCARD in self.__rest_info[self.KEY_REPLY_MAP]:
                    return self.__rest_info[self.KEY_REPLY_MAP][self.KEY_REPLY_WILDCARD]
                print(f"{self.__class__.__name__}: No default mapping...")
                return None

        try:
            entry = self._find_entry(self.__rest_info[self.KEY_REST_URL], reply_json)
        except KeyError:
            entry = reply_json

        if entry is None:
            if self.KEY_REPLY_ENTRY in self.__rest_info:
                print(f"{self.__class__.__name__}: Unable to extract entry @ {self.KEY_REPLY_ENTRY}={self.__rest_info[self.KEY_REPLY_ENTRY]}")
            else:
                print(f"{self.__class__.__name__}: Unable to extract entry @ {self.KEY_REPLY_ENTRY} is UNDEFINED")
            return None

        remote_profile_token = None
        for key in self.__rest_info[self.KEY_REPLY_PROFILE_FIELDS]:
            try:
                remote_profile_part = self._find_entry(key, entry)
            except KeyError:
                assert False, f"No key {key} in {self.__rest_info}!"
                print(f"{self.__class__.__name__}: Unable to find key={key} in entry")
                return None                                    
            if remote_profile_token is None:
                remote_profile_token = remote_profile_part
            else:
                remote_profile_token = remote_profile_token + "_" + remote_profile_part

        if remote_profile_token is None:
            print(f"{self.__class__.__name__}: Unable to extract remote profile name")
            return None
    
        profile = None
        profile_name = None
        try:
           profile_name = self.__rest_info[self.KEY_REPLY_MAP][remote_profile_token]
        except KeyError:
            if self.debug:
                print(f"{self.__class__.__name__}: no profile name for {router_context.get_router()}")
                print(f"{self.__class__.__name__}: Look for wildcard: {self.KEY_REPLY_WILDCARD}")
            profile_name = remote_profile_token

        return profile_name
