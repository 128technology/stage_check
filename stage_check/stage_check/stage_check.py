#!/usr/bin/env python36
###############################################################################
#       _                           _               _
#   ___| |_ __ _  __ _  ___     ___| |__   ___  ___| | __  _ __  _   _
#  / __| __/ _` |/ _` |/ _ \   / __| '_ \ / _ \/ __| |/ / | '_ \| | | |
#  \__ \ || (_| | (_| |  __/  | (__| | | |  __/ (__|   < _| |_) | |_| |
#  |___/\__\__,_|\__, |\___|___\___|_| |_|\___|\___|_|\_(_) .__/ \__, |
#                |___/    |_____|                         |_|    |___/
#
###############################################################################
import os
import sys
import getpass
import importlib

import time

import re

import subprocess

import pprint

import ipaddress

import shlex

import argparse

import json
import jmespath
import jsonschema

try:
    from stage_check import paths
except ImportError:
    import paths

try:
    from stage_check import init_helper
except ImportError:
    import init_helper

try:
    from stage_check import gql_helper
except ImportError:
    import gql_helper

try:
    from stage_check import Linux
except ImportError:
    import Linux

try:
    from stage_check import RouterContext
except ImportError:
    import RouterContext

try:
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import profiles
except ImportError:
    import profiles

try:
    from stage_check import _version
except ImportError:
    import _version


