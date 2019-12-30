#!/usr/bin/env python3.6
##########################################################################################
#   _            _       ____             _          ____  _        _                     
#  | |_ ___  ___| |_    |  _ \  _____   _(_) ___ ___/ ___|| |_ __ _| |_ ___   _ __  _   _ 
#  | __/ _ \/ __| __|   | | | |/ _ \ \ / / |/ __/ _ \___ \| __/ _` | __/ _ \ | '_ \| | | |
#  | ||  __/\__ \ |_    | |_| |  __/\ V /| | (_|  __/___) | || (_| | ||  __/_| |_) | |_| |
#   \__\___||___/\__|___|____/ \___| \_/ |_|\___\___|____/ \__\__,_|\__\___(_) .__/ \__, |
#                  |_____|                                                   |_|    |___/ 
#
##########################################################################################
import os
import sys

import argparse

import pprint
import json
import re

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
    from stage_check import TestDeviceState
except ImportError:
    import TestDeviceState   

class Test_DeviceState(pytest_common.TestBase):
    default_config = {
        "TestModule"   : "DeviceState",
        "OutputModule" : "Text",
        "Description"  : "NetworkDeviceStatus",
        "Parameters"   : {
           "exclude_tests" : [
               "name == 't1-backup'",
               "forwarding == False"
           ],
           "entry_tests" : {
               "no_match" : {
                   "status"  : "PASS"
               },
               "defaults" : {
                   "status"  : "FAIL",
                   "format"  : "Node {node_name} dev {name} is {state.operationalStatus}"
               },
               "tests" : [
                   { "test" : "state.operationalStatus == 'OPER_DOWN'" }
               ],
               "result": {
                   "PASS" : "All required network devices In Service",
                   "FAIL" : "{FAIL} required network devices are not LINK UP",
                   "WARN" : "Incorrect state for {WARN} device interfaces"
               }
           }
        }
    }

    states_config = {
        "TestModule"   : "DeviceState",
        "OutputModule" : "Text",
        "Description"  : "NetworkDeviceStatus",
        "Parameters"   : {
           "exclude_tests" : [
           ],
           "entry_tests" : {
               "no_match" : {
                   "status"  : "PASS"
               },
               "defaults" : {
                   "status"  : "FAIL",
                   "format"  : "Node {node_name} dev {name} is {state.operationalStatus}"
               },
               "tests" : [
                   { 
                       "test" : "name == 'PUBLIC_S' && (op_status == 'OPER_UP' || dStates.primary.PUBLIC_P.op_status == 'OPER_UP')",
                       "format" : "",
                       "status" : "PASS"
                   },
                   { 
                       "test" : "name == 'PUBLIC_P' && (op_status == 'OPER_UP' || dStates.secondary.PUBLIC_S.op_status == 'OPER_UP')",
                       "format" : "",
                       "status" : "PASS"
                   },
                   { "test" : "op_status != 'OPER_UP'" }
               ],
               "result": {
                   "PASS" : "All required network devices In Service",
                   "FAIL" : "{FAIL} required network devices are not LINK UP",
                   "WARN" : "Incorrect state for {WARN} device interfaces"
               }
           }
        }
    }

    peer_config = {
        "TestModule"   : "DeviceState",
        "OutputModule" : "Text",
        "Description"  : "NetworkDeviceStatus",
        "Parameters"   : {
           "exclude_tests" : [
           ],
           "entry_tests" : {
               "no_match" : {
                   "status"  : "PASS"
               },
               "defaults" : {
                   "status"  : "FAIL",
                   "format"  : "Node {node_name} dev {name} is {op_status}"
               },
               "tests" : [
                   { 
                     "test" : "name == 'PUBLIC' && (op_status == 'OPER_UP' || peer_op_status == 'OPER_UP')",
                     "format" : "",
                     "status" : "PASS"
                   },
                   { "test" : "op_status != 'OPER_UP'" }
               ],
               "result": {
                   "PASS" : "All required network devices In Service",
                   "FAIL" : "{FAIL} required network devices are not LINK UP",
                   "WARN" : "Incorrect state for {WARN} device interfaces"
               }
           }
        }
    }

    json_output = {
        "fields" : {
            "TestStatus" : 0
        },
        "name" : "TestDeviceState",
        "tags" : {
            "InvokingNode" : "Node",
            "InvokingRole" : "conductor",
            "InvokingRouter" : "cond1",
            "Router" : "corp2",
            "RouterIndex" : 1,
            "RouterIndexLast" : 1,
            "StageCheckVersion" : "1.0.0",
            "TestDescription" : "NetworkDeviceStatus",
            "TestIndex" : 0,
            "TestIndexLast" : 0,
            "TestVersion" : "0.0.0"
        },
        "timestamp" : 1111111111
    }

    test_parameters = [
    {
      "config" : default_config,
      "json_reply" : {
         'data':  {
             'allRouters': {
               'edges': [
                   {
                      'node':  {
                          'name': 'corp2',
                          'nodes': {
                             'edges': [
                                {
                                   'node': {
                                      'deviceInterfaces': {
                                           'edges': [
                                               {
                                                  'node': {
                                                      'name': 'PUBLIC_P',
                                                      'state': {
                                                          'operationalStatus': 'OPER_UP'
                                                       }
                                                    }
                                                 },
                                               {
                                                   'node': {
                                                       'name': 'WIRELESS_P',
                                                       'state': {
                                                           'operationalStatus': 'OPER_UP'
                                                       }
                                                     }
                                                }
                                             ]
                                        },
                                      'name': 'corp2A'
                                     }
                                  },
                                {
                                    'node': {
                                        'deviceInterfaces': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'name': 'PUBLIC_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP'
                                                       }
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'name': 'WIRELESS_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP'}
                                                    }
                                                }
                                            ]
                                        },
                                        'name': 'corp2B'}
                                }
                             ]
                            }
                        }
                     }
                 ]
               }
           }
        },
        "messages" : [ "0  NetworkDeviceStatus           : \x1b[32m\x1b[01mPASS\x1b[0m  All required network devices In Service" ],
        "json_status" : 0
      },
    {
      "config" : default_config,
      "json_reply" : {
          "errors": [
               {"locations": [{"column": 128, "line": 1}],
                "message": "Timeout has occurred",
                "path": ["allRouters",
                         "edges",
                          0,
                          "node",
                          "nodes",
                          "edges",
                          1,
                          "node",
                          "deviceInterfaces",
                          "edges",
                          0,
                          "node",
                          "state"]},
              {"locations": [{"column": 128, "line": 1}],
               "message": "Timeout has occurred",
               "path": ["allRouters",
                        "edges",
                        0,
                        "node",
                        "nodes",
                        "edges",
                        1,
                        "node",
                        "deviceInterfaces",
                        "edges",
                        1,
                        "node",
                        "state"]}],
         'data':  {
             'allRouters': {
               'edges': [
                   {
                      'node':  {
                          'name': 'corp2',
                          'nodes': {
                             'edges': [
                                {
                                   'node': {
                                      'deviceInterfaces': {
                                           'edges': [
                                               {
                                                  'node': {
                                                      'name': 'PUBLIC_P',
                                                      'state': {
                                                          'operationalStatus': 'OPER_UP'
                                                       }
                                                    }
                                                 },
                                               {
                                                   'node': {
                                                       'name': 'WIRELESS_P',
                                                       'state': {
                                                           'operationalStatus': 'OPER_UP'
                                                       }
                                                     }
                                                }
                                             ]
                                        },
                                      'name': 'corp2A'
                                     }
                                  },
                                {
                                    'node': {
                                        'deviceInterfaces': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'name': 'PUBLIC_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP'
                                                       }
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'name': 'WIRELESS_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP'}
                                                    }
                                                }
                                            ]
                                        },
                                        'name': 'corp2B'}
                                }
                             ]
                            }
                        }
                     }
                 ]
               }
           }
        },
        "messages" : [ "0  NetworkDeviceStatus           : \x1b[34m\x1b[01mWARN  All required network devices In Service\x1b[0m",
                       "   :                                     GQL[x2]: Timeout has occurred" ],
        "json_status" : 2
      },
    {
      "config" : default_config,
      "json_reply" : {
         'data':  {
             'allRouters': {
               'edges': [
                   {
                      'node':  {
                          'name': 'corp2',
                          'nodes': {
                             'edges': [
                                {
                                   'node': {
                                      'deviceInterfaces': {
                                           'edges': [
                                               {
                                                  'node': {
                                                      'name': 'PUBLIC_P',
                                                      'state': {
                                                          'operationalStatus': 'OPER_DOWN'
                                                       }
                                                    }
                                                 },
                                               {
                                                   'node': {
                                                       'name': 'WIRELESS_P',
                                                       'state': {
                                                           'operationalStatus': 'OPER_UP'
                                                       }
                                                     }
                                                }
                                             ]
                                        },
                                      'name': 'corp2A'
                                     }
                                  },
                                {
                                    'node': {
                                        'deviceInterfaces': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'name': 'PUBLIC_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_DOWN'
                                                        }
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'name': 'WIRELESS_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP'}
                                                    }
                                                }
                                            ]
                                        },
                                        'name': 'corp2B'}
                                }
                             ]
                            }
                        }
                     }
                 ]
               }
           }
        },
        "messages" : [ "0  NetworkDeviceStatus           : \x1b[31m\x1b[01mFAIL  2 required network devices are not LINK UP\x1b[0m",
                       "   :                                     Node corp2A dev PUBLIC_P is OPER_DOWN",
                       "   :                                     Node corp2B dev PUBLIC_S is OPER_DOWN" ],
        "json_status" : 1
      },
    {
      "config" : default_config,
      "json_reply" : {
         'data':  {
             'allRouters': {
               'edges': [
                   {
                      'node':  {
                          'name': 'corp2',
                          'nodes': {
                             'edges': [
                                {
                                   'node': {
                                      'deviceInterfaces': {
                                           'edges': [
                                               {
                                                  'node': {
                                                      'name': 'PUBLIC_P',
                                                      'forwarding' : False,
                                                      'state': {
                                                          'operationalStatus': 'OPER_DOWN'
                                                       }
                                                    }
                                                 },
                                               {
                                                   'node': {
                                                       'name': 'WIRELESS_P',
                                                       'state': {
                                                           'operationalStatus': 'OPER_UP'
                                                       },
                                                       'forwarding' : False
                                                     }
                                                }
                                             ]
                                        },
                                      'name': 'corp2A'
                                     }
                                  },
                                {
                                    'node': {
                                        'deviceInterfaces': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'name': 'PUBLIC_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_DOWN',
                                                            'forwarding' : False
                                                        }
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'name': 'WIRELESS_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP'}
                                                    }
                                                }
                                            ]
                                        },
                                        'name': 'corp2B'}
                                }
                             ]
                            }
                        }
                     }
                 ]
               }
           }
        },
        "messages" : [ "0  NetworkDeviceStatus           : \x1b[31m\x1b[01mFAIL  1 required network devices are not LINK UP\x1b[0m",
                       "   :                                     Node corp2B dev PUBLIC_S is OPER_DOWN" ],
        "json_status" : 1
      },
      {
        "config" : default_config,
        "json_reply" : {
          "errors": [
               {"locations": [{"column": 128, "line": 1}],
                "message": "Timeout has occurred",
                "path": ["allRouters",
                         "edges",
                          0,
                          "node",
                          "nodes",
                          "edges",
                          1,
                          "node",
                          "deviceInterfaces",
                          "edges",
                          0,
                          "node",
                          "state"]},
              {"locations": [{"column": 128, "line": 1}],
               "message": "Timeout has occurred",
               "path": ["allRouters",
                        "edges",
                        0,
                        "node",
                        "nodes",
                        "edges",
                        1,
                        "node",
                        "deviceInterfaces",
                        "edges",
                        1,
                        "node",
                        "state"]}],
          'data':  {
             'allRouters': {
               'edges': [
                   {
                      'node':  {
                          'name': 'corp2',
                          'nodes': {
                             'edges': [
                                {
                                   'node': {
                                      'deviceInterfaces': {
                                           'edges': [
                                               {
                                                  'node': {
                                                      'name': 'PUBLIC_P',
                                                      'forwarding' : False,
                                                      'state': {
                                                          'operationalStatus': 'OPER_DOWN'
                                                       }
                                                    }
                                                 },
                                               {
                                                   'node': {
                                                       'name': 'WIRELESS_P',
                                                       'state': {
                                                           'operationalStatus': 'OPER_UP'
                                                       },
                                                       'forwarding' : False
                                                     }
                                                }
                                             ]
                                        },
                                      'name': 'corp2A'
                                     }
                                  },
                                  {
                                    'node': {
                                        'deviceInterfaces': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'name': 'PUBLIC_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_DOWN',
                                                            'forwarding' : False
                                                        }
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'name': 'WIRELESS_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP'}
                                                    }
                                                }
                                            ]
                                        },
                                        'name': 'corp2B'}
                                   }
                                ] 
                            }
                        }
                     }
                  ]
               }
            }
         },
         "messages" : [ "0  NetworkDeviceStatus           : \x1b[31m\x1b[01mFAIL  1 required network devices are not LINK UP\x1b[0m",
                        "   :                                     GQL[x2]: Timeout has occurred",
                        "   :                                     Node corp2B dev PUBLIC_S is OPER_DOWN" ],
         "json_status" : 1
       },
    {
      "config" : states_config,
      "json_reply" : {
         'data':  {
             'allRouters': {
               'edges': [
                   {
                      'node':  {
                          'name': 'corp2',
                          'nodes': {
                             'edges': [
                                {
                                   'node': {
                                      'deviceInterfaces': {
                                           'edges': [
                                               {
                                                  'node': {
                                                      'name': 'PUBLIC_P',
                                                      'forwarding' : False,
                                                      'state': {
                                                          'operationalStatus': 'OPER_UP',
                                                          'adminStatus': 'ADMIN_UP',
                                                          'redundancyStatus': 'NONE'
                                                       }
                                                    }
                                                 },
                                               {
                                                   'node': {
                                                       'name': 'WIRELESS_P',
                                                       'state': {
                                                           'operationalStatus': 'OPER_DOWN',
                                                            'adminStatus': 'ADMIN_UP',
                                                            'redundancyStatus': 'NONE'
                                                       },
                                                       'forwarding' : False
                                                     }
                                                }
                                             ]
                                        },
                                      'name': 'corp2A'
                                     }
                                  },
                                {
                                    'node': {
                                        'deviceInterfaces': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'name': 'PUBLIC_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_DOWN',
                                                            'adminStatus': 'ADMIN_UP',
                                                            'redundancyStatus': 'NONE'
                                                         },
                                                         'forwarding' : False
                                                     }
                                                },
                                                {
                                                    'node': {
                                                        'name': 'WIRELESS_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP',
                                                            'adminStatus': 'ADMIN_UP',
                                                            'redundancyStatus': 'NONE'
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        'name': 'corp2B'}
                                }
                             ]
                            }
                        }
                     }
                 ]
               }
           }
        },
        "messages" : [ "0  NetworkDeviceStatus           : \x1b[31m\x1b[01mFAIL  1 required network devices are not LINK UP\x1b[0m",
                       "   :                                     Node corp2A dev WIRELESS_P is OPER_DOWN" ],
        "json_status" : 1
      },
    {
      "config" : peer_config,
      "json_reply" : {
         'data':  {
             'allRouters': {
               'edges': [
                   {
                      'node':  {
                          'name': 'corp2',
                          'nodes': {
                             'edges': [
                                {
                                   'node': {
                                      'deviceInterfaces': {
                                           'edges': [
                                               {
                                                  'node': {
                                                      'name': 'PUBLIC',
                                                      'forwarding' : False,
                                                      'state': {
                                                          'operationalStatus': 'OPER_UP',
                                                          'adminStatus': 'ADMIN_UP',
                                                          'redundancyStatus': 'NONE'
                                                       }
                                                    }
                                                 },
                                               {
                                                   'node': {
                                                       'name': 'WIRELESS_P',
                                                       'state': {
                                                           'operationalStatus': 'OPER_DOWN',
                                                            'adminStatus': 'ADMIN_UP',
                                                            'redundancyStatus': 'NONE'
                                                       },
                                                       'forwarding' : False
                                                     }
                                                }
                                             ]
                                        },
                                      'name': 'corp2A'
                                     }
                                  },
                                {
                                    'node': {
                                        'deviceInterfaces': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'name': 'PUBLIC',
                                                        'state': {
                                                            'operationalStatus': 'OPER_DOWN',
                                                            'adminStatus': 'ADMIN_UP',
                                                            'redundancyStatus': 'NONE',
                                                            'forwarding' : False
                                                        }
                                                    }
                                                },
                                                {
                                                    'node': {
                                                        'name': 'WIRELESS_S',
                                                        'state': {
                                                            'operationalStatus': 'OPER_UP',
                                                            'adminStatus': 'ADMIN_UP',
                                                            'redundancyStatus': 'NONE',
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        'name': 'corp2B'}
                                }
                             ]
                            }
                        }
                     }
                 ]
               }
           }
        },
        "messages" : [ "0  NetworkDeviceStatus           : \x1b[31m\x1b[01mFAIL  1 required network devices are not LINK UP\x1b[0m",
                       "   :                                     Node corp2A dev WIRELESS_P is OPER_DOWN" ],
        "json_status" : 1
        }
     ] 

    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance', test_parameters)

    def test_device_state(self, test_instance, local_context, graphql_url, capsys):
        test_id = 0
        test = TestDeviceState.create_instance(test_id, test_instance["config"], self.args)
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
            #assert count < len(test_messages), f'{count}: "' + line + '" == MISSING!'  
            assert line == test_messages[count]
            count += 1
        assert count == len(test_messages) 


    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance', test_parameters)

    def test_device_state_json(self, test_instance, local_context, graphql_url, capsys):
        test_id = 0
        json_config = test_instance["config"].copy()
        json_config["OutputModule"] = "Json"
        test = TestDeviceState.create_instance(test_id, json_config, self.args)
        test.create_output_instance()
        responses.add(responses.POST, graphql_url, json=test_instance["json_reply"], status=200)
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        json_string = captured.out
        matches = re.search(r"(?sm)^\s+({.*}),", json_string)
        assert not matches is None
        json_string = matches.group(1)
        #assert False, "'" + json_string + "'"

        json_out = json.loads(json_string)
        assert json_out["fields"]["TestStatus"] == test_instance["json_status"] 
        
