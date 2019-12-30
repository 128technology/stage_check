#!/usr/bin/env python3.6
########################################################################################
#   ____                              ____  _        _                          
#  |  _ \ _ __ ___   ___ ___  ___ ___/ ___|| |_ __ _| |_ ___  ___   _ __  _   _ 
#  | |_) | '__/ _ \ / __/ _ \/ __/ __\___ \| __/ _` | __/ _ \/ __| | '_ \| | | |
#  |  __/| | | (_) | (_|  __/\__ \__ \___) | || (_| | ||  __/\__ \_| |_) | |_| |
#  |_|   |_|  \___/ \___\___||___/___/____/ \__\__,_|\__\___||___(_) .__/ \__, |
#                                                                  |_|    |___/ 
########################################################################################
import os
import sys

import sly
import argparse

import pprint
import pytest
import mock
import pyfakefs

import requests
import json

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
    from stage_check import TestProcessStates
except ImportError:
    import TestProcessStates

"""                   
                   { 
                       "test"   : "! @peer_status && status != 'RUNNING'", 
                       "format" : "{name} in state {status}",
                       "status" : "FAIL" 
                   },
                   {
                       "test"   : "@peer_leaderStatus && peer_leaderStatus != 'PRIMARY' && leaderSstatus != 'PRIMARY'",
                       "format" : "{node_name}: {name} in leaderState {status}, peer leaderstate {peer_status}",
                       "status" : "FAIL"  
                   },
                   {
                       "test"   : "@peer_primary && peer_primary != TRUE && primary != TRUE",
                       "format" : "{node_name}: {name} is not primary and peer is not primary",
                       "status" : "FAIL"  
                   }
                 
"""

