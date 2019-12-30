#!/usr/bin/env python3.6
#################################################################################
#   _            _       ____                _                               
#  | |_ ___  ___| |_    / ___|  ___  ___ ___(_) ___  _ __  ___   _ __  _   _ 
#  | __/ _ \/ __| __|   \___ \ / _ \/ __/ __| |/ _ \| '_ \/ __| | '_ \| | | |
#  | ||  __/\__ \ |_     ___) |  __/\__ \__ \ | (_) | | | \__ \_| |_) | |_| |
#   \__\___||___/\__|___|____/ \___||___/___/_|\___/|_| |_|___(_) .__/ \__, |
#                  |_____|                                      |_|    |___/ 
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
    from stage_check import TestSessions
except ImportError:
    import TestSessions

class Test_Sessions(pytest_common.TestBase):
    config = {
        "TestModule"   : "Sessions",
        "OutputModule" : "Text",
        "Description"  : "Check Inactive Sessions",
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
                         "test"   : "inactivityTimeout > 0 && 3600 - inactivityTimeout > 400", 
                         "format" : "session {sessionUuid} idle {test_idle_duration}s",
	   	         "status" : "FAIL"
                     }
                ],
                "result"    : {
                    "PASS"  : "{session_flow_count}/{session_flow_count} port {filter_string} sessions have idle times < {idle_threshold_seconds}s ({total_count} flows processed)",
                    "FAIL"  : "{match_count}/{session_flow_count} port {filter_string} sessions idle > {idle_threshold_seconds}s ({total_count} flows processed)"
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
                                        'flowEntries': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'destIp': '198.168.0.2',
                                                        'destPort': 5060,
                                                        'deviceInterfaceName': '3',
                                                        'devicePort': 3,
                                                        'encrypted': True,
                                                        'forward': True,
                                                        'inactivityTimeout': 3540,
                                                        'natIp': '0.0.0.0',
                                                        'natPort': 0,
                                                        'networkInterfaceName': 'voice',
                                                        'protocol': 'UDP',
                                                        'serviceName': 'voice',
                                                        'sessionUuid': '04be7d06-53ae-4f1a-9ee0-ebd48c95656a',
                                                        'sourceIp': '10.0.1.1',
                                                        'sourcePort': 5060,
                                                        'startTime': 1576000000,
                                                        'tenant': 'voice.users',
                                                        'vlan': 3
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'destIp': '192.168.0.3',
                                                        'destPort': 16384,
                                                        'deviceInterfaceName': '2',
                                                        'devicePort': 2,
                                                        'encrypted': True,
                                                        'forward': False,
                                                        'inactivityTimeout': 3540,
                                                        'natIp': '0.0.0.0',
                                                        'natPort': 0,
                                                        'networkInterfaceName': 'ha-fabric',
                                                        'protocol': 'UDP',
                                                        'serviceName': 'voice',
                                                        'sessionUuid': '04be7d06-53ae-4f1a-9ee0-ebd48c95656a',
                                                        'sourceIp': '10.0.1.3',
                                                        'sourcePort': 16385,
                                                        'startTime': 1576000000,
                                                        'tenant': 'voice.users',
                                                        'vlan': 0
                                                    }
                                                }
                                            ]
                                        },
                                         'name': 'SITE0002P1A'
                                     }
                                 },
                                  {
                                      'node': {
                                          'flowEntries': {
                                              'edges': []
                                          },
                                          'name': 'SITE00002P1B'
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
        "messages" : [ "0  Check Inactive Sessions       : \x1b[32m\x1b[01mPASS\x1b[0m  1/1 port 5060 sessions have idle times < 400s (2 flows processed)" ]
      },
      {
        "json_reply" : {
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
                                        'flowEntries': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'destIp': '192.168.0.2',
                                                        'destPort': 5060,
                                                        'deviceInterfaceName': '3',
                                                        'devicePort': 3,
                                                        'encrypted': True,
                                                        'forward': True,
                                                        'inactivityTimeout': 3540,
                                                        'natIp': '0.0.0.0',
                                                        'natPort': 0,
                                                        'networkInterfaceName': 'voice',
                                                        'protocol': 'UDP',
                                                        'serviceName': 'voice',
                                                        'sessionUuid': '04be7d06-53ae-4f1a-9ee0-ebd48c95656a',
                                                        'sourceIp': '10.0.1.1',
                                                        'sourcePort': 5060,
                                                        'startTime': 1576000000,
                                                        'tenant': 'voice.users',
                                                        'vlan': 3
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'destIp': '192.168.0.3',
                                                        'destPort': 5060,
                                                        'deviceInterfaceName': '2',
                                                        'devicePort': 2,
                                                        'encrypted': True,
                                                        'forward': False,
                                                        'inactivityTimeout': 1200,
                                                        'natIp': '0.0.0.0',
                                                        'natPort': 0,
                                                        'networkInterfaceName': 'ha-fabric',
                                                        'protocol': 'UDP',
                                                        'serviceName': 'voice',
                                                        'sessionUuid': '04be7d06-53ae-4f1a-9ee0-ebd48c95656a',
                                                        'sourceIp': '10.0.1.3',
                                                        'sourcePort': 5060,
                                                        'startTime': 1576000000,
                                                        'tenant': 'voice.users',
                                                        'vlan': 0
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'destIp': '192.168.0.3',
                                                        'destPort': 5060,
                                                        'deviceInterfaceName': '2',
                                                        'devicePort': 2,
                                                        'encrypted': True,
                                                        'forward': False,
                                                        'inactivityTimeout': 1200,
                                                        'natIp': '0.0.0.0',
                                                        'natPort': 0,
                                                        'networkInterfaceName': 'ha-fabric',
                                                        'protocol': 'UDP',
                                                        'serviceName': 'voice',
                                                        'sessionUuid': '04be7d06-53ae-4f1a-9ee0-ebd48c956bbb',
                                                        'sourceIp': '10.0.1.3',
                                                        'sourcePort': 5060,
                                                        'startTime': 1576000000,
                                                        'tenant': 'voice.users',
                                                        'vlan': 0
                                                    }
                                                }
                                            ]
                                        },
                                         'name': 'SITE0002P1A'
                                     }
                                 },
                                  {
                                      'node': {
                                          'flowEntries': {
                                              'edges': []
                                          },
                                          'name': 'SITE00002P1B'
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
        "messages" : [ "0  Check Inactive Sessions       : \x1b[31m\x1b[01mFAIL  2/2 port 5060 sessions idle > 400s (3 flows processed)\x1b[0m",
                       "   :                                     session 04be7d06-53ae-4f1a-9ee0-ebd48c95656a idle 2400s",
                       "   :                                     session 04be7d06-53ae-4f1a-9ee0-ebd48c956bbb idle 2400s" ]
      },
      {
        "json_reply" : {
           'data': {
              'allRouters': {
                 'edges': [
                    {
                       'node': {
                           'name': 'SITE0001P6',
                           'nodes': {
                              'edges': [
                                 {
                                     'node': {
                                        'flowEntries': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'destIp': '192.168.0.2',
                                                        'destPort': 5060,
                                                        'deviceInterfaceName': '3',
                                                        'devicePort': 3,
                                                        'encrypted': True,
                                                        'forward': True,
                                                        'inactivityTimeout': 3540,
                                                        'natIp': '0.0.0.0',
                                                        'natPort': 0,
                                                        'networkInterfaceName': 'voice',
                                                        'protocol': 'UDP',
                                                        'serviceName': 'voice',
                                                        'sessionUuid': '04be7d06-53ae-4f1a-9ee0-ebd48c95656a',
                                                        'sourceIp': '10.0.1.1',
                                                        'sourcePort': 5060,
                                                        'startTime': 1576000000,
                                                        'tenant': 'voice.users',
                                                        'vlan': 3
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'destIp': '192.168.0.3',
                                                        'destPort': 16384,
                                                        'deviceInterfaceName': '2',
                                                        'devicePort': 2,
                                                        'encrypted': True,
                                                        'forward': False,
                                                        'inactivityTimeout': 3540,
                                                        'natIp': '0.0.0.0',
                                                        'natPort': 0,
                                                        'networkInterfaceName': 'ha-fabric',
                                                        'protocol': 'UDP',
                                                        'serviceName': 'voice',
                                                        'sessionUuid': '04be7d06-53ae-4f1a-9ee0-ebd48c95656a',
                                                        'sourceIp': '10.0.1.3',
                                                        'sourcePort': 16385,
                                                        'startTime': 1576000000,
                                                        'tenant': 'voice.users',
                                                        'vlan': 0
                                                    }
                                                },
                                                {
                                                    'node' : None
                                                },
                                                None
                                            ]
                                        },
                                         'name': 'SITE0002P1A'
                                     }
                                 },
                                  {
                                      'node': {
                                          'flowEntries': {
                                              'edges': []
                                          },
                                          'name': 'SITE00002P1B'
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
        "messages" : [ "0  Check Inactive Sessions       : \x1b[32m\x1b[01mPASS\x1b[0m  1/1 port 5060 sessions have idle times < 400s (4 flows processed)" ]
      }
    ]
   )

    def test_run_on_cond(self, test_instance, local_context, graphql_url, capsys):
        test_id = 0
        test = TestSessions.create_instance(test_id, Test_Sessions.config, self.args)
        test.create_output_instance()

        responses.add(responses.POST, graphql_url, json=pytest_common.assets, status=200)
        router_context = RouterContext.create_instance(local_context, "SITE0001P1", self.args, 
                                                       pytest_common.assets[0])
        router_context.set_node(asset_json=pytest_common.assets[1])

        # Note if test.run uses more than one call to the graphql API, responses.remove()
        # and responses.add() cannot properly satisfy different requests to the same url
        responses.remove(responses.POST, graphql_url)
        responses.add(responses.POST, graphql_url, json=test_instance["json_reply"], status=200)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()

        count = 0
        test_messages = test_instance["messages"]
        for line in all_lines:
            #assert count < len(test_messages), f'{count}: "' + line + '" == MISSING!' 
            assert line == test_messages[count]
            count += 1
        assert count == len(test_messages)
        
