#!/usr/bin/env python3.6
##############################################################################################
#   _            _       _    _       ___        __                    
#  | |_ ___  ___| |_    | |  | |_ ___|_ _|_ __  / _| ___   _ __  _   _ 
#  | __/ _ \/ __| __|   | |  | __/ _ \| || '_ \| |_ / _ \ | '_ \| | | |
#  | ||  __/\__ \ |_    | |__| ||  __/| || | | |  _| (_) || |_) | |_| |
#   \__\___||___/\__|___|_____\__\___|___|_| |_|_|  \___(_) .__/ \__, |
#                   |_____|                                |_|    |___/ 
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
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest

try:
    from stage_check import TestNodeConnectivity
except ImportError:
    import TestNodeCOnnectivity


class Test_NodeConnectivity(pytest_common.TestBase):
    """
    static-address is specified in parametrized data...
    """
    default_config = {
        "TestModule"   : "NodeConnectivity",
        "OutputModule" : "Text",
        "Description"  : "Test node connectivity",
        "Parameters"   : {
            "exclude_tests" : [
                 {  "status": "CONNECTED" }
            ]
        }
    }

    graphql_router_asset_regex = r"\{allRouters.*?nodes.*?state\s*\{\s*processes"

    graphql_node_connectivity_regex = r"\{allRouters.*?nodes.*?connectivity"

    one_node_connx_pass_data = {
        'data': {
            'allRouters': {
            'edges': [
               {
                  'node': {
                      'name': 'corp2',
                      'nodes': {
                          'edges': [
                              {
                                  'node': {
                                       'assetId': 'LR012345678901',
                                       'connectivity': [
                                           {
                                               'remoteNodeName' : 'cond_A',
                                               'remoteNodeRole': 'CONDUCTOR',
                                               'remoteRouterName': 'cond',
                                               'status': 'CONNECTED'
                                           },
                                           {
                                               'remoteNodeName': 'cond_B',
                                               'remoteNodeRole': 'CONDUCTOR',
                                               'remoteRouterName': 'cond',
                                               'status': 'CONNECTED'
                                           }
                                       ],
                                       'name'   : 'corp2A'
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

    two_node_connx_fail_data = {
        'data': {
            'allRouters': {
            'edges': [
               {
                  'node': {
                      'name': 'corp2',
                      'nodes': {
                          'edges': [
                              {
                                  'node': {
                                      'assetId': 'LR012345678901',
                                      'connectivity': [
                                          {
                                              'remoteNodeName' : 'cond_A',
                                              'remoteNodeRole': 'CONDUCTOR',
                                              'remoteRouterName': 'cond',
                                              'status': 'CONNECTED'
                                          },
                                          {
                                              'remoteNodeName': 'cond_B',
                                              'remoteNodeRole': 'CONDUCTOR',
                                              'remoteRouterName': 'cond',
                                              'status': 'DISCONNECTED'
                                          },
                                          {
                                              'remoteNodeName': 'corp2B',
                                              'remoteNodeRole': 'CONTROL',
                                              'remoteRouterName': 'corp2',
                                              'status': 'CONNECTED'
                                          }
                                       ],
                                      'name': 'corp2A'
                                 }
                            },
                            {
                                'node': {
                                     'assetId': 'LR012345678902',
                                      'connectivity': [
                                          {
                                              'remoteNodeName' : 'cond_A',
                                              'remoteNodeRole': 'CONDUCTOR',
                                              'remoteRouterName': 'cond',
                                              'status': 'CONNECTED'
                                          },
                                          {
                                              'remoteNodeName': 'cond_B',
                                              'remoteNodeRole': 'CONDUCTOR',
                                              'remoteRouterName': 'cond',
                                              'status': 'CONNECTED'
                                          },
                                          {
                                              'remoteNodeName': 'corp2A',
                                              'remoteNodeRole': 'CONTROL',
                                              'remoteRouterName': 'corp2',
                                              'status': 'DISCONNECTED'
                                          }
                                     ],
                                     'name': 'corp2B'
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
        self.default_args(router="corp2", node="corp2A")
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @pytest.mark.parametrize('test_instance,requests_post_output', [
       (
          {
              "config"      : default_config,
              "second_node" : False,
              "headline"    : "0  Test node connectivity        : \x1b[32m\x1b[01mPASS\x1b[0m  2 / 2 connections OK"
          },
          [
              {
                  "regex" : graphql_router_asset_regex,
                  "reply" : pytest_common.TestBase.router_info_reply_single
              },
              {
                  "regex" : graphql_node_connectivity_regex,
                  "reply" : one_node_connx_pass_data
              }
          ]
       ),
       (
          {
              "config"      : default_config,
              "second_node" : True,
              "headline"    : "0  Test node connectivity        : \x1b[31m\x1b[01mFAIL  2 / 6 connections are not status=CONNECTED\x1b[0m"
          },
          [
              {
                  "regex" : graphql_router_asset_regex,
                  "reply" : pytest_common.TestBase.router_info_reply
              },
              {
                  "regex" : graphql_node_connectivity_regex,
                  "reply" : two_node_connx_fail_data
              }
          ]
       )
     ] 
   )


    def test_node_connections(self, test_instance, local_context, graphql_url, capsys, mock_check_user, mock_requests_post):
        config = test_instance["config"]
        test_id = 0
        test = TestNodeConnectivity.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(
            local_context, 
            self.args.router, 
            self.args)
        if test_instance["second_node"]:
            router_context.set_node(name="corp2B")

        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()
        
        #assert False, pprint.pformat(all_lines)
        assert all_lines[0] == test_instance["headline"]

