#!/usr/bin/env python3.6
##############################################################################################
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
    from stage_check import TestLteIfConfig
except ImportError:
    import TestLteIfConfig

def prep_output_list(source, namespace, device):
    lte_source = { "LTE" : source }
    source_string = json.dumps(lte_source, indent=None)
    json_output_dict = { "output" : source_string }
    if not namespace is None:
        json_output_dict['namespace'] = namespace
    if not device is None:
        json_output_dict['device'] = device
    json_output = [ json_output_dict ]
    #json_output = [ { "output" : source_string, "namespace" : namespace, "device" :  device } ]
    json_string = json.dumps(json_output, indent=None)
    test_string = "JSON: " + json_string
    #assert False, f"PREP_OUTPUT: {json.dumps([test_string], indent=2)}"     
    return [ test_string ]

class Test_LteIfConfig(pytest_common.TestBase):
    """
    static-address is specified in parametrized data...
    """
    default_config = {
        "TestModule"   : "LteIfConfig",
        "OutputModule" : "Text",
        "Description"  : "Test LTE Intf Stats",
        "Parameters"   : {
            "node_type" : "primary",
            "entry_tests" : {
                "no_match" : {
                    "status"  : "PASS"
                },
                "defaults" : {
                    "status"  : "FAIL"
                },
                "tests"  : [
                    { "test" : "?RX_errors && RX_errors > 1000" }
                ]        
            }
        }
    }

    all_config = {
        "TestModule"   : "LteIfConfig",
        "OutputModule" : "Text",
        "Description"  : "Test LTE Intf Stats",
        "Parameters"   : {
            "node_type" : "all",
            "entry_tests" : {
                "no_match" : {
                    "status"  : "PASS"
                },
                "defaults" : {
                    "status"  : "FAIL"
                },
                "tests"  : [
                    { "test" : "?RX_errors && RX_errors > 1000" }
                ]        
            }
        }
    }

    graphql_router_asset_regex = r"\{allRouters.*?nodes.*?state\s*\{\s*processes"

    graphql_devint_regex = r"\{allRouters.*?nodes.*?deviceInterfaces"

    one_node_dev_data = {
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
                                       'deviceInterfaces': {
                                           'edges': [
                                                {
                                                     'node': {
                                                           'name': '1',
                                                           'type' : 'lte',
                                                           'globalId' : 1,
                                                           'deviceId' : 1,
                                                           'targetInterface' : 'fubar_1',
                                                           'state': {'operationalStatus': 'OPER_UP' }
                                                      }
                                                },
                                                {
                                                     'node': {
                                                           'name': '2',
                                                           'type' : 'ethernet',
                                                           'globalId' : 2,
                                                           'deviceId' : 2,
                                                           'targetInterface' : None,
                                                           'state': {'operationalStatus': 'OPER_UP'}
                                                      }
                                                },
                                                {
                                                     'node': {
                                                          'name': '3',
                                                           'type' : 'lte',
                                                           'globalId' : 3,
                                                           'deviceId' : 3,
                                                           'targetInterface' : 'fubar_3',
                                                           'state': {'operationalStatus': 'OPER_DOWN'}
                                                     }
                                                },
                                                {
                                                     'node': {
                                                          'name': '4',
                                                           'type' : 'lte',
                                                           'globalId' : 4,
                                                           'deviceId' : 4,
                                                           'targetInterface' : 'fubar_4',
                                                           'state': {'operationalStatus': None}
                                                     }
                                                },
                                                {
                                                     'node': {
                                                          'name': '5',
                                                           'type' : 'ethernet',
                                                           'globalId' : 5,
                                                           'deviceId' : 5,
                                                           'targetInterface' : None,
                                                           'state': {'operationalStatus': 'OPER_DOWN'}
                                                     }
                                                }
                                           ]
                                      },
                                      'name': 'corp2A'
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

    two_node_dev_data = {
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
                                       'deviceInterfaces': {
                                           'edges': [
                                                {
                                                     'node': {
                                                           'name': '1',
                                                           'type' : 'lte',
                                                           'globalId' : 1,
                                                           'deviceId' : 1,
                                                           'targetInterface' : 'fubar_1',
                                                           'state': {'operationalStatus': 'OPER_UP' }
                                                      }
                                                },
                                                {
                                                     'node': {
                                                           'name': '2',
                                                           'type' : 'ethernet',
                                                           'globalId' : 2,
                                                           'deviceId' : 2,
                                                           'targetInterface' : None,
                                                           'state': {'operationalStatus': 'OPER_UP'}
                                                      }
                                                },
                                                {
                                                     'node': {
                                                          'name': '3',
                                                           'type' : 'lte',
                                                           'globalId' : 3,
                                                           'deviceId' : 3,
                                                           'targetInterface' : 'fubar_3',
                                                           'state': {'operationalStatus': 'OPER_DOWN'}
                                                     }
                                                },
                                                {
                                                     'node': {
                                                          'name': '4',
                                                           'type' : 'lte',
                                                           'globalId' : 4,
                                                           'deviceId' : 4,
                                                           'targetInterface' : 'fubar_4',
                                                           'state': {'operationalStatus': None}
                                                     }
                                                },
                                                {
                                                     'node': {
                                                          'name': '5',
                                                           'type' : 'ethernet',
                                                           'globalId' : 5,
                                                           'deviceId' : 5,
                                                           'targetInterface' : None,
                                                           'state': {'operationalStatus': 'OPER_DOWN'}
                                                     }
                                                }
                                           ]
                                      },
                                      'name': 'corp2A'
                                 }
                            },
                            {
                                'node': {
                                     'assetId': 'LR012345678902',
                                     'deviceInterfaces': {
                                         'edges': [
                                              {
                                                   'node': {
                                                         'name': '1',
                                                         'type' : 'lte',
                                                         'globalId' : 1,
                                                         'deviceId' : 1,
                                                         'targetInterface' : 'fubar_1',
                                                         'state': {'operationalStatus': 'OPER_UP' }
                                                    }
                                              },
                                              {
                                                   'node': {
                                                         'name': '2',
                                                         'type' : 'ethernet',
                                                         'globalId' : 2,
                                                         'deviceId' : 2,
                                                         'targetInterface' : None,
                                                         'state': {'operationalStatus': 'OPER_UP'}
                                                    }
                                              },
                                              {
                                                   'node': {
                                                        'name': '3',
                                                         'type' : 'lte',
                                                         'globalId' : 3,
                                                         'deviceId' : 3,
                                                         'targetInterface' : 'fubar_3',
                                                         'state': {'operationalStatus': 'OPER_DOWN'}
                                                   }
                                              },
                                              {
                                                   'node': {
                                                        'name': '4',
                                                        'type' : 'lte',
                                                        'globalId' : 4,
                                                        'deviceId' : 4,
                                                        'targetInterface' : 'fubar_4',
                                                        'state': {'operationalStatus': None}
                                                    }
                                              },
                                              {
                                                   'node': {
                                                        'name': '5',
                                                        'type' : 'ethernet',
                                                        'globalId' : 5,
                                                        'deviceId' : 5,
                                                        'targetInterface' : None,
                                                        'state': {'operationalStatus': 'OPER_DOWN'}
                                                     }
                                                }
                                           ]
                                      },
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

    passing_dev_data = {
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
                                       'deviceInterfaces': {
                                           'edges': [
                                                {
                                                     'node': {
                                                           'name': '1',
                                                           'type' : 'lte',
                                                           'globalId' : 1,
                                                           'deviceId' : 1,
                                                           'targetInterface' : 'fubar_1',
                                                           'state': {'operationalStatus': 'OPER_UP' }
                                                      }
                                                }
                                           ]
                                      },
                                      'name': 'corp2A'
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

    linux_ifconfig_as_json = {
       "RX_packets"    : 0,
       "RX_bytes"      : 0,
       "RX_errors"     : 0,
       "RX_dropped"    : 0,
       "RX_overruns"   : 0,
       "RX_frame"      : 0,
       "TX_packets"    : 13,
       "TX_bytes"      : 624,
       "TX_errors"     : 0,
       "TX_dropped"    : 0,
       "TX_overruns"   : 0,
       "TX_carrier"    : 0,
       "TX_collisions" : 0
    }

    test_parameters = [ 
       (
          {
              "config"      : default_config,
              "second_node" : False,
              "headline"    : "0  Test LTE Intf Stats           : \x1b[31m\x1b[01mFAIL  2 issues with 2/1 (cfg:3/5) interfaces\x1b[0m",
              "json_status" : 1
          },
          {
              "primary"   : prep_output_list(linux_ifconfig_as_json, "lte", "fubar_1"),
              "secondary" : prep_output_list(linux_ifconfig_as_json, "lte", "fubar_1"),
              "solitary"  : prep_output_list(linux_ifconfig_as_json, "lte", "fubar_1")
          },
          [
              {
                  "regex" : graphql_router_asset_regex,
                  "reply" : pytest_common.TestBase.router_info_reply_single
              },
              {
                  "regex" : graphql_devint_regex,
                  "reply" : one_node_dev_data
              }
          ]
       ),
       (
          {
              "config"      : all_config,
              "second_node" : True,
              "headline"    : "0  Test LTE Intf Stats           : \x1b[31m\x1b[01mFAIL  4 issues with 4/2 (cfg:6/10) interfaces\x1b[0m",
              "json_status" : 1
          },
          {
              "primary"   : prep_output_list(linux_ifconfig_as_json, "lte", "fubar_1"),
              "secondary" : prep_output_list(linux_ifconfig_as_json, "lte", "fubar_1"),
              "solitary"  : prep_output_list(linux_ifconfig_as_json, "lte", "fubar_1")
          },
          [
              {
                  "regex" : graphql_router_asset_regex,
                  "reply" : pytest_common.TestBase.router_info_reply
              },
              {
                  "regex" : graphql_devint_regex,
                  "reply" : two_node_dev_data
              }
          ]
       ),
       (
          {
              "config"      : all_config,
              "second_node" : False,
              "headline"    : "0  Test LTE Intf Stats           : \x1b[32m\x1b[01mPASS\x1b[0m  All 1 (cfg:1/1) interfaces(s) OK",
              "json_status" : 0
          },
          {
              "primary"   : prep_output_list(linux_ifconfig_as_json, "lte", "fubar_1"),
              "secondary" : prep_output_list(linux_ifconfig_as_json, "lte", "fubar_1"),
              "solitary"  : prep_output_list(linux_ifconfig_as_json, "lte", "fubar_1")
          },
          [
              {
                  "regex" : graphql_router_asset_regex,
                  "reply" : pytest_common.TestBase.router_info_reply_single
              },
              {
                  "regex" : graphql_devint_regex,
                  "reply" : passing_dev_data
              }
          ]
       ),
       (
          {
              "config"      : all_config,
              "second_node" : False,
              "headline"    : "0  Test LTE Intf Stats           : \x1b[31m\x1b[01mFAIL  2 issues with 1/1 (cfg:1/1) interfaces\x1b[0m",
              "json_status" : 1
          },
          {
              "primary"   : prep_output_list({}, None, None),
              "secondary" : prep_output_list({}, None, None),
              "solitary"  : prep_output_list({}, None, None)
          },
          [
              {
                  "regex" : graphql_router_asset_regex,
                  "reply" : pytest_common.TestBase.router_info_reply_single
              },
              {
                  "regex" : graphql_devint_regex,
                  "reply" : passing_dev_data
              }
          ]
       )
    ]


    def setup(self):
        self.default_args(router="corp2", node="corp2A")
        sys.path.append(os.path.dirname(__file__))


    @pytest.mark.usefixtures("create_conductor_files")
    @pytest.mark.parametrize('test_instance,linux_run_output,requests_post_output', test_parameters)

    def test_ifconfig_stats(self, test_instance, local_context, graphql_url, capsys, mock_linux_run, mock_check_user, mock_requests_post):
        config = test_instance["config"]
        test_id = 0
        test = TestLteIfConfig.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(
            local_context, 
            self.args.router, 
            self.args)
        if test_instance["second_node"]:
            router_context.set_node(name="corp2B")
        #assert False, router_context.to_string()

        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()
        
        #assert False, pprint.pformat(all_lines)
        # until some real tests can be run...
        assert all_lines[3] == test_instance["headline"], '\n'.join(all_lines) + 'VS:\n' + test_instance['headline']


    @pytest.mark.usefixtures("create_conductor_files")
    @pytest.mark.parametrize('test_instance,linux_run_output,requests_post_output', test_parameters)

    def test_ifconfig_stats_json(self, test_instance, local_context, graphql_url, capsys, mock_linux_run, mock_check_user, mock_requests_post):
        config = test_instance["config"]
        config["OutputModule"] = "Json" 
        test_id = 0
        test = TestLteIfConfig.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(
            local_context, 
            self.args.router, 
            self.args)
        if test_instance["second_node"]:
            router_context.set_node(name="corp2B")

        test.run(local_context, router_context, None, fp=None)
        captured = capsys.readouterr()

        json_string = captured.out
        matches = re.search(r"(?sm)^\s+({.*}),", json_string)
        assert not matches is None
        json_string = matches.group(1)

        json_out = json.loads(json_string)
        assert json_out["fields"]["TestStatus"] == test_instance["json_status"] 
