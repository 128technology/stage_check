#!/usr/bin/env python3.6
######################################################################################
#
#   _            _       ____          _                 _                        
#  | |_ ___  ___| |_    |  _ \ ___  __| |_   _ _ __   __| | __ _ _ __   ___ _   _ 
#  | __/ _ \/ __| __|   | |_) / _ \/ _` | | | | '_ \ / _` |/ _` | '_ \ / __| | | |
#  | ||  __/\__ \ |_    |  _ <  __/ (_| | |_| | | | | (_| | (_| | | | | (__| |_| |
#   \__\___||___/\__|___|_| \_\___|\__,_|\__,_|_| |_|\__,_|\__,_|_| |_|\___|\__, |
#                  |_____|                                                  |___/ 
#   ____        _        _                     ____                                
#  |  _ \  __ _| |_ __ _| |__   __ _ ___  ___ / ___|___  _ __  _ __    _ __  _   _ 
#  | | | |/ _` | __/ _` | '_ \ / _` / __|/ _ \ |   / _ \| '_ \| '_ \  | '_ \| | | |
#  | |_| | (_| | || (_| | |_) | (_| \__ \  __/ |__| (_) | | | | | | |_| |_) | |_| |
#  |____/ \__,_|\__\__,_|_.__/ \__,_|___/\___|\____\___/|_| |_|_| |_(_) .__/ \__, |
#                                                                     |_|    |___/ 
#       
#######################################################################################
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
    from stage_check import TestRedundancyDatabaseConn
except ImportError:
    import TestRedundancyDatabaseConn


class Test_RedundancyDatabaseConn(pytest_common.TestBase):

    success_reply = {
      "data": {
        "metrics": {
          "redundancy" : { 
            "databaseConnection": {
              "activeConnections" : [
                {
                  "node"  : "SITE0001P2A",
                  "value" : "2"
                },
                {
                  "node"  : "SITE0001P2B",
                  "value" : "1"
                }
              ]
            }
          }
        }
      }
    }

    one_fail_reply = {
      "data": {
        "metrics": {
          "redundancy" : { 
            "databaseConnection": {
              "activeConnections" : [
                {
                  "node"  : "SITE0001P2A",
                  "value" : "1"
                },
                {
                  "node"  : "SITE0001P2B",
                  "value" : "0"
                }
              ] 
            }
          }
        }
      }
    }

    one_only_reply = {
      "data": {
        "metrics": {
          "redundancy" : { 
            "databaseConnection": {
              "activeConnections" : [
                {
                  "node"  : "SITE0001P2B",
                  "value" : "0"
                }
              ]
            }
          }
        }
      }
    }

    both_fail_reply = {
      "data": {
        "metrics": {
          "redundancy" : { 
            "databaseConnection": {
              "activeConnections" : [
                {
                  "node"  : "SITE0001P2A",
                  "value" : "0"
                },
                {
                  "node"  : "SITE0001P2B",
                  "value" : "0"
                }
              ]
            }
          }
        }
      }
    }

    """
    static-address is specified in parametrized data...
    """
    default_config = {
        "TestModule"   : "RedundancyDatabaseConn",
        "OutputModule" : "Text",
        "Description"  : "Redundancy DB",
        "Parameters"   : {
            "expected_entries" : 2,
            "entry_tests" : {
                "no_match" : {
                   "status"  : "PASS"
                },
                "tests" : [
                    {
                        "test"   : "value < 1",
                        "format" : "     {node}: Active DB Connections = {value}",
                        "status" : "FAIL"
                    }
                ],
                "result": {
                     "PASS" : "{PASS}/{tested_count} nodes have >=1 redundancy DB conns",
                     "FAIL" : "{FAIL}/{tested_count} nodes have 0 redundancy DB conns",
                     "WARN" : ""
                }
            }
        }
    }

    test_parameters = [
        {
            "config" : default_config,
            "json_reply" : success_reply,
            "messages" : [
                  "0  Redundancy DB                 : \x1b[32m\x1b[01mPASS\x1b[0m  2/2 nodes have >=1 redundancy DB conns"
             ],
            "json_status" : 0
        }, 
        {
            "config" : default_config,
            "json_reply" : one_fail_reply,
            "messages" : [
                  "0  Redundancy DB                 : \x1b[31m\x1b[01mFAIL  1/2 nodes have 0 redundancy DB conns\x1b[0m",
                  "   :                                          SITE0001P2B: Active DB Connections = 0"
             ],
            "json_status" : 1
        }, 
        {
            "config" : default_config,
            "json_reply" : both_fail_reply,
            "messages" : [
                  "0  Redundancy DB                 : \x1b[31m\x1b[01mFAIL  2/2 nodes have 0 redundancy DB conns\x1b[0m",
                   "   :                                          SITE0001P2A: Active DB Connections = 0",
                   "   :                                          SITE0001P2B: Active DB Connections = 0"
             ],
            "json_status" : 1
        }, 
        {
            "config" : default_config,
            "json_reply" : one_only_reply,
            "messages" : [
                  "0  Redundancy DB                 : \x1b[31m\x1b[01mFAIL  Data included 1 nodes; expected 2\x1b[0m",
                   "   :                                          SITE0001P2B: Active DB Connections = 0"
             ],
            "json_status" : 1
        }, 
    ]

    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance', test_parameters)

    def test_redundancy_db_conn(self, test_instance, local_context, graphql_url, capsys):
        test_id = 0
        test = TestRedundancyDatabaseConn.create_instance(test_id, test_instance["config"], self.args)
        test.create_output_instance()
        responses.add(responses.POST, graphql_url, json=test_instance["json_reply"], status=200)
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test.run(local_context, router_context, None, fp=None)
        #self.verify_output(capsys, test_instance)


        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()

        # assert len(all_lines[0]) == len(test_instance["message"]) 
        count = 0
        test_messages = test_instance["messages"]
        for line in all_lines:
            assert count < len(test_messages), f'{count}: "' + line + '" == MISSING!'  
            assert line == test_messages[count]
            count += 1
        assert count == len(test_messages) 






        

              
