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

class MockResponse:
    def __init__(self, json_data={}, status=200):
        self.status_code = status
        self.json_data = json_data
        self.content = "TEST CONTENT"
        self.text = "TEST TEXT"

    def json(self):
        return self.json_data

# These global dictionaries are manipulated by paramtrized test data
JSON_NI_RESPONSE={}
JSON_PING_RESPONSE={}

@pytest.fixture
def mock_requests_post(monkeypatch):
    """
    Monkey patch requests.post and return a pseudo response
    object. Note that data returned depends on examination
    of the json graphql request

    TODO:  Find some way to parametrize this.
    """
    def mocked_post(uri, *args, **kwargs):
        global JSON_NI_RESPONSE
        global JSON_PING_RESPONSE
        try:
            json_string = kwargs["data"]
            json_data = json.loads(json_string)
            #pprint.pprint(json_data)
            query_string = json_data["query"]
            # This is ugly, but sufficient
            if re.match(re.escape("{allRouters"), query_string):
                return MockResponse(json_data=JSON_NI_RESPONSE)
            elif re.match(re.escape("{ping"), query_string):
                return MockResponse(json_data=JSON_PING_RESPONSE)
            else:
                return MockResponse()
        except TypeError:
            pass
        return MockResponse()                   
    monkeypatch.setattr(requests, 'post', mocked_post) 

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

    def setup(self):
        self.args = argparse.Namespace()
        self.args.debug = True
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
          "config"          : default_config,
          "json_ni_reply"   : default_ni_data,
          "json_ping_reply" : {
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
           },
           "message" : "0  Test Gateway Ping             : \x1b[32m\x1b[01mPASS\x1b[0m  NI DIA: 10/10 replies from 10.0.0.1; average latency 8.4ms"
       },
       {
          "config"          : default_config,
          "json_ni_reply"   : default_ni_data,
          "json_ping_reply" : {
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
           },
           "message" : "0  Test Gateway Ping             : \x1b[32m\x1b[01mPASS\x1b[0m  NI DIA: 10/10 replies from 10.0.0.1; average latency 8.4ms"
       },
       {
          "config"          : default_config,
          "json_ni_reply"   : default_ni_data,
          "json_ping_reply" : {
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
           },
           "message" : "0  Test Gateway Ping             : \x1b[31m\x1b[01mFAIL  NI DIA: 10/10 fails to 10.0.0.1; average latency 0.0ms\x1b[0m"
       },
       {
          "config"          : mode_auto_config,
          "json_ni_reply"   : default_ni_data,
          "json_ping_reply" : {
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
           },
           "message" : "0  Test Gateway Ping             : \x1b[32m\x1b[01mPASS\x1b[0m  NI DIA: 10/10 replies from 10.0.0.1; average latency 8.4ms"
       }
    ] 
   )

    def test_ping(self, test_instance, local_context, graphql_url, capsys, mock_requests_post):
        global JSON_NI_RESPONSE
        global JSON_PING_RESPONSE
        JSON_NI_RESPONSE = test_instance["json_ni_reply"]
        JSON_PING_RESPONSE = test_instance["json_ping_reply"]
        test_id = 0
        config = test_instance["config"]
        test = TestGatewayPing.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()
        
        if self.args.debug == False:
            # Match Progress strings 
            max_count = config["Parameters"]["iterations"]
            cur_it = 0
            cur_index = 2
            while cur_it < max_count:
                progress_str = f"0  Test Gateway Ping             :       NI DIA: ping 10.0.0.1 {cur_it}/{max_count} tmo=2s"
                assert all_lines[cur_index] == progress_str
                cur_it += 1
                cur_index += 1
            cur_index += 1   
            assert len(all_lines[cur_index]) == len(test_instance["message"]) 
            assert all_lines[cur_index] == test_instance["message"]
        else:
            lc = 0
            for line in all_lines:
                print(f"{lc}: {line}")
                lc += 1


        
