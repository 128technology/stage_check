####################################################################################
#   _            _                  _     _          _                             
#  | |_ ___  ___| |_     __ _  __ _| |   | |__   ___| |_ __   ___ _ __ _ __  _   _ 
#  | __/ _ \/ __| __|   / _` |/ _` | |   | '_ \ / _ \ | '_ \ / _ \ '__| '_ \| | | |
#  | ||  __/\__ \ |_   | (_| | (_| | |   | | | |  __/ | |_) |  __/ | _| |_) | |_| |
#   \__\___||___/\__|___\__, |\__, |_|___|_| |_|\___|_| .__/ \___|_|(_) .__/ \__, |
#                  |_____| |_|   |_||_____|           |_|             |_|    |___/ 
# 
####################################################################################

import pprint

import pytest 

import pytest_common
import gql_helper

class TestGqlHelper(pytest_common.TestBase):
    unflattened_json_1 = {
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
                                              'assetId': 'LR000000000001',
                                              'deviceInterfaces': {
                                                  'edges': [
                                                       {
                                                           'node': {
                                                                'name': 'one',
                                                                'networkInterfaces': {
                                                                    'edges': [
                                                                        {
                                                                            'node': {
                                                                                'addresses': {
                                                                                    'edges': [
                                                                                        {
                                                                                            'node': {
                                                                                                'gateway': '169.254.1.1',
                                                                                                'ipAddress': '169.254.1.2',
                                                                                                'prefixLength': 30
                                                                                            }}]},
                                                                                'name': 'alpha',
                                                                                'state': None
                                                                            }}]},
                                                               'sharedPhysAddress': None,
                                                               'state': {
                                                                   'operationalStatus': 'OPER_UP'
                                                               }}},
                                                      {
                                                          'node': {
                                                              'name': 'two',
                                                              'networkInterfaces': {
                                                                  'edges': [
                                                                      {
                                                                          'node': {
                                                                              'addresses': {
                                                                                  'edges': [
                                                                                      {
                                                                                          'node': {
                                                                                              'gateway': None,
                                                                                              'ipAddress': '169.254.2.2',
                                                                                              'prefixLength': 25
                                                                                          }}]},
                                                                              'name': 'beta',
                                                                              'state': {
                                                                                  'addresses': [
                                                                                      {
                                                                                          'gateway': '<empty>',
                                                                                          'ipAddress': '<empty>',
                                                                                          'prefixLength': 0
                                                                                      }]}}},
                                                                      {
                                                                          'node': {
                                                                              'addresses': {
                                                                                  'edges': [
                                                                                      {
                                                                                          'node': {
                                                                                              'gateway': None,
                                                                                              'ipAddress': '169.254.3.2',
                                                                                              'prefixLength': 27}}]},
                                                                              'name': 'gamma',
                                                                              'state': {
                                                                                  'addresses': [
                                                                                      {
                                                                                          'gateway': '<empty>',
                                                                                          'ipAddress': '<empty>',
                                                                                          'prefixLength': 0
                                                                                      }]}}},
                                                                      
                                                                      {
                                                                          'node': {
                                                                              'addresses': {
                                                                                  'edges': [
                                                                                      {
                                                                                          'node': {
                                                                                              'gateway': None,
                                                                                              'ipAddress': '169.254.4.2',
                                                                                              'prefixLength': 27
                                                                                          }}]},
                                                                              'name': 'delta',
                                                                              'state': {
                                                                                  'addresses': [
                                                                                      {
                                                                                          'gateway': '<empty>',
                                                                                          'ipAddress': '<empty>',
                                                                                          'prefixLength': 0
                                                                                      }]}}}]},
                                                              'sharedPhysAddress': '00:01:02:03:04:05',
                                                              'state': {
                                                                  'operationalStatus': 'OPER_UP'}}},
                                                      {
                                                          'node': {
                                                              'name': 'three',
                                                              'networkInterfaces': {
                                                                  'edges': [
                                                                      {
                                                                          'node': {
                                                                              'addresses': {
                                                                                  'edges': []
                                                                              },
                                                                              'name': 'epsilon',
                                                                              'state': {
                                                                                  'addresses': [
                                                                                      {
                                                                                          'gateway': '169.254.5.1',
                                                                                          'ipAddress': '169.254.5.2',
                                                                                          'prefixLength': 23
                                                                                      }]}}}]},
                                                              'sharedPhysAddress': '06:07:08:09:0a:0b',
                                                              'state': {
                                                                  'operationalStatus': 'OPER_UP'
                                                              }}},
                                                      {
                                                          'node': {
                                                              'name': 'four',
                                                              'networkInterfaces': {
                                                                  'edges': [
                                                                      {
                                                                          'node': {
                                                                              'addresses': {
                                                                                  'edges': [
                                                                                      {
                                                                                          'node': {
                                                                                              'gateway': '169.254.6.1',
                                                                                              'ipAddress': '169.254.6.2',
                                                                                              'prefixLength': 31}}]},
                                                                              'name': 'zeta',
                                                                              'state': {
                                                                                  'addresses': [
                                                                                      {
                                                                                          'gateway': '<empty>',
                                                                                          'ipAddress': '<empty>',
                                                                                          'prefixLength': 0
                                                                                      }]}}}]},
                                                              'sharedPhysAddress': None,
                                                              'state': {
                                                                  'operationalStatus': 'OPER_UP'
                                                              }}},
                                                      {
                                                          'node': {
                                                              'name': 'five',
                                                              'networkInterfaces': {
                                                                  'edges': [
                                                                      {
                                                                          'node': {
                                                                              'addresses': {
                                                                                  'edges': [
                                                                                      {
                                                                                          'node': {
                                                                                              'gateway': None,
                                                                                              'ipAddress': '169.254.7.2',
                                                                                              'prefixLength': 30
                                                                                          }}]},
                                                                              'name': 'theta',
                                                                              'state': {
                                                                                  'addresses': [
                                                                                      {
                                                                                          'gateway': '<empty>',
                                                                                          'ipAddress': '<empty>',
                                                                                          'prefixLength': 0
                                                                                      }]}}}]},
                                                              'sharedPhysAddress': None,
                                                              'state': {
                                                                  'operationalStatus': 'OPER_UNKNOWN'
                                                              }}}]},
                                             'name': 'SITE0001P1A'
                                         }},
                                    {
                                        'node': {
                                            'assetId': 'LR000000000002',
                                            'deviceInterfaces': {
                                                'edges': [
                                                    {
                                                        'node': {
                                                            'name': 'one',
                                                            'networkInterfaces': {
                                                                'edges': [
                                                                    {
                                                                        'node': {
                                                                            'addresses': {
                                                                                'edges': [
                                                                                    {
                                                                                        'node': {
                                                                                            'gateway': '169.254.1.1',
                                                                                            'ipAddress': '169.254.1.2',
                                                                                            'prefixLength': 30
                                                                                        }}]},
                                                                            'name': 'alpha',
                                                                            'state': None
                                                                        }}]},
                                                            'sharedPhysAddress': None,
                                                            'state': {
                                                                'operationalStatus': 'OPER_UP'
                                                            }}},
                                                    {
                                                        'node': {
                                                            'name': 'two',
                                                            'networkInterfaces': {
                                                                'edges': [
                                                                    {
                                                                        'node': {
                                                                            'addresses': {
                                                                                'edges': [
                                                                                    {
                                                                                        'node': {
                                                                                            'gateway': None,
                                                                                            'ipAddress': '169.254.2.2',
                                                                                            'prefixLength': 25
                                                                                        }}]},
                                                                            'name': 'beta',
                                                                            'state': None
                                                                        }},
                                                                    {
                                                                        'node': {
                                                                            'addresses': {
                                                                                'edges': [
                                                                                    {
                                                                                        'node': {
                                                                                            'gateway': None,
                                                                                            'ipAddress': '169.254.3.2',
                                                                                            'prefixLength': 27
                                                                                        }}]},
                                                                            'name': 'gamma',
                                                                            'state': None
                                                                        }},
                                                                    {
                                                                        'node': {
                                                                            'addresses': {
                                                                                'edges': [
                                                                                    {
                                                                                        'node': {
                                                                                            'gateway': None,
                                                                                            'ipAddress': '169.254.4.2',
                                                                                            'prefixLength': 27
                                                                                        }}]},
                                                                            'name': 'delta',
                                                                            'state': None
                                                                        }}]},
                                                            'sharedPhysAddress': '00:01:02:03:04:05',
                                                            'state': {
                                                                'operationalStatus': 'OPER_UP'
                                                            }
                                                        }
                                                    },
                                                    {
                                                        'node': {'name': 'three',
                                                              'networkInterfaces': {
                                                                  'edges': [
                                                                      {
                                                                          'node': { 
                                                                              'addresses': {
                                                                                  'edges': []
                                                                              },
                                                                              'name': 'epsilon',
                                                                              'state': None
                                                                          }}]},
                                                                 'sharedPhysAddress': '06:07:08:09:0a:0b',
                                                                 'state': {
                                                                     'operationalStatus': 'OPER_DOWN'
                                                                 }}},
                                                    {
                                                        'node': {
                                                            'name': 'five',
                                                            'networkInterfaces': {
                                                                'edges': [
                                                                    {
                                                                        'node': {
                                                                            'addresses': {
                                                                                'edges': [
                                                                                    {
                                                                                        'node': {
                                                                                            'gateway': None,
                                                                                            'ipAddress': '169.254.8.2',
                                                                                            'prefixLength': 30
                                                                                        }}]},
                                                                            'name': 'theta',
                                                                            'state': None
                                                                        }}]},
                                                            'sharedPhysAddress': None,
                                                            'state': {
                                                                'operationalStatus': 'OPER_UP'
                                                            }}}]},
                                            'name': 'SITE0001P1B'
                                        }}]}}}]}}}
    expected_json_1 =  [
            {
                'addresses': [
                    {
                        'gateway': '169.254.1.1',
                        'ipAddress': '169.254.1.2',
                        'prefixLength': 30
                    }],
                'name': 'alpha',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000001',
                '/allRouters/nodes/deviceInterfaces/name': 'one',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': None,
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1A',
                'state': None
            },
            {
                'addresses': [
                    {
                        'gateway': None,
                        'ipAddress': '169.254.2.2',
                        'prefixLength': 25
                    }],
                'name': 'beta',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000001',
                '/allRouters/nodes/deviceInterfaces/name': 'two',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1A',
                'state': {
                    'addresses': [
                        {
                            'gateway': '<empty>',
                            'ipAddress': '<empty>',
                            'prefixLength': 0
                        }]}},
            {
                'addresses': [
                        {
                            'gateway': None,
                            'ipAddress': '169.254.3.2',
                            'prefixLength': 27
                        }],
                'name': 'gamma',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000001',
                '/allRouters/nodes/deviceInterfaces/name': 'two',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1A',
                'state': {
                    'addresses': [
                        {
                            'gateway': '<empty>',
                            'ipAddress': '<empty>',
                            'prefixLength': 0
                        }
                    ]
                }
            },
            {
                'addresses': [
                    {
                        'gateway': None,
                        'ipAddress': '169.254.4.2',
                        'prefixLength': 27
                    }],
                'name': 'delta',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000001',
                '/allRouters/nodes/deviceInterfaces/name': 'two',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1A',
                'state': {
                    'addresses': [
                        {
                            'gateway': '<empty>',
                            'ipAddress': '<empty>',
                            'prefixLength': 0
                        }]}},
            {
                'addresses': [],
                'name': 'epsilon',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000001',
                '/allRouters/nodes/deviceInterfaces/name': 'three',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': '06:07:08:09:0a:0b',
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1A',
                'state': {
                    'addresses': [
                        {
                            'gateway': '169.254.5.1',
                            'ipAddress': '169.254.5.2',
                            'prefixLength': 23
                        }]}},
            {
                'addresses': [
                    { 
                        'gateway': '169.254.6.1',
                        'ipAddress': '169.254.6.2',
                        'prefixLength': 31
                    }],
                'name': 'zeta',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000001',
                '/allRouters/nodes/deviceInterfaces/name': 'four',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': None,
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1A',
                'state': {
                    'addresses': [
                        {
                            'gateway': '<empty>',
                            'ipAddress': '<empty>',
                            'prefixLength': 0
                        }]}},
            {
            'addresses': [
                {
                    'gateway': None,
                    'ipAddress': '169.254.7.2',
                    'prefixLength': 30
            }],
            'name': 'theta',
            '/allRouters/name': 'SITE0001P1',
            '/allRouters/nodes/assetId': 'LR000000000001',
            '/allRouters/nodes/deviceInterfaces/name': 'five',
            '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': None,
            '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UNKNOWN',
            '/allRouters/nodes/name': 'SITE0001P1A',
            'state': {
                'addresses': [
                    {
                        'gateway': '<empty>',
                        'ipAddress': '<empty>',
                        'prefixLength': 0
            }]}},
            {
                'addresses': [
                    {
                        'gateway': '169.254.1.1',
                        'ipAddress': '169.254.1.2',
                        'prefixLength': 30
                }],
                'name': 'alpha',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000002',
                '/allRouters/nodes/deviceInterfaces/name': 'one',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': None,
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1B',
                'state': None
            },
            {
                'addresses': [ 
                    {
                        'gateway': None,
                        'ipAddress': '169.254.2.2',
                        'prefixLength': 25
                }],
                'name': 'beta',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000002',
                '/allRouters/nodes/deviceInterfaces/name': 'two',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1B',
                'state': None
            },
            {
                'addresses': [ 
                    {
                        'gateway': None,
                        'ipAddress': '169.254.3.2',
                        'prefixLength': 27
                }],
                'name': 'gamma',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000002',
                '/allRouters/nodes/deviceInterfaces/name': 'two',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1B',
                'state': None
            },
            {
                'addresses': [ 
                    {
                        'gateway': None,
                        'ipAddress': '169.254.4.2',
                        'prefixLength': 27
                }],
                'name': 'delta',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000002',
                '/allRouters/nodes/deviceInterfaces/name': 'two',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1B',
                'state': None
            },
            {
                'addresses': [],
                'name': 'epsilon',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000002',
                '/allRouters/nodes/deviceInterfaces/name': 'three',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': '06:07:08:09:0a:0b',
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_DOWN',
                '/allRouters/nodes/name': 'SITE0001P1B',
                'state': None
            },
            {
                'addresses': [ 
                    {
                        'gateway': None,
                        'ipAddress': '169.254.8.2',
                        'prefixLength': 30
                }],
                'name': 'theta',
                '/allRouters/name': 'SITE0001P1',
                '/allRouters/nodes/assetId': 'LR000000000002',
                '/allRouters/nodes/deviceInterfaces/name': 'five',
                '/allRouters/nodes/deviceInterfaces/sharedPhysAddress': None,
                '/allRouters/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                '/allRouters/nodes/name': 'SITE0001P1B',
                'state': None
            }
        ]

    unflattened_json_2 = {
        "data": {
            "allServices": {
                  "edges": [
                      {
                          "node": {
                               "name": "Store_1234_One",
                               "shareServiceRoutes": True
                           }
                      },
                      {
                          "node": {
                               "name": "Store_1234_Two",
                               "shareServiceRoutes": True
                           }
                      },
                      {
                          "node": {
                               "name": "Store_1234_Three",
                               "shareServiceRoutes": True
                           }
                      },
                      {
                          "node": {
                               "name": "Store_1234_Four",
                               "shareServiceRoutes": True
                          }
                      }
                  ]
              }
         }
    }

    expected_json_2 = [
        {
             "name": "Store_1234_One",
             "shareServiceRoutes": True
        },
        {
            "name": "Store_1234_Two",
            "shareServiceRoutes": True
        },
        {
            "name": "Store_1234_Three",
            "shareServiceRoutes": True
        },
        {
            "name": "Store_1234_Four",
            "shareServiceRoutes": True
        }
    ]


    def test_flattened_json(self):
        gql = gql_helper.NodeGQL("allRouters")
        json_results = gql.format_results(TestGqlHelper.unflattened_json_1)
        flatter_json = gql.flatten_json(json_results, '/allRouters/nodes/deviceInterfaces/networkInterfaces')
        assert flatter_json == TestGqlHelper.expected_json_1

        gql = gql_helper.NewGQL("allServices")
        json_results = TestGqlHelper.unflattened_json_2['data']
        flatter_json = gql.flatten_json(json_results, '/allServices', '/')
        assert flatter_json == TestGqlHelper.expected_json_2
