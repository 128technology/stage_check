####################################################################################
#   _            _                  _     _          _                             
#  | |_ ___  ___| |_     __ _  __ _| |   | |__   ___| |_ __   ___ _ __ _ __  _   _ 
#  | __/ _ \/ __| __|   / _` |/ _` | |   | '_ \ / _ \ | '_ \ / _ \ '__| '_ \| | | |
#  | ||  __/\__ \ |_   | (_| | (_| | |   | | | |  __/ | |_) |  __/ | _| |_) | |_| |
#   \__\___||___/\__|___\__, |\__, |_|___|_| |_|\___|_| .__/ \___|_|(_) .__/ \__, |
#                  |_____| |_|   |_||_____|           |_|             |_|    |___/ 
# 
####################################################################################

import pytest 

import pytest_common
import gql_helper

class TestGqlHelper(pytest_common.TestBase):
    unflattened_json = {
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
    expected_json =  [
            {
                'addresses': [
                    {
                        'gateway': '169.254.1.1',
                        'ipAddress': '169.254.1.2',
                        'prefixLength': 30
                    }],
                'name': 'alpha',
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000001',
                'router/nodes/deviceInterfaces/name': 'one',
                'router/nodes/deviceInterfaces/sharedPhysAddress': None,
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1A',
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
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000001',
                'router/nodes/deviceInterfaces/name': 'two',
                'router/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1A',
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
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000001',
                'router/nodes/deviceInterfaces/name': 'two',
                'router/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1A',
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
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000001',
                'router/nodes/deviceInterfaces/name': 'two',
                'router/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1A',
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
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000001',
                'router/nodes/deviceInterfaces/name': 'three',
                'router/nodes/deviceInterfaces/sharedPhysAddress': '06:07:08:09:0a:0b',
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1A',
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
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000001',
                'router/nodes/deviceInterfaces/name': 'four',
                'router/nodes/deviceInterfaces/sharedPhysAddress': None,
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1A',
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
            'router/name': 'SITE0001P1',
            'router/nodes/assetId': 'LR000000000001',
            'router/nodes/deviceInterfaces/name': 'five',
            'router/nodes/deviceInterfaces/sharedPhysAddress': None,
            'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UNKNOWN',
            'router/nodes/name': 'SITE0001P1A',
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
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000002',
                'router/nodes/deviceInterfaces/name': 'one',
                'router/nodes/deviceInterfaces/sharedPhysAddress': None,
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1B',
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
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000002',
                'router/nodes/deviceInterfaces/name': 'two',
                'router/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1B',
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
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000002',
                'router/nodes/deviceInterfaces/name': 'two',
                'router/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1B',
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
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000002',
                'router/nodes/deviceInterfaces/name': 'two',
                'router/nodes/deviceInterfaces/sharedPhysAddress': '00:01:02:03:04:05',
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1B',
                'state': None
            },
            {
                'addresses': [],
                'name': 'epsilon',
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000002',
                'router/nodes/deviceInterfaces/name': 'three',
                'router/nodes/deviceInterfaces/sharedPhysAddress': '06:07:08:09:0a:0b',
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_DOWN',
                'router/nodes/name': 'SITE0001P1B',
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
                'router/name': 'SITE0001P1',
                'router/nodes/assetId': 'LR000000000002',
                'router/nodes/deviceInterfaces/name': 'five',
                'router/nodes/deviceInterfaces/sharedPhysAddress': None,
                'router/nodes/deviceInterfaces/state/operationalStatus': 'OPER_UP',
                'router/nodes/name': 'SITE0001P1B',
                'state': None
            }
        ]

    def test_flattened_json(self):
        gql = gql_helper.NodeGQL("allRouters")
        json_results = gql.format_results(TestGqlHelper.unflattened_json)
        flatter_json = gql.flatten_json(json_results, 'router/nodes/deviceInterfaces/networkInterfaces', '/')
        assert flatter_json == TestGqlHelper.expected_json