class TestExecutor(object):

    TEST_EXECUTOR_VERSION = _version.__version__

    # Overall test config...
    JSON_SCHEMA_FILE = "config_schema.json"
    JSON_CONFIG_FILE = "config.json"

    def __init__(self, args):
        """
        """
        self.tests                = []
        self.router_dict          = {}
        # dictionary of router lists keyed by pattern
        self.routers_by_pattern   = {}

        self.__paths = paths.Paths(args, debug=args.debug)
        if args.debug == True:
            self.paths.dump()

        self.local_info = init_helper.NodeInfo(debug=args.debug)
        """
        if self.local_info.get_node_type() == "conductor":
            self.gql_token  = gql_helper.RestToken(gql_path=self.paths.gql_path)
        else:
            self.gql_token  = None
        """
        self.gql_token = None

        gql_helper.set_local_rpm_version( self.local_info.version)

        self.exclude_list    = args.exclude
        self.primary_regex   = args.primary_regex
        self.secondary_regex = args.secondary_regex
        self._debug          = args.debug
        self.router_patterns = args.router_patterns
        self.start_after     = args.start_after

        self._stage_check_path = self.paths.runtime_path

        self.load_config(args)

        if 'HWTypeConversions' in self.config_dict:
            RouterContext.set_hw_type_regex_subs(
               self.config_dict['HWTypeConversions']
            )

        self.force_json = args.json

        output_header = True
        if "SuppressAboutText" in self.config_dict and\
           self.config_dict["SuppressAboutText"] == True:
            output_header = False
        if self.force_json:
            output_header = False
        if output_header:
            self.print_version()

        self.load_router_module()
        self.load_banner_module()
        self.load_profile_module(args)

        if args.debug:
            print(f'Local Node Info:')
            print(f'----------------')
            display_string = self.local_info.to_string()
            print(f"{display_string}")

        self.create_router_contexts(args)

        self.tests_by_status = {}

        self._warn_is_fail = args.warn_is_fail

        self.exclude_list = args.exclude

        self.output_file = args.output

        self.status_strings={}
        self.status_strings[Output.Status.OK]   = 'PASS'
        self.status_strings[Output.Status.WARN] = 'WARN'
        self.status_strings[Output.Status.FAIL] = 'FAIL'
        

    @property
    def warn_is_fail(self):
        return self._warn_is_fail

    @property
    def debug(self):
        return self._debug

    @property
    def stage_check_path(self):
        return self._stage_check_path

    @property
    def paths(self):
        return self.__paths

    def version(self):
        return self.TEST_EXECUTOR_VERSION

    def print_version(self):
        print(f'---------------------------')
        print(f'stage_check version: {self.version()}')
        print(f'---------------------------')

    def clear_counts(self):
        self.tests_by_status = {}

    def count_results(self, status):
        try:
            count = len(self.tests_by_status[status])
        except (KeyError, TypeError):
            count = 0
            pass
        return count

    def tally_results(self, test, status):
        """
        To be stored in router context?
        """
        if status not in self.tests_by_status:
            self.tests_by_status[status] = []
        self.tests_by_status[status].append(test.description())

    def tests_shell_status(self):
        shell_status = 1
        if self._warn_is_fail:
            if Output.Status.WARN in self.tests_by_status or \
               Output.Status.FAIL in self.tests_by_status:
                shell_status = 1
        else:
            if Output.Status.FAIL in self.tests_by_status:
                shell_status = 0
        return shell_status


    def get_json_assets(self):
        """
        Loads a list of json assets from the conductor
        """
        qn = gql_helper.NodeGQL("allAuthorities", [ 'assets { assetId routerName nodeName t128Version status assetIdConfigured text failedStatus }' ],
                                                      [ ], top_level=True, debug=self.debug)
        json_reply={}
        query_status = qn.send_query(self.gql_token, json_reply)
        if not query_status == 200:
            print('\n*** Unable to query conductor assets ***\n')
            sys.exit(1)

        flatter_json = qn.flatten_json(json_reply, "/allAuthorities/assets")
        #match_string=f"node.assets[*]"
        #flatter_json = jmespath.search(match_string, json_reply)

        if self.debug:
            print('........ flattened list ..........')
            pprint.pprint(flatter_json)

        self.json_assets = flatter_json
        return query_status


    def create_router_contexts(self, args):
        """
        create one or more router assets
        """
        try:
            router_context_data = self.config_dict["RouterContextData"]
        except KeyError:
            router_context_data = {}

        if "PrimaryRegex" in self.config_dict:
             args.primary_regex = self.config_dict["PrimaryRegex"]
        if "SecondaryRegex" in self.config_dict:
             args.secondary_regex = self.config_dict["SecondaryRegex"]
        if "SiteNumberRegex" in self.config_dict:
             args.site_regex = self.config_dict["SiteNumberRegex"]
        if "PodNumberRegex" in self.config_dict:
             args.pod_regex = self.config_dict["PodNumberRegex"]
        if len(self.router_patterns) > 0:
            if self.local_info.get_node_type() == 'conductor':
                self.get_json_assets()
                for asset in self.json_assets:
                    try:
                        router_name = asset['routerName']
                    except KeyError:
                        continue
                    matched_router = False
                    for pattern in self.router_patterns:
                        if args.regex_patterns:
                            if re.search(pattern, router_name):
                                matched_router = True
                                break
                        else:
                            if pattern in router_name:
                                matched_router = True
                                break
                    if matched_router:
                        op_string='Add'
                        if router_name not in self.router_dict:
                            rc = self.router_module.create_instance(
                                self.local_info, 
                                router_name, 
                                args,
                                asset, 
                                router_context_data
                            )
                            self.router_dict[router_name] = rc
                            if pattern in self.routers_by_pattern:
                                self.routers_by_pattern[pattern].append(rc)
                            else:
                                self.routers_by_pattern[pattern] = [ rc ]
                        else:
                            op_string='Update'
                            self.router_dict[router_name].set_node(asset_json=asset)
                        if args.debug or args.context:
                            print(f'{op_string} router: {router_name}')
                            rc.display()
            else:
                print('\n*** Only conductors can match router patterns! ***\n')
                sys.exit(1)

        if args.router is not None and \
           len(self.router_dict) == 0:
            rc = self.router_module.create_instance(
                self.local_info, 
                args.router, 
                args, 
                config=router_context_data
            )
            self.router_dict[rc.get_router()] = rc
            self.router_patterns = [ 'placeholder' ]
            self.routers_by_pattern['placeholder'] = [ rc ]
            if args.debug or args.context:
                print(f'Adding default Router')
                rc.display()

    def run_tests(self, router_context, router_count=0, fp=None):
        """
        """
        self.clear_counts()
        router_max = len(self.router_dict)
        test_max   = len(router_context.tests)
        for test in router_context.tests:
            if test.enabled == False:
                continue
            if len(test.hw_types) > 0 and \
               router_context.nodes_with_hw_type(test.hw_types) == 0:
                continue
            if test.check_tags(router_context.exclude_tags):
                continue
            if not test.check_tags(router_context.include_tags, True):
                continue
            if test.test_id not in self.exclude_list:
                if test.skip_single_node and \
                   router_context.skip_single_node:
                    # TODO Indicate single node somehow?
                    continue
                test.last_test_id = test_max
                test.router_index = router_count
                test.last_router_index = router_max
                status = test.run(
                    self.local_info,
                    router_context,
                    self.gql_token,
                    fp
                )
                self.tally_results(test, status)
        if fp is not None:
            if self.count_results(Output.Status.FAIL) > 0:
                self.banner.header(
                    router_context,
                    router_count,
                    router_max
                )
                for test in router_context.tests:
                    test.test_end_by_status([Output.Status.FAIL])
                self.banner.trailer(
                    router_context,
                    router_count,
                    router_max
                )
            else:
                self.banner.header_summary(router_context, self.tests_by_status)
                self.banner.trailer_summary(router_context)

        # create a new output instance to reset state...
        for test in router_context.tests:
            test.create_output_instance()

    def run_suite(self, fp=None):
        """
        Output routers matching patterns specified using the order spacified in the -R
        argument list.  Since multiple routers may match a pattern, sort RouterContexts
        matching a pattern by router name.
        """
        def getKey(item):
            """
            Return a router context key for sorting
            """
            return item.get_router()

        router_count = 1

        skip_router = False
        if self.start_after is not None:
            skip_router = True

        for key in self.router_patterns:
            if not key in self.routers_by_pattern:
                continue
            router_max = len(self.router_dict)
            for router_context in sorted(self.routers_by_pattern[key], key=getKey):
                if self.start_after is not None and \
                   self.start_after in router_context.get_router():
                    skip_router = False
                    router_count += 1
                    continue
                if skip_router == True:
                    router_count += 1
                    continue

                self.query_hw_by_version(router_context)
                router_context.query_extra_info()
                self.profile_manager.load_router(router_context)

                self.banner.header(
                    router_context,
                    router_count,
                    router_max,
                    fp)
                self.run_tests(
                    router_context,
                    router_count,
                    fp
                )
                self.banner.trailer(
                    router_context,
                    router_count,
                    router_max,
                    fp
                )

                if fp is not None:
                    fp.write('\n')
                router_count += 1

    def test_routers(self):
        """
        Output ti stdout or to an output file
        """
        if self.output_file == '':
            self.run_suite()
        else:
            with open(self.output_file, "w") as fp:
                self.run_suite(fp)

    def load_config(self, args):
        self.config_dict = {}
        self.config_schema_dict = {}

        config_path = self.paths.config_file
        with open(config_path) as config_handle:
            self.config_dict = json.load(config_handle)

        if self.debug:
            print(f"loaded {config_path}")

        schema_path = os.path.join(self.stage_check_path, self.JSON_SCHEMA_FILE)
        with open(schema_path) as schema_handle:
            self.config_schema_dict = json.load(schema_handle)

        if self.debug:
            print(f"loaded {schema_path}")

        try:
            valid = jsonschema.validate(self.config_dict, self.config_schema_dict)
        except Exception as e:
            print("******************************************")
            print("* Error Validating Config! EXITING ")
            print("******************************************")
            print(e)
            sys.exit(1)

        # print(f"validated configuration...")

    def load_router_module(self):
        """
        Loads the router context module used to create RouterContext child instances
        as asset or argument processesing drives router context creation.
        """
        self.router_module = None
        try:
            router_module_name = self.config_dict["RouterContextModule"]
            # router_module_name = self.router_module
        except KeyError:
            print("******************************************")
            print("* No RouterContextModule defined! EXITING ")
            print("******************************************")
            sys.exit(1)

        try:
            router_module = importlib.import_module(router_module_name)
        except Exception as e:
            print(f"******************************************")
            print(f"* Exception loading {router_module_name}  ")
            print(f"* {e}                                     ")
            print(f"* in: {sys.path}                          ")
            print(f"******************************************")
            print(f"Script-Path:  {os.path.dirname(os.path.realpath(__file__))}")
            print(f"Working-Path: {os.getcwd()}")
            sys.exit(1)

        if hasattr(router_module, "create_instance"):
            self.router_module = router_module
            # print(f"Successfully registered router plugin '{router_module_name}'")
        else:
            print("************************************************")
            print(f"* RouterContextModule {router_context_name}")
            print("* is missing create_instance function; EXITING ")
            print("************************************************")
            sys.exit(1)

    def load_banner_module(self):
        """
        Loads the Banner module used to create the Banner for each
        Router's test sequence
        """
        self.banner_module = None
        try:
            if self.force_json:
                banner_module_name = "BannerJson"
            else:
                banner_module_name = self.config_dict["BannerModule"]
         
        except KeyError:
            print("***********************************")
            print("* No BannerModule defined! EXITING ")
            print("***********************************")
            sys.exit(1)

        try:
            banner_module = importlib.import_module(banner_module_name)
        except Exception as e:
            print(f"******************************************")
            print(f"* Exception loading {banner_module_name}  ")
            print(f"* {e}                                     ")
            print(f"* in: {sys.path}                          ")
            print(f"******************************************")
            print(f"Script-Path:  {os.path.dirname(os.path.realpath(__file__))}")
            print(f"Working-Path: {os.getcwd()}")
            sys.exit(1)

        if hasattr(banner_module, "create_instance"):
            self.banner_module = banner_module
            # print(f"Successfully registered banner plugin '{banner_module_name}'")
        else:
            print("************************************************")
            print(f"* BannerModule {banner_context_name}")
            print("* is missing create_instance function; EXITING ")
            print("************************************************")
            sys.exit(1)

        # TODO The banner is probably more a property of the router
        self.banner = self.banner_module.create_instance()

    def load_profile_module(self, args):
        try:
            module_base = self.config_dict["ProfileModule"]
        except KeyError:
            module_base = "Default"
        module_name = "Profiles_" + module_base

        if self.debug:
            print(f"Profile base: {module_base}")

        try:
             module = importlib.import_module(module_name)
        except Exception as e:
            print(f"******************************************")
            print(f"* Exception loading {module_name}         ")
            print(f"* {e}                                     ")
            print(f"* in: {sys.path}                          ")
            print(f"******************************************")
            print(f"Script-Path:  {os.path.dirname(os.path.realpath(__file__))}")
            print(f"Working-Path: {os.getcwd()}")
            sys.exit(1)

        try:
            self.profile_manager = module.Manager(self.paths, args)
        except NameError:
            print(f"******************************************")
            print(f"* Exception loading {module_name}         ")
            print(f"* {module_name}.Manager not defined       ")
            print(f"* in: {sys.path}                          ")
            print(f"*                                         ")
            print(f"* This module has no class!!!             ")
            print(f"******************************************")
            print(f"Script-Path:  {os.path.dirname(os.path.realpath(__file__))}")
            print(f"Working-Path: {os.getcwd()}")
            sys.exit(1)
        if self.debug:
            print(f"Imported profile manager: {module_name}")

    def query_lshw_class(self, router_context, lshw_class):
        if self.debug:
            print(f'**** Query HW Type using LSHW class={lshw_class} ****')
        json_data = []
        error_lines = []
        lshw = Linux.LSHW(debug=self.debug, class_type=lshw_class)
        shell_status = lshw.run_linux_args(
           router_context,
           "all",
           lshw_class,
           error_lines,
           json_data
        )
        if self.debug:
            print('........ hardware info ..........')
            pprint.pformat(json_data)
        return json_data 

    def query_lshw_data(self, router_context):
        json_data = self.query_lshw_class(router_context, "system")
        if not router_context.set_lshw_info(json_data):
            print(f"**** Set default LSHW class failed!", flush=True)
            lshw_class = router_context.get_alt_lshw_class()
            json_data = self.query_lshw_class(router_context, lshw_class)
            router_context.set_lshw_info(json_data)
 
    def query_hw_by_version(self, router_context):
        if router_context.nodes_with_lesser_rpm_version("5.1.0") > 0:
            self.query_lshw_data(router_context)
        else:
            router_context.query_hw_info()
            if not router_context.valid_hw_type():
                if self.debug:
                    print(f"*** REST GraphQL yields invalid hw_type; trying lshw ***")
                lshw_class = router_context.get_alt_lshw_class()
                json_data = self.query_lshw_class(router_context, lshw_class)
                router_context.set_lshw_info(json_data)
