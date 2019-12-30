#!/usr/bin/env python3.6
##############################################################################################
#  _            _       ____                 _           _     _ _ _ _         
# | |_ ___  ___| |_    |  _ \ ___  __ _  ___| |__   __ _| |__ (_) (_) |_ _   _ 
# | __/ _ \/ __| __|   | |_) / _ \/ _` |/ __| '_ \ / _` | '_ \| | | | __| | | |
# | ||  __/\__ \ |_    |  _ <  __/ (_| | (__| | | | (_| | |_) | | | | |_| |_| |
#  \__\___||___/\__|___|_| \_\___|\__,_|\___|_| |_|\__,_|_.__/|_|_|_|\__|\__, |
#                 |_____|                                                |___/ 
#  _____                    ____                                  
# |  ___| __ ___  _ __ ___ |  _ \ ___  ___ _ __ ___   _ __  _   _ 
# | |_ | '__/ _ \| '_ ` _ \| |_) / _ \/ _ \ '__/ __| | '_ \| | | |
# |  _|| | | (_) | | | | | |  __/  __/  __/ |  \__ \_| |_) | |_| |
# |_|  |_|  \___/|_| |_| |_|_|   \___|\___|_|  |___(_) .__/ \__, |
#                                                    |_|    |___/ 
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
    from stage_check import TestReachabilityFromPeers
except ImportError:
    import TestReachabilityFromPeers


class Test_ReachabilityFromPeers(pytest_common.TestBase):

    peer_routers_reply = {
      "data": {
        "allRouters": {
          "edges": [
            {
              "node": {
                "name" : "SITE0001P1",
                "peers": {
                  "edges": [
                    {
                      "node": {
                        "name": "SITE0002P1",
                        "routerName": "SITE0002P1"
                         }
                    },
                    {
                      "node": {
                        "name": "SITE0003P1",
                        "routerName": "SITE0003P1"
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

    """
    Note json value of null is interpreted as python None.
    """
    path_status_reply = {
        "data": {
            "allRouters": {
                "edges": [
                    {
              "node": {
              "name": "SITE0002P1",
              "peers": {
                  "edges": [
                      {
                  "node": {
                      "name": "SITE0001P1",
                      "routerName": "SITE0001P1",
                      "_id": "authority/router:SITE0002P1/peer:SITE0001P1",
                      "paths": [
                          {
                        "node": "SITE0002P1A",
                              "adjacentNode": "SITE0001P1A",
                              "adjacentHostname": None,
                              "deviceInterface": "devint_test_1",
                              "networkInterface": "netint_test_1_1",
                              "status": "UP"
                          }
                       ]
                   }
                },
                {
                  "node": {
                      "name": "SITE0003P1",
                      "routerName": "SITE0003P1",
                      "_id": "authority/router:SITE0003P1A/peer:SITE0002P1",
                      "paths": [
                          {
                        "node": "SITE0002P1A",
                              "adjacentNode": "SITE0003P1A",
                              "adjacentHostname": None,
                              "deviceInterface": "devint_test_1",
                              "networkInterface": "netint_test_1_1",
                              "status": None
                          },
                      {
                        "node": "SITE0001P1A",
                          "adjacentNode": None,
                          "adjacentHostname": "interface-1.SITE0001P1.Authority",
                          "deviceInterface": "devint_test_1",
                          "networkInterface": "netint_test_1.1",
                          "status": "Down"
                      }
                    ]
                  }
                }
              ]
            }
          }
        },
        {
          "node": {
              "name": "SITE0003P1",
              "peers": {
                  "edges": [
                      {
                  "node": {
                      "name": "SITE0001P1",
                      "routerName": "SITE0001P1",
                      "_id": "authority/router:SITE0003P1/peer:SITE0001P1",
                      "paths": [
                          {
                        "node": "SITE0003P1A",
                        "adjacentNode": None,
                        "adjacentHostname": None,
                        "deviceInterface": "devint_test_2",
                        "networkInterface": "netint_test_2.1",
                        "status": "UP"
                      },
                      {
                        "node": "SITE003P1A",
                        "adjacentNode": None,
                        "adjacentHostname": None,
                        "deviceInterface": "devint_test_3",
                        "networkInterface": "netint_test_3.1",
                        "status": "DOWN"
                      }
                    ]
                  }
                },
                {
                  "node": {
                    "name": "SITE0002P1",
                    "routerName": "SITE0002P1",
                    "_id": "authority/router:SITE000/peer:SITE000",
                    "paths": [
                      {
                        "node": "SITE0003P1A",
                        "adjacentNode": None,
                        "adjacentHostname": None,
                        "deviceInterface": "devint_test_1",
                        "networkInterface": "netint_test_1.1",
                        "status": "UP"
                      },
                      {
                        "node": "SITE0003P1A",
                        "adjacentNode": None,
                        "adjacentHostname": None,
                        "deviceInterface": "devint_test_2",
                        "networkInterface": "devint_test_2.1",
                        "status": "DOWN"
                      }
                    ]
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


    """
    static-address is specified in parametrized data...
    """
    default_config = {
        "TestModule"   : "ReachabilityFromPeers",
        "OutputModule" : "Text",
        "Description"  : "Reachability From Peers",
        "Parameters"   : {
            "entry_tests" : {
                "no_match" : {
                    "status"  : "PASS"
                },
                "defaults" : {
                    "status"  : "FAIL"
                },
                "tests"  : [
                    {
                        "test"   : "status != 'UP'" ,
                        "format" : "{}:{deviceInterface}:{networkInterface}->{node} status={status}"
                    }
                ],
               "result"    : {
                   "PASS"  : "All {total_count} paths from {router_OK} are UP",
                   "FAIL"  : "{router_FAIL}/{router_total} routers report {FAIL}/{total_count} paths DOWN"
               }
            }
        }
    }

    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance,requests_post_output', [
       (
           {
              "config"  : default_config,
              "message" : "0  Reachability From Peers       : \x1b[31m\x1b[01mFAIL  1/2 routers report 1/3 paths DOWN\x1b[0m"
           },
           [
               {
                    "regex"  : r"{ allRouters\s*\(\s*name\s*:",
                    "reply"  : peer_routers_reply
               },
               {
                    "regex"  : r"{ allRouters\s*\(\s*names\s*:",
                    "reply"  : path_status_reply
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
        test = TestReachabilityFromPeers.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()
        
        if self.args.debug == False:
            # assert len(all_lines[cur_index]) == len(test_instance["message"]) 
            assert all_lines[0] == test_instance["message"]
        else:
            lc = 0
            for line in all_lines:
                print(f"{lc}: {line}")
                lc += 1


        

              
