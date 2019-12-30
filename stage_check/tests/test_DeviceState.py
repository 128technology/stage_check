#!/usr/bin/env python3.6
##########################################################################################
#   _            _       ____             _          ____  _        _                     
#  | |_ ___  ___| |_    |  _ \  _____   _(_) ___ ___/ ___|| |_ __ _| |_ ___   _ __  _   _ 
#  | __/ _ \/ __| __|   | | | |/ _ \ \ / / |/ __/ _ \___ \| __/ _` | __/ _ \ | '_ \| | | |
#  | ||  __/\__ \ |_    | |_| |  __/\ V /| | (_|  __/___) | || (_| | ||  __/_| |_) | |_| |
#   \__\___||___/\__|___|____/ \___| \_/ |_|\___\___|____/ \__\__,_|\__\___(_) .__/ \__, |
#                  |_____|                                                   |_|    |___/ 
#
##########################################################################################
import os
import sys

import argparse

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
    from stage_check import RouterContext
except ImportError:
    import RouterContext

try:
    from stage_check import TestDeviceState
except ImportError:
    import TestDeviceState   

class Test_DeviceState(pytest_common.TestBase):
    config = {
        "TestModule"   : "DeviceState",
        "OutputModule" : "Text",
        "Description"  : "NetworkDeviceStatus",
        "Parameters"   : {
           "exclude_tests" : [
               "name == 't1-backup'"
           ],
           "entry_tests" : {
               "no_match" : {
                   "status"  : "PASS"
               },
               "defaults" : {
                   "status"  : "FAIL",
                   "format"  : "Node {node_name} dev {name} is {state.operationalStatus}"
               },
               "tests" : [
                   { "test" : "state.operationalStatus == 'OPER_DOWN'" }
               ]
           }
        }
    }

    def setup(self):
        self.args = argparse.Namespace()
        self.args.debug = False
        self.args.regex_patterns = False
        self.args.version = False
        self.args.router=""
        self.args.primary_regex="A$"
        self.args.secondary_regex="B$"
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance', [
    {
      "json_reply" : {
         'data':  {
             'allRouters': {
               'edges': [
                   {
                      'node':  {
                          'name': 'corp2',
                          'nodes': {
                             'edges': [
                                {
                                   'node': {
                                      'deviceInterfaces': {
                                           'edges': [
                                               {
                                                  'node': {
                                                      'name': 'PUBLIC_P',
                                                      'state': {
                                                          'operationalStatus': 'OPER_UP'
                                                       }
                                                    }
                                                 },
                                               {
                                                   'node': {
                                                       'name': 'WIRELESS_P',
                                                       'state': {
                                                           'operationalStatus': 'OPER_UP'
                                                       }
                                                     }
                                                }
                                             ]
                                        },
                                      'name': 'corp2-primary'
                                     }
                                  },
                                {
                                    'node': {
                                        'deviceInterfaces': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'name': 'PUBLIC_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP'
                                                       }
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'name': 'WIRELESS_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP'}
                                                    }
                                                }
                                            ]
                                        },
                                        'name': 'corp2-secondary'}
                                }
                             ]
                            }
                        }
                     }
                 ]
               }
           }
        },
        "message" : "0  NetworkDeviceStatus           : \x1b[32m\x1b[01mPASS\x1b[0m  All required network devices In Service"
      },
    {
      "json_reply" : {
         'data':  {
             'allRouters': {
               'edges': [
                   {
                      'node':  {
                          'name': 'corp2',
                          'nodes': {
                             'edges': [
                                {
                                   'node': {
                                      'deviceInterfaces': {
                                           'edges': [
                                               {
                                                  'node': {
                                                      'name': 'PUBLIC_P',
                                                      'state': {
                                                          'operationalStatus': 'OPER_DOWN'
                                                       }
                                                    }
                                                 },
                                               {
                                                   'node': {
                                                       'name': 'WIRELESS_P',
                                                       'state': {
                                                           'operationalStatus': 'OPER_UP'
                                                       }
                                                     }
                                                }
                                             ]
                                        },
                                      'name': 'corp2-primary'
                                     }
                                  },
                                {
                                    'node': {
                                        'deviceInterfaces': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'name': 'PUBLIC_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_DOWN'
                                                        }
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'name': 'WIRELESS_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP'}
                                                    }
                                                }
                                            ]
                                        },
                                        'name': 'corp2-secondary'}
                                }
                             ]
                            }
                        }
                     }
                 ]
               }
           }
        },
        "message" : "0  NetworkDeviceStatus           : \x1b[31m\x1b[01mFAIL  2 required network devices are not LINK UP\x1b[0m"
      }
    ] 
   )

    def test_non_errors(self, test_instance, local_context, graphql_url, capsys):
        test_id = 0
        test = TestDeviceState.create_instance(test_id, Test_DeviceState.config, self.args)
        test.create_output_instance()
        responses.add(responses.POST, graphql_url, json=test_instance["json_reply"], status=200)
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()

        assert len(all_lines[0]) == len(test_instance["message"]) 
        assert all_lines[0] == test_instance["message"]

        
