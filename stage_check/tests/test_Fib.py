#!/usr/bin/env python3.6
#################################################################################
#   _            _       _____ _ _                  
#  | |_ ___  ___| |_    |  ___(_) |__   _ __  _   _ 
#  | __/ _ \/ __| __|   | |_  | | '_ \ | '_ \| | | |
#  | ||  __/\__ \ |_    |  _| | | |_) || |_) | |_| |
#   \__\___||___/\__|___|_|   |_|_.__(_) .__/ \__, |
#                  |_____|             |_|    |___/ 
#
#################################################################################
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
    from stage_check import TestFib
except ImportError:
    import TestFib


class Test_Fib(pytest_common.TestBase):
    config = {
        "TestModule"   : "Fib",
        "OutputModule" : "Text",
        "Description"  : "Check Fib",
        "Parameters"   : {
            "max_sessions_to_query"  : 500,
            "idle_maximum_seconds"   : 3600,
            "idle_threshold_seconds" : 400,
	    "filter_string"          : "5060",
            "exclude_tests"          : [
	        "sourcePort != 5060 && destPort != 5060"
            ],
            "entry_tests"            : {
	        "tests"  : [
                     {
                         "test"   : "allRouters/nodes/fibEntries/route/tenant == 'AppDMZ.LAN.Site' && \
                                     allRouters/nodes/fibEntries/route/protocol == 'ICMP' && \
                                     allRouters/nodes/fibEntries/serviceName == 'RI_Any_default'", 
                         "format" : "session {sessionUuid} idle {test_idle_duration}s",
	   	         "status" : "PASS"
                     }
                ],
                "result"    : {
                    "PASS"  : "Test Passed",
                    "FAIL"  : "Test Failed"
                }
            }
        }
    }

    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance', [
      {
        "json_reply" : {
          "data": {
            "allRouters": {
              "edges": [
               {
                 "node": {
                 "name": "SITE00001P1",
                 "nodes": {
                   "edges": [
                   {
                     "node": {
                     "name": "SITE00001P1A",
                     "fibEntries": {
                       "edges": [
                       {
                         "node": {
                           "serviceName": "RI_Any_default",
                           "route": {
                             "tenant" : "Vertical.LAN.Store",
                             "ipPrefix": "0.0.0.0/0",
                             "l4Port": 0,
                             "l4PortUpper": 0,
                             "protocol": "ICMP",
                             "nextHops": [
                               {
                                 "devicePort": 3,
                                 "gateway": "12.230.70.246",
                                 "nodeId": 1,
                                 "vlan": 0,
                                 "deviceInterface": "SiteWAN",
                                 "networkInterface": "Broadband"
                               },
                               {
                                 "devicePort": 1,
                                 "gateway": "12.230.70.246",
                                 "nodeId": 1,
                                 "vlan": 0,
                                 "deviceInterface": "SiteLTE",
                                 "networkInterface": "Lte"
                               },
                               {
                                 "devicePort": 3,
                                 "gateway": "12.51.52.30",
                                 "nodeId": 1,
                                 "vlan": 0,
                                 "deviceInterface": "SiteWAN",
                                 "networkInterface": "Broadband"
                               },
                               {
                                 "devicePort": 3,
                                 "gateway": "12.51.52.22",
                                 "nodeId": 1,
                                 "vlan": 0,
                                 "deviceInterface": "SiteWAN",
                                 "networkInterface": "Broadband"
                               },
                               {
                                 "devicePort": 1,
                                 "gateway": "12.51.52.22",
                                 "nodeId": 1,
                                 "vlan": 0,
                                 "deviceInterface": "SiteLTE",
                                 "networkInterface": "Lte"
                               },
                               {
                                 "devicePort": 1,
                                 "gateway": "12.51.52.30",
                                 "nodeId": 1,
                                 "vlan": 0,
                                 "deviceInterface": "SiteLTE",
                                 "networkInterface": "Lte"
                                }
                              ]
                             }
                            }
                          },
                          {
                          "node": {
                            "serviceName": "RI_Any_default",
                            "route": {
                              "tenant": "AppDMZ.LAN.Site",
                              "ipPrefix": "0.0.0.0/0",
                              "l4Port": 0,
                              "l4PortUpper": 0,
                              "protocol": "ICMP",
                              "nextHops": [
                                {
                                  "devicePort": 3,
                                  "gateway": "12.230.70.246",
                                  "nodeId": 1,
                                  "vlan": 0,
                                  "deviceInterface": "SiteWAN",
                                  "networkInterface": "Broadband"
                                },
                                {
                                  "devicePort": 1,
                                  "gateway": "12.230.70.246",
                                  "nodeId": 1,
                                  "vlan": 0,
                                  "deviceInterface": "SiteLTE",
                                  "networkInterface": "Lte"
                                },
                                {
                                  "devicePort": 3,
                                  "gateway": "12.51.52.30",
                                  "nodeId": 1,
                                  "vlan": 0,
                                  "deviceInterface": "SiteWAN",
                                  "networkInterface": "Broadband"
                                },
                                {
                                  "devicePort": 3,
                                  "gateway": "12.51.52.22",
                                  "nodeId": 1,
                                  "vlan": 0,
                                  "deviceInterface": "SiteWAN",
                                  "networkInterface": "Broadband"
                                },
                                {
                                  "devicePort": 1,
                                  "gateway": "12.51.52.22",
                                  "nodeId": 1,
                                  "vlan": 0,
                                  "deviceInterface": "SiteLTE",
                                  "networkInterface": "Lte"
                                },
                                {
                                  "devicePort": 1,
                                  "gateway": "12.51.52.30",
                                  "nodeId": 1,
                                  "vlan": 0,
                                  "deviceInterface": "SiteLTE",
                                  "networkInterface": "Lte"
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
                ]
              }
            }
          },
          "message" : "0  Check Fib                     : \x1b[32m\x1b[01mPASS\x1b[0m  12 FIB entries PASS (0 excluded)"
       }
     ]
   )

    #
    # Revisit this test -- what exactly should this test do... count number of matching
    # entries?  
    #
    def test_run_on_cond(self, test_instance, local_context, graphql_url, capsys):
        test_id = 0
        test = TestFib.create_instance(test_id, Test_Fib.config, self.args)
        test.create_output_instance()

        responses.add(responses.POST, graphql_url, json=pytest_common.assets, status=200)
        router_context = RouterContext.create_instance(local_context, "SITE0001P1", self.args, 
                                                       pytest_common.assets[0])
        router_context.set_node(asset_json=pytest_common.assets[1])

        # Note if test.run uses more than one call to the graphql API, responses.remove()
        # and responses.add() cannot properly satisfy different requests to the same url
        responses.remove(responses.POST, graphql_url)
        responses.add(responses.POST, graphql_url, json=test_instance["json_reply"], 
                      status=200)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()

        assert all_lines[0] == test_instance["message"]

        
