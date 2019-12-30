#!/usr/bin/python/env python3.6
#####################################################################
#                    __ _ _
#   _ __  _ __ ___  / _(_) | ___  ___   _ __  _   _
#  | '_ \| '__/ _ \| |_| | |/ _ \/ __| | '_ \| | | |
#  | |_) | | | (_) |  _| | |  __/\__ \_| |_) | |_| |
#  | .__/|_|  \___/|_| |_|_|\___||___(_) .__/ \__, |
#  |_|                                           |_|
#
#####################################################################

import os
import sys
import importlib
import json
import jsonschema
import pprint

try:
    from stage_check import paths
except ImportError:
    import paths

class Base:
    def __init__(self, paths, args):
        self.__paths = paths
        self.__args  = args
        self.__debug = args.debug
        self.__name  = "Base"
        self.__profiles = {}
        self.__module_dict = {}
        self.__schema_dict = {}

    @property
    def debug(self):
        return self.__debug

    @property
    def name(self):
        return self.__name

    @property
    def paths(self):
        return self.__paths

    def _load_tests(self, profile_as_json, tests):
        index = 0
        tests.clear()
        for entry in profile_as_json["Tests"]:
            test_module_base = entry["TestModule"]
            test_module_name = "Test" + test_module_base
            test_schema_key = 'Schema' + test_module_base
            test_schema_file = test_schema_key + '.json'
            if test_module_name not in self.__module_dict:
                test_module = importlib.import_module(test_module_name)
                if hasattr(test_module, "create_instance"):
                    self.__module_dict[test_module_name] = test_module
                    # print(f"Successfully registered test plugin '{test_module_name}'")
                else:
                    print(f"Module '{test_module_name}' has no create_instance function; skipping")

                if test_module_name not in self.__schema_dict:
                    schema_config_path = os.path.join(self.__paths.runtime_path, test_schema_file)
                    try:
                        with open(schema_config_path) as schema_handle:
                            self.__schema_dict[test_module_name] = json.load(schema_handle)
                    except IOError:
                        print(f"******************************************")
                        print(f"* Exception reading {schema_config_path}  ")
                        print(f"* Exiting...                              ")
                        print(f"******************************************")
                        assert False, f"schema: {schema_config_path}"
                        sys.exit(1)
            json_schema = self.__schema_dict[test_module_name]
            jsonschema.validate(entry["Parameters"], json_schema)
            test_module = self.__module_dict[test_module_name]
            test = test_module.create_instance(index, entry, self.__args)
            test.create_output_instance(self.__module_dict)
            tests.append(test)
            index += 1

    def _load_profile(self, name, search_path=None):
        if search_path is None:
            basename = os.path.basename(self.paths.config_file)
            filebase = os.path.splitext(basename[0])
            if filebase == name:
                profile_path = self.paths.config_file
            else:
                profile_path = os.path.join(self.paths.profile_path, name + ".json")
        else:
            profile_path = os.path.join(search_path, name + ".json")
            if (self.debug):
                print(f"_load_profile: Profile Path {profile_path}")
        try:
            tests = []
            with open(profile_path) as fp:
                profile_as_json = json.load(fp)
            self._load_tests(profile_as_json, tests)
            self.__profiles[name] = tests
        except IOError:
            print(f"**************************************************")
            print(f"* Unable to open profile {profile_path}\n* ")
            print(f"* Exiting...")
            print(f"**************************************************")
            sys.exit(1)

    def _get_test_profile(self, profile_name, load=True, search_path=None):
        if self.debug:
            print(f"{self.name}:_get_test_profile({profile_name}, load={load}, search_path={search_path})")
        tests = None
        try:
            tests = self.__profiles[profile_name]
        except KeyError:
            if load:                            
                self._load_profile(profile_name, search_path)
                try:
                    tests = self.__profiles[profile_name]
                except KeyError:
                    pass
        return tests

    def _router_to_profile_name(self, router_context):
        """
        Must Be Overloaded, if load_router is not
        """
        raise ValueError

    def dump_profiles(self):
        pprint.pprint(self.__profiles)

    def load_router(self, router_context):
        profile_name = router_context.profile_name
        if profile_name is None or \
           profile_name == 'UNDEFINED':    
            profile_name = self._router_to_profile_name(router_context)
        if profile_name is not None and \
            len(router_context.tests) == 0:
            if self.debug:
                print(f"profiles.load_router: Load tests for {profile_name}...")
            tests = self._get_test_profile(profile_name)
            router_context.set_tests(profile_name, tests)
        else:
            if self.debug:
                print(f"profiles.load_router: Tests already loaded for router_context...")