class Test_ProcessStates(pytest_common.TestBase):
    default_config = {
        "TestModule"   : "ProcessStates",
        "OutputModule" : "Text",
        "Description"  : "SSR Process States",
        "Parameters"   : {
           "exclude_tests" : [],
           "entry_tests" : {
               "defaults" : {
                   "status"  : "FAIL",
                   "format"  : "Node {nodeName} is in state {status}"
               },
               "no_match" : {
                   "status" : "PASS"
               },
               "tests" : [
                   { 
                       "test"   : "?peer_status && peer_status != 'RUNNING' && status != 'RUNNING'", 
                       "format" : "{node_name}: {name} in state {status}, peer state {peer_status}",
                       "status" : "FAIL" 
                   }
               ],
               "result"    : {
                   "PASS"  : "All {PASS}/{total_count} processes are RUNNING",
                   "FAIL"  : "{FAIL}/{total_count} processes are NOT RUNNING"
               }
           }
        }
    }

    big_reply = {
      "data": {
       "allRouters": {
          "name" : "SITE0001P1",
          "edges": [
            {
              "node": {
                "nodes": {
                  "edges": [
                    {
                      "node": {
                        "name" : "SITE0001P1A",
                        "state" : {
                          "processes": [
                            {
                              "name": "accessManager",
                              "processName": "accessManager",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "analyticsReporter",
                              "processName": "analyticsReporter",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "applicationFrameworkManager",
                              "processName": "applicationFrameworkManager",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "conflux",
                              "processName": "conflux",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "databaseQueryCoordinator",
                              "processName": "databaseQueryCoordinator",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "dnsManager",
                              "processName": "dnsManager",
                              "status": "RUNNING",
                              "primary": True,
                              "leaderStatus": "ACTIVE"
                            },
                            {
                              "name": "dynamicPeerUpdateManager",
                              "processName": "dynamicPeerUpdateManager",
                              "status": "RUNNING",
                              "primary": True,
                              "leaderStatus": "ACTIVE"
                            },
                            {
                              "name": "highway",
                              "processName": "highway",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "nodeMonitor",
                              "processName": "nodeMonitor",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "persistentDataManager",
                              "processName": "persistentDataManager",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "redisServerManager",
                              "processName": "redisServerManager",
                              "status": "RUNNING",
                              "primary": True,
                              "leaderStatus": "ACTIVE"
                           },
                           {
                              "name": "routingManager",
                              "processName": "routingManager",
                              "status": "RUNNING",
                              "primary": True,
                              "leaderStatus": "ACTIVE"
                           },
                           {
                              "name": "secureCommunicationManager",
                              "processName": "secureCommunicationManager",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                           },
                           {
                              "name": "securityKeyManager",
                              "processName": "securityKeyManager",
                              "status": "RUNNING",
                              "primary": True,
                              "leaderStatus": "ACTIVE"
                            },
                            {
                              "name": "snmpTrapAgent",
                              "processName": "snmpTrapAgent",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "stateMonitor",
                              "processName": "stateMonitor",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "systemServicesCoordinator",
                              "processName": "systemServicesCoordinator",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            }
                          ]
                        }
                      }
                   },
                   {
                    "node": {
                      "name" : "SITE0001P1B",
                      "state": {
                        "processes": [
                            {
                              "name": "accessManager",
                              "processName": "accessManager",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "analyticsReporter",
                              "processName": "analyticsReporter",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "applicationFrameworkManager",
                              "processName": "applicationFrameworkManager",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "conflux",
                              "processName": "conflux",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "databaseQueryCoordinator",
                              "processName": "databaseQueryCoordinator",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "dnsManager",
                              "processName": "dnsManager",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "STANDBY"
                            },
                            {
                              "name": "dynamicPeerUpdateManager",
                              "processName": "dynamicPeerUpdateManager",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "STANDBY"
                            },
                            {
                              "name": "highway",
                              "processName": "highway",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                              "name": "nodeMonitor",
                              "processName": "nodeMonitor",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                            },
                            {
                               "name": "persistentDataManager",
                               "processName": "persistentDataManager",
                               "status": "RUNNING",
                               "primary": False,
                               "leaderStatus": "NONE"
                            },
                            {
                               "name": "redisServerManager",
                               "processName": "redisServerManager",
                               "status": "RUNNING",
                               "primary": False,
                               "leaderStatus": "STANDBY"
                            },
                            {
                               "name": "routingManager",
                               "processName": "routingManager",
                               "status": "RUNNING",
                               "primary": False,
                               "leaderStatus": "STANDBY"
                            },
                            {
                                "name": "secureCommunicationManager",
                                "processName": "secureCommunicationManager",
                                "status": "RUNNING",
                                "primary": False,
                                "leaderStatus": "NONE"
                            },
                            {
                              "name": "securityKeyManager",
                              "processName": "securityKeyManager",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "STANDBY"
                             },
                             {
                               "name": "snmpTrapAgent",
                               "processName": "snmpTrapAgent",
                               "status": "RUNNING",
                               "primary": False,
                               "leaderStatus": "NONE"
                             },
                             {
                              "name": "stateMonitor",
                              "processName": "stateMonitor",
                              "status": "RUNNING",
                              "primary": False,
                              "leaderStatus": "NONE"
                             },
                             {
                               "name": "systemServicesCoordinator",
                               "processName": "systemServicesCoordinator",
                               "status": "RUNNING",
                               "primary": False,
                              "leaderStatus": "NONE"
                             }
                           ]
                        }
                      }
                    }
                  ]
                }
              }
            }
          ]
        }
      }
    }

    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))

    """
    GQLTemplates include unescaped \n which means the matching regex for the
    mocked request must be able to handle multi-line matching i.e. r'(?m)...'
    """

    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance,requests_post_output', [
       (
           {
              "config"  : default_config,
              "message" : "0  SSR Process States            : \x1b[32m\x1b[01mPASS\x1b[0m  All 34/34 processes are RUNNING"
           },
           [
               {
                    "regex"  : r"(?m)\n*\s*{\n*\s*allRouters\s*\(\s*name\s*:",
                    "reply"  : big_reply
               }
            ]
         )
      ]
    )


    def test_reachability_from(self, test_instance, local_context, graphql_url, capsys, mock_requests_post):
        test_id = 0
        config = test_instance["config"]
        # create_conductor_files above sets the local_context to conductor, 
        # but router_context is set to a router:
        self.args.router = "SITE0001P1"
        test = TestProcessStates.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()
        
        if self.args.debug == False:
            # assert len(all_lines[cur_index]) == len(test_instance["message"]) 
            assert all_lines[0] == test_instance["message"]
            #assert False, captured.out
        else:
            lc = 0
            for line in all_lines:
                print(f"{lc}: {line}")
                lc += 1

     

        
