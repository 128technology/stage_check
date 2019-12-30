#!/usr/bin/env python3.6
########################################################################################
#   _            _          _                 _   ____  _        _                     
#  | |_ ___  ___| |_       / \   ___ ___  ___| |_/ ___|| |_ __ _| |_ ___   _ __  _   _ 
#  | __/ _ \/ __| __|     / _ \ / __/ __|/ _ \ __\___ \| __/ _` | __/ _ \ | '_ \| | | |
#  | ||  __/\__ \ |_     / ___ \\__ \__ \  __/ |_ ___) | || (_| | ||  __/_| |_) | |_| |
#   \__\___||___/\__|___/_/   \_\___/___/\___|\__|____/ \__\__,_|\__\___(_) .__/ \__, |
#                  |_____|                                                |_|    |___/ 
#
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
    from stage_check import TestAssetState
except ImportError:
    import TestAssetState   

class Test_AssetState(pytest_common.TestBase):
    config = {
        "TestModule"   : "AssetState",
        "OutputModule" : "Text",
        "Description"  : "Check Router Asset(s) State",
        "Parameters"   : {
           "exclude_tests" : [],
           "entry_tests" : {
               "defaults" : {
                   "status"  : "FAIL",
                   "format"  : "Node {nodeName} is in state {status}"
               },
               "tests" : [
                   { "test" : "status != 'RUNNING'" }
               ],
               "result"    : {
                   "PASS"  : "All {non_match_count}/{total_count} nodes are in state RUNNING",
                   "FAIL"  : "{match_count}/{total_count} nodes are NOT RUNNING"
               }
           }
        }
    }

    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))
   
    @pytest.mark.usefixtures("create_router_files")
    @responses.activate
    @pytest.mark.parametrize('graphql_json',
    [
        {"data":
          {"allAuthorities":
             {"edges":
                [
                  {"node":
                     {"assets":
                         pytest_common.assets
                      }
                   }
                ]
             }
          }
        }
     ]
    )
    def test_on_router(self, graphql_json, local_context, capsys, graphql_url):
        test_id = 0
        test = TestAssetState.create_instance(test_id, Test_AssetState.config, self.args)
        test.create_output_instance()
        responses.add(responses.POST, graphql_url, json=graphql_json, status=200)
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()
 
        message = "0  Check Router Asset(s) State   : \033[34m\x1b[01mWARN  Test not supported by node corp2B type \033[31mcontrol\x1b[0m"
        #assert len(all_lines[0]) == len(message) 
        assert all_lines[0] == message

        #m = mocker.patch('requests.post', new=sim_requests_post, autospec=True)
        #with open("fubar", "r") as fp:
        #    # lines = fp.readlines()
        #    lines = fp.read().splitlines()
        #lines2=Test_AssetState.local_init.splitlines()
        #assert lines2 == lines

    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('graphql_json',
    [
        {"data":
          {"allAuthorities":
             {"edges":
                [
                  {"node":
                     {"assets":
                       [
                         {"assetId" : "LR000000000001",
                          "routerName" : "SITE0001P1",
                          "nodeName" : "SITE0001P1A",
                          "t128Version" : "4.1.1-1.el7.centos",
                          "status" : "RUNNING",
                          "assetIdConfigured" : True,
                          "text" : "",
                          "failedStatus" : None
                         },
                         {"assetId" : "LR000000000002",
                          "routerName" : "SITE0001P1",
                          "nodeName" : "SITE0001P1B",
                          "t128Version" : "4.1.1-1.el7.centos",
                          "status" : "RUNNING",
                          "assetIdConfigured" : True,
                          "text" : "",
                          "failedStatus" : None
                          }
                        ]
                      }
                   }
                ]
             }
          }
        }
     ]
    )
    def test_run_on_cond(self, graphql_json, local_context, capsys, graphql_url):
        test_id = 0
        test = TestAssetState.create_instance(test_id, Test_AssetState.config, self.args)
        test.create_output_instance()
        responses.add(responses.POST, graphql_url, json=graphql_json, status=200)
        router_context = RouterContext.create_instance(local_context, "SITE0001P1", self.args, 
                                                       pytest_common.assets[0])
        router_context.set_node(asset_json=pytest_common.assets[1])
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()

        json_body = { "1" : "a" }
        headers = {}
        headers['Content-Type']  = 'application/json'
        response = requests.post(graphql_url, data = json.dumps(json_body), headers = headers, verify = False) 
        assert response.status_code == 200
        assert response.json() == graphql_json
        #assert router_context.get_router() == "X"
        #assert router_context.primary_name() == "X"
        #assert router_context.secondary_name() == "X"

        message = "0  Check Router Asset(s) State   : \x1b[32m\x1b[01mPASS\x1b[0m  All 2/2 nodes are in state RUNNING"
        #assert len(all_lines[0]) == len(message) 
        assert all_lines[0] == message

        
