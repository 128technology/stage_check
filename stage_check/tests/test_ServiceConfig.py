#!/usr/bin/env python3.6
##############################################################################################
#   _            _       ____                  _          ____  _                           
#  | |_ ___  ___| |_    / ___|  ___ _ ____   _(_) ___ ___|  _ \(_)_ __   __ _   _ __  _   _ 
#  | __/ _ \/ __| __|   \___ \ / _ \ '__\ \ / / |/ __/ _ \ |_) | | '_ \ / _` | | '_ \| | | |
#  | ||  __/\__ \ |_     ___) |  __/ |   \ V /| | (_|  __/  __/| | | | | (_| |_| |_) | |_| |
#   \__\___||___/\__|___|____/ \___|_|    \_/ |_|\___\___|_|   |_|_| |_|\__, (_) .__/ \__, |
#                  |_____|                                              |___/  |_|    |___/ 
#
##############################################################################################
import os
import sys

import argparse

import re
import pprint
import json

import pytest
import mock
import pyfakefs
import requests
import responses
from pytest_mock import mocker

try:
    from stage_check import pytest_common
except ImportError:
    import pytest_common

try:
    from stage_check import Linux
except ImportError:
    import Linux

try:
    from stage_check import RouterContext
except ImportError:
    import RouterContext

try:
    from stage_check import TestServiceConfig
except ImportError:
    import TestServiceConfig


class Test_ServiceConfig(pytest_common.TestBase):
    """
    static-address is specified in parametrized data...
    """
    default_config = {
        "TestModule"   : "ServiceConfig",
        "OutputModule" : "Text",
        "Description"  : "Inspect Service Config",
        "Parameters"   : {
            "query" : { 
                "arguments" : {
                    "names" : [
                        "Store_{site-id}_One",
                        "Store_{site-id}_Two"
                        "Store_{site-id}_Three",
                        "Store_{site-id}_Four"
                    ]
                },
                "fields" : [
                    "name",
                    "shareServiceRoutes"
                ]
            },
            "flatten_path" : None,
            "expected_count" : 4,
            "entry_tests" : {
                "no_match" : {
                    "status"  : "PASS"
                },
                "defaults" : {
                    "status"  : "FAIL"
                },
                "tests"  : [
		    { 
			"test" : "?shareServiceRoutes == False && name == 'Store_{site-id}_Four'",
			"format" : "Service {name} share-service-routes is EMPTY",
		    },
		    { 
			"test" : "@shareServiceRoutes == 'None' || shareServiceRoutes != True",
			"format" : "Service {name} shared-service-routes={shareServiceRoutes}" 
		    }
                ],
                "result" : {
                    "FAIL" : "{match_count}/{total_count} services have config exceptions",
                    "WARN" : "Missing Services",
                    "PASS" : "All {total_count} services are OK"
                }
            }
        }
     }                


    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance,get_site_id_output,requests_post_output', [
       (
           {
              "config"  : default_config,
              "message" : "0  Inspect Service Config        : \x1b[32m\x1b[01mPASS\x1b[0m  All 4 services are OK"
           },
           "1234",
           [
               {
                    "regex"  : r"{ allServices",
                    "reply"  : {
                        "data": {
                            "allServices": {
                                "edges": [
                                    {
                                        "node": {
                                            "name": "Store_1234_One",
                                            "shareServiceRoutes": True
                                        }
                                    },
                                    {
                                        "node": {
                                            "name": "Store_1234_Two",
                                            "shareServiceRoutes": True
                                        }
                                    },
                                    {
                                        "node": {
                                            "name": "Store_1234_Three",
                                            "shareServiceRoutes": True
                                        }
                                    },
                                    {
                                        "node": {
                                            "name": "Store_1234_Four",
                                            "shareServiceRoutes": True
                                        }
                                    }
                                ]
                            }
                        }
                    }
               }
           ]
       ),
       (
           {
               "config"  : default_config,
               "message" : "0  Inspect Service Config        : \x1b[31m\x1b[01mFAIL  2/4 services have config exceptions\x1b[0m"
           },
           "1234",
           [
               {
                    "regex"  : r"{ allServices",
                    "reply"  : {
                        "data": {
                            "allServices": {
                                "edges": [
                                    {
                                        "node": {
                                            "name": "Store_1234_One",
                                            "shareServiceRoutes": True
                                        }
                                    },
                                    {
                                        "node": {
                                            "name": "Store_1234_Two",
                                            "shareServiceRoutes": False
                                        }
                                    },
                                    {
                                        "node": {
                                            "name": "Store_1234_Three",
                                            "shareServiceRoutes": True
                                        }
                                    },
                                    {
                                        "node": {
                                            "name": "Store_1234_Four"
                                        }
                                    }
                                ]
                            }
                        }
                    }
               }
           ]
       ),
       (
           {
               "config"  : default_config,
               "message" : "0  Inspect Service Config        : \x1b[31m\x1b[01mFAIL  0/2 services have config exceptions\x1b[0m"
           },
           "1234",
           [
               {
                    "regex"  : r"{ allServices",
                    "reply"  : {
                        "data": {
                            "allServices": {
                                "edges": [
                                    {
                                        "node": {
                                            "name": "Store_1234_One",
                                            "shareServiceRoutes": True
                                        }
                                    },
                                    {
                                        "node": {
                                            "name": "Store_1234_Three",
                                            "shareServiceRoutes": True
                                        }
                                    },
                                ]
                            }
                        }
                    }
               }
           ]
       )
    ] 
   )

    def test_service_config(self, test_instance, local_context, graphql_url, capsys, mock_get_site_id, mock_requests_post):
        test_id = 0
        config = test_instance["config"]
        test = TestServiceConfig.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()
        
        if self.args.debug:
            assert False, pprint.pformat(all_lines)
        else:
            assert all_lines[3] == test_instance["message"]


        

              
