#!/usr/bin/env python3.6
###################################################################################################
#   _            _       ____       _                           ____  _                           
#  | |_ ___  ___| |_    / ___| __ _| |_ _____      ____ _ _   _|  _ \(_)_ __   __ _   _ __  _   _ 
#  | __/ _ \/ __| __|  | |  _ / _` | __/ _ \ \ /\ / / _` | | | | |_) | | '_ \ / _` | | '_ \| | | |
#  | ||  __/\__ \ |_   | |_| | (_| | ||  __/\ V  V / (_| | |_| |  __/| | | | | (_| |_| |_) | |_| |
#   \__\___||___/\__|___\____|\__,_|\__\___| \_/\_/ \__,_|\__, |_|   |_|_| |_|\__, (_) .__/ \__, |
#                  |_____|                                |___/               |___/  |_|    |___/ 
#
###################################################################################################
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
    from stage_check import RouterContext
except ImportError:
    import RouterContext

try:
    from stage_check import TestGatewayPing
except ImportError:
    import TestGatewayPing   

class Test_GatewayPing(pytest_common.TestBase):
    default_ni_data = {
        'data': {
            'allRouters': {
            'edges': [
               {
                  'node': {
                      'name': 'SITE0001P1',
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
                                                           'networkInterfaces': {'edges': []},
                                                           'sharedPhysAddress': None,
                                                           'state': {'operationalStatus': None}
                                                      }
                                                },
                                                {
                                                     'node': {
                                                           'name': '2',
                                                           'networkInterfaces': {'edges': []},
                                                           'sharedPhysAddress': None,
                                                           'state': {'operationalStatus': 'OPER_UP'}
                                                      }
                                                },
                                                {
                                                     'node': {
                                                          'name': '3',
                                                          'networkInterfaces': {'edges': []},
                                                          'sharedPhysAddress': 'aa:aa:aa:aa:aa:01',
                                                          'state': {'operationalStatus': 'OPER_UP'}
                                                     }
                                                },
                                                {
                                                     'node': {
                                                          'name': '4',
                                                          'networkInterfaces': {
                                                               'edges': [
                                                                    {
                                                                        'node': {
                                                                             'addresses': {'edges': []},
                                                                             'name': 'DIA',
                                                                             'state': {
                                                                                 'addresses': [
                                                                                      {
                                                                                          'gateway': '10.0.0.1',
                                                                                          'ipAddress': '10.0.0.2',
                                                                                          'prefixLength': 24
                                                                                      }
                                                                                  ]
                                                                              }
                                                                         }
                                                                    }
                                                               ]
                                                          },
                                                          'sharedPhysAddress': 'aa:aa:aa:aa:aa:02',
                                                          'state': {'operationalStatus': 'OPER_UP'}
                                                     }
                                                },
                                                {
                                                    'node': {
                                                        'name': '5',
                                                        'networkInterfaces': { 'edges': []},
                                                        'sharedPhysAddress': None,
                                                        'state': {'operationalStatus': 'OPER_UP'}
                                                     }
                                                }
                                           ]
                                      },
                                      'name': 'SITE00001P1A'
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
                                                        'networkInterfaces': {'edges': []},
                                                        'sharedPhysAddress': None,
                                                        'state': {'operationalStatus': None}
                                                    }
                                               },
                                               {
                                                   'node': {
                                                        'name': '2',
                                                        'networkInterfaces': {'edges': []},
                                                        'sharedPhysAddress': None,
                                                        'state': {'operationalStatus': 'OPER_UP'}
                                                    }
                                               },
                                               {
                                                    'node': {
                                                        'name': '3',
                                                        'networkInterfaces': {'edges': []},
                                                        'sharedPhysAddress': 'aa:aa:aa:aa:aa:01',
                                                        'state': {'operationalStatus': 'OPER_UP'}
                                                    }
                                               },
                                               {
                                                    'node': {
                                                        'name': '4',
                                                        'networkInterfaces': {
                                                            'edges': [
                                                                 {
                                                                     'node': {
                                                                          'addresses': {'edges': []},
                                                                          'name': 'DIA',
                                                                          'state': None
                                                                      }
                                                                 }
                                                             ]
                                                        },
                                                        'sharedPhysAddress': 'aa:aa:aa:aa:aa:02',
                                                        'state': {'operationalStatus': 'OPER_DOWN'}
                                                    }
                                               },
                                               {
                                                    'node': {
                                                        'name': '5',
                                                        'networkInterfaces': {'edges': []},
                                                        'sharedPhysAddress': None,
                                                        'state': {'operationalStatus': 'OPER_UP'}
                                                    }
                                               }
                                          ]
                                    },
                                    'name': 'SITE0001P1B'
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
        "TestModule"   : "GatewayPing",
        "OutputModule" : "Text",
        "Description"  : "Test Gateway Ping",
        "Parameters"   : {
            "node_type"          : "primary",
            "network-interfaces" : [ 
                "DIA" 
            ],
            "static-address"     : False,
            "iterations"         : 10
        }
    }

    mode_dynamic_config = {
        "TestModule"   : "GatewayPing",
        "OutputModule" : "Text",
        "Description"  : "Test Gateway Ping",
        "Parameters"   : {
            "node_type"          : "primary",
            "network-interfaces" : [ 
                "DIA" 
            ],
            "address_type"       : "dynamic",
            "iterations"         : 10
        }
    }

    mode_static_config = {
        "TestModule"   : "GatewayPing",
        "OutputModule" : "Text",
        "Description"  : "Test Gateway Ping",
        "Parameters"   : {
            "node_type"          : "primary",
            "network-interfaces" : [ 
                "DIA" 
            ],
            "address_type"       : "static",
            "iterations"         : 10
        }
    }

    mode_auto_config = {
        "TestModule"   : "GatewayPing",
        "OutputModule" : "Text",
        "Description"  : "Test Gateway Ping",
        "Parameters"   : {
            "node_type"          : "primary",
            "network-interfaces" : [ 
                "DIA" 
            ],
            "address_type"       : "auto",
            "iterations"         : 10
        }
    }

    latency_config = {
        "TestModule"   : "GatewayPing",
        "OutputModule" : "Text",
        "Description"  : "Test Gateway Ping",
        "Parameters"   : {
            "node_type"          : "primary",
            "network-interfaces" : [ 
                "DIA" 
            ],
            "address_type"              : "dynamic",
            "iterations"                : 10,
            "max_response_overages"     : 1,
            "max_single_response_time"  : 50.0,
            "max_average_response_time" : 25.0
        }
    }

    secondary_config = {
        "TestModule"   : "GatewayPing",
        "OutputModule" : "Text",
        "Description"  : "Test Gateway Ping",
        "Parameters"   : {
            "node_type"          : "secondary",
            "network-interfaces" : [
                "DIA"
            ],
            "static-address"     : False,
            "iterations"         : 10
        }
     }

    # Given that currently the same graphql reply is mocked regardless of
    # homw many times the mock is called, iterate once, return failure
    # but allow 1 failure which should resut in SUCCESS.
    ok_max_ping_failures_config = {
        "TestModule"   : "GatewayPing",
        "OutputModule" : "Text",
        "Description"  : "Test Gateway Ping",
        "Parameters"   : {
            "node_type"          : "primary",
            "network-interfaces" : [ 
                "DIA" 
            ],
            "static-address"     : False,
            "iterations"         : 1,
            "max_ping_failures"  : 1
        }
    }

    # somewhat contrived; see comment for ok_max_ping_failures..
    max_ping_failures_config = {
        "TestModule"   : "GatewayPing",
        "OutputModule" : "Text",
        "Description"  : "Test Gateway Ping",
        "Parameters"   : {
            "node_type"          : "primary",
            "network-interfaces" : [ 
                "DIA" 
            ],
            "static-address"     : False,
            "iterations"         : 1,
            "max_ping_failures"  : 0
        }
    }

    warn_config = {
        "TestModule"   : "GatewayPing",
        "OutputModule" : "Text",
        "Description"  : "Test Gateway Ping",
        "Parameters"   : {
            "node_type"          : "primary",
            "network-interfaces" : [ 
                "DIA" 
            ],
            "static-address"     : False,
            "iterations"         : 10,
            "fail_status"        : "WARN"
        }
    }

    test_parameters = [
       (
           {
               "config"          : default_config,
               "message" : "0  Test Gateway Ping             : \x1b[32m\x1b[01mPASS\x1b[0m  NI DIA: 10/10 replies from 10.0.0.1; average latency 8.44ms",
               "json_status" : 0
           },
           [
               {
                   "regex" : r"{allRouters", 
                   "reply" : default_ni_data
               },
               {
                   "regex" : r"{ping", 
                   "reply" : {
                       'data': {
                            'ping': {
                                'reachable': True,
                                'responseTime': '8.443',
                                'sequence': 1,
                                'status': '0',
                                'statusReason': '',
                                'ttl': 255
                             }
                        }
                    }
                }
            ]
        ),
        (
            {
               "config"          : default_config,
               "message" : "0  Test Gateway Ping             : \x1b[32m\x1b[01mPASS\x1b[0m  NI DIA: 10/10 replies from 10.0.0.1; average latency 8.44ms",
               "json_status" : 0
           },
           [ 
               {
                   "regex" : r"{allRouters", 
                   "reply" : default_ni_data
               },
               {
                   "regex" : r"{ping", 
                   "reply" : {
                       'data': {
                           'ping': {
                               'reachable': True,
                               'responseTime': '8.443',
                               'sequence': 1,
                               'status': 'SUCCESS',
                               'statusReason': '',
                               'ttl': 255
                            }
                        }
                    }
                }
            ]
       ),
       (
          {
               "config"          : default_config,
               "message" : "0  Test Gateway Ping             : \x1b[31m\x1b[01mFAIL  NI DIA: 10/10 fails to 10.0.0.1; average latency 0.00ms\x1b[0m",
               "json_status" : 1
          },
          [
              {                   
                  "regex" : r"{allRouters", 
                  "reply" : default_ni_data
              },
              {
                  "regex" : r"{ping", 
                  "reply" : {
                      'data': {
                           'ping': {
                               'reachable': False,
                               'responseTime': '0',
                               'sequence': 1,
                               'status': 'SUCCESS',
                               'statusReason': '',
                               'ttl': 255
                            }
                       }
                   }
              }
          ]
       ),
       (
           {
               "config"          : mode_auto_config,
               "message" : "0  Test Gateway Ping             : \x1b[32m\x1b[01mPASS\x1b[0m  NI DIA: 10/10 replies from 10.0.0.1; average latency 8.44ms",
               "json_status" : 0
           },
           [
              {                   
                  "regex" : r"{allRouters", 
                  "reply" : default_ni_data
              },
              {
                  "regex" : r"{ping", 
                  "reply" : {
                      'data': {
                          'ping': {
                              'reachable': True,
                              'responseTime': '8.443',
                              'sequence': 1,
                              'status': 'SUCCESS',
                              'statusReason': '',
                              'ttl': 255
                           }
                       }
                   }
               }
           ]
        ),
       (
           {
               "config"          : secondary_config,
               "test-info-lines" : False,
               "message"         : "0  Test Gateway Ping             : \x1b[31m\x1b[01mFAIL  Cannot ping via NI DIA, device status: OPER_DOWN\x1b[0m",
               "json_status"     : 1
           },
           [
              {                   
                  "regex" : r"{allRouters", 
                  "reply" : default_ni_data
              },
              {
                  "regex" : r"{ping", 
                  "reply" : {
                      'data': {
                          'ping': {
                              'reachable': True,
                              'responseTime': '8.443',
                              'sequence': 1,
                              'status': 'SUCCESS',
                              'statusReason': '',
                              'ttl': 255
                           }
                       }
                   }
               }
           ]
        ),
       (
           {
               "config"  : ok_max_ping_failures_config,
               "message"  : "0  Test Gateway Ping             : \x1b[32m\x1b[01mPASS\x1b[0m  NI DIA: 0/1 replies from 10.0.0.1; average latency 0.00ms",
               "json_status" : 0
           },
           [
               {
                   "regex" : r"{allRouters", 
                   "reply" : default_ni_data
               },
               {
                   "regex" : r"{ping", 
                   "reply" : {
                       'data': {
                            'ping': {
                                'reachable': False,
                                'responseTime': '8.443',
                                'sequence': 1,
                                'status': '0',
                                'statusReason': '',
                                'ttl': 255
                             }
                        }
                    }
                }
            ]
        ),
       (
           {
               "config"  : max_ping_failures_config,
               "message" : "0  Test Gateway Ping             : \x1b[31m\x1b[01mFAIL  NI DIA: 1/1 fails to 10.0.0.1; average latency 0.00ms\x1b[0m",
               "json_status" : 1
           },
           [
               {
                   "regex" : r"{allRouters", 
                   "reply" : default_ni_data
               },
               {
                   "regex" : r"{ping", 
                   "reply" : {
                       'data': {
                            'ping': {
                                'reachable': False,
                                'responseTime': '8.443',
                                'sequence': 1,
                                'status': '0',
                                'statusReason': '',
                                'ttl': 255
                             }
                        }
                    }
                }
            ]
        ),
        (
           {
               "config"          : default_config,
               "message" : "0  Test Gateway Ping             : \x1b[31m\x1b[01mFAIL  Issues detected for 1/1 interfaces (0 excluded)\x1b[0m",
               "json_status" : 1
           },
           [
              {                   
                  "regex" : r"{allRouters", 
                  "reply" : default_ni_data
              },
              {
                  "regex" : r"{ping", 
                  "reply" : {
                      'data': {
                           'ping': {
                               'responseTime': '0',
                               'ttl': 255
                            }
                       }
                   }
              }
           ]
        ),
        (
           {
               "config"      : warn_config,
               "message" : "0  Test Gateway Ping             : \x1b[34m\x1b[01mWARN  Issues detected for 1/1 interfaces (0 excluded)\x1b[0m",
               "json_status" : 2
           },
           [
              {                   
                  "regex" : r"{allRouters", 
                  "reply" : default_ni_data
              },
              {
                  "regex" : r"{ping", 
                  "reply" : {
                      'data': {
                           'ping': {
                               'responseTime': '0',
                               'ttl': 255
                            }
                       }
                   }
              }
           ]
        )
    ]

    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))


    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance,requests_post_output', test_parameters)

    def test_ping(self, test_instance, local_context, graphql_url, capsys, mock_requests_post):
        check_prog_lines = True
        if "test-info-lines" in test_instance:
            check_prog_lines = bool(test_instance["test-info-lines"])
        test_id = 0
        config = test_instance["config"]
        test = TestGatewayPing.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()
        
        if self.args.debug == False:
            #assert False, pprint.pformat(all_lines)
            # Match Progress strings 
            max_count = config["Parameters"]["iterations"]
            cur_it = 0
            cur_index = 2
            count=0
            if check_prog_lines:
                while cur_it < max_count:
                    progress_str = f"0  Test Gateway Ping             :       NI DIA: ping 10.0.0.1 {cur_it}/{max_count} tmo=2s"
                    assert all_lines[cur_index] == progress_str
                    cur_it += 1
                    cur_index += 1
                cur_index += 1
            else:
               cur_index = -1
            #assert False, pprint.pformat(all_lines) 
            #assert len(all_lines[cur_index]) == len(test_instance["message"])
            assert all_lines[cur_index] == test_instance["message"]
        else:
            lc = 0
            for line in all_lines:
                print(f"{lc}: {line}")
                lc += 1


    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance,requests_post_output', test_parameters)

    def test_ping_json(self, test_instance, local_context, graphql_url, capsys, mock_requests_post):
        test_id = 0
        config = test_instance["config"]
        config["OutputModule"] = "Json"
        test = TestGatewayPing.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)

        test.run(local_context, router_context, None, fp=None)
        captured = capsys.readouterr()

        json_string = captured.out
        matches = re.search(r"(?sm)^\s+({.*}),", json_string)
        assert not matches is None
        json_string = matches.group(1)

        json_out = json.loads(json_string)
        assert json_out["fields"]["TestStatus"] == test_instance["json_status"] 

        
