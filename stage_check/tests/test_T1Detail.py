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
    from stage_check import TestT1Detail
except ImportError:
    import TestT1Detail

def prep_output_list(source, namespace, device):
    json_output = [ { "output" : source, "namespace" : namespace, "device" :  device } ]
    json_string = json.dumps(json_output, indent=None)
    test_string = "JSON: " + json_string
    return [ test_string ]

def prep_old_output(source):
    lines = source.splitlines()
    return lines

class Test_T1Detail(pytest_common.TestBase):
    """
    static-address is specified in parametrized data...
    """
    one_node_config=  {
        "TestModule"   : "T1Detail",
        "OutputModule" : "Text",
        "Description"  : "Check T1 Details",
        "Parameters"   : {
            "node_type"    :  "primary",
            "namespace"    :  "(t1-ns-[0-9]+) ",
            "linux_device" :  "^[0-9]+: (w1.*?[0-9]+):",
	    "find_devices" :  True,
	    "entry_tests" : {
               "no_match" : {
                   "status"  : "PASS"
               },
               "defaults" : {
                   "status"  : "FAIL"
               },
	       "tests"  : [
               	   { "test" : "AIS == 'ON'", "format" : "AIS == {AIS}" }, 
	           { "test" : "ALOS == 'ON'", "format" : "ALOS == {ALOS}" }, 
                   { "test" : "Bit_Errors_CRC6/Ft/Fs > 1000", "format" : "Bit Errors CRC6/Ft/Fs ({Bit_Errors_CRC6/Ft/Fs}) > 1000" }, 
                   { "test" : "LOF == 'ON'", "format" : "LOF == {LOF}" }, 
                   { "test" : "LOS == 'ON'", "format" : "LOS == {LOS}" }, 
                   { "test" : "Line_Code_Violation > 1000", "format" : "Line Code Violation ({Line_Code_Violation}) > 1000" }, 
                   { "test" : "Loss_of_Signal == 'ON'", "format" : "Loss of Signal == {Loss_of_Signal}" },
	           { "test" : "Open_Circuit == 'ON'", "format" : "Open Circuit == {Open_Circuit}" },
                   { "test" : "Out_of_Frame_Errors > 1000", "format" : "Out of Frame Errors ({Out_of_Frame_Errors}) > 1000" }, 
		   { "test" : "RAI == 'ON'", "format" : "RAI == {RAI}" },
		   { "test" : "RED == 'ON'", "format" : "RED == {RED}" },
		   { "test" : "Short_Circuit == 'ON'", "format" : "Short Circuit == {Short_Circuit}" },
		   { "test" : "Sync_Errors > 1000", "format" : "{node_name}: Sync Errors ({Sync_Errors}) > 1000" },
                   { "test" : "TxAIS == 'ON'", "format" : "TxAIS == {TxAIS}" }, 
		   { "test" : "YEL == 'ON'", "format" : "YEL == {YEL}" },
		   { "test" : "Rx_Level_High != '-2.5'", "format" : "Rx Level {Rx_Level_High} != -2.5" }
            ]
         }
       }
    }

    one_node_old_style=  {
        "TestModule"   : "T1Detail",
        "OutputModule" : "Text",
        "Description"  : "Check T1 Details",
        "Parameters"   : {
            "node_type"    :  "primary",
            "namespace"    :  "(t1-ns-[0-9]+) ",
            "linux_device" :  "^[0-9]+: (w1.*?[0-9]+):",
	    "find_devices" :  False,
	    "entry_tests" : {
               "no_match" : {
                   "status"  : "PASS"
               },
               "defaults" : {
                   "status"  : "FAIL"
               },
	       "tests"  : [
               	   { "test" : "AIS == 'ON'", "format" : "AIS == {AIS}" }, 
	           { "test" : "ALOS == 'ON'", "format" : "ALOS == {ALOS}" }, 
                   { "test" : "Bit_Errors_CRC6/Ft/Fs > 1000", "format" : "Bit Errors CRC6/Ft/Fs ({Bit_Errors_CRC6/Ft/Fs}) > 1000" }, 
                   { "test" : "LOF == 'ON'", "format" : "LOF == {LOF}" }, 
                   { "test" : "LOS == 'ON'", "format" : "LOS == {LOS}" }, 
                   { "test" : "Line_Code_Violation > 1000", "format" : "Line Code Violation ({Line_Code_Violation}) > 1000" }, 
                   { "test" : "Loss_of_Signal == 'ON'", "format" : "Loss of Signal == {Loss_of_Signal}" },
	           { "test" : "Open_Circuit == 'ON'", "format" : "Open Circuit == {Open_Circuit}" },
                   { "test" : "Out_of_Frame_Errors > 1000", "format" : "Out of Frame Errors ({Out_of_Frame_Errors}) > 1000" }, 
		   { "test" : "RAI == 'ON'", "format" : "RAI == {RAI}" },
		   { "test" : "RED == 'ON'", "format" : "RED == {RED}" },
		   { "test" : "Short_Circuit == 'ON'", "format" : "Short Circuit == {Short_Circuit}" },
		   { "test" : "Sync_Errors > 1000", "format" : "{node_name}: Sync Errors ({Sync_Errors}) > 1000" },
                   { "test" : "TxAIS == 'ON'", "format" : "TxAIS == {TxAIS}" }, 
		   { "test" : "YEL == 'ON'", "format" : "YEL == {YEL}" },
		   { "test" : "Rx_Level_High != '-2.5'", "format" : "Rx Level {Rx_Level_High} != -2.5" }
            ]
         }
       }
    }

    all_node_config=  {
        "TestModule"   : "T1Detail",
        "OutputModule" : "Text",
        "Description"  : "Check T1 Details",
        "Parameters"   : {
            "node_type"    :  "all",
            "namespace"    :  "(t1-ns-[0-9]+) ",
            "linux_device" :  "^[0-9]+: (w1.*?[0-9]+):",
	    "find_devices" :  True,
	    "entry_tests" : {
               "no_match" : {
                   "status"  : "PASS"
               },
               "defaults" : {
                   "status"  : "FAIL"
               },
	       "tests"  : [
               	   { "test" : "AIS == 'ON'", "format" : "AIS == {AIS}" }, 
	           { "test" : "ALOS == 'ON'", "format" : "ALOS == {ALOS}" }, 
                   { "test" : "Bit_Errors_CRC6/Ft/Fs > 1000", "format" : "Bit Errors CRC6/Ft/Fs ({Bit_Errors_CRC6/Ft/Fs}) > 1000" }, 
                   { "test" : "LOF == 'ON'", "format" : "LOF == {LOF}" }, 
                   { "test" : "LOS == 'ON'", "format" : "LOS == {LOS}" }, 
                   { "test" : "Line_Code_Violation > 1000", "format" : "Line Code Violation ({Line_Code_Violation}) > 1000" }, 
                   { "test" : "Loss_of_Signal == 'ON'", "format" : "Loss of Signal == {Loss_of_Signal}" },
	           { "test" : "Open_Circuit == 'ON'", "format" : "Open Circuit == {Open_Circuit}" },
                   { "test" : "Out_of_Frame_Errors > 1000", "format" : "Out of Frame Errors ({Out_of_Frame_Errors}) > 1000" }, 
		   { "test" : "RAI == 'ON'", "format" : "RAI == {RAI}" },
		   { "test" : "RED == 'ON'", "format" : "RED == {RED}" },
		   { "test" : "Short_Circuit == 'ON'", "format" : "Short Circuit == {Short_Circuit}" },
		   { "test" : "Sync_Errors > 1000", "format" : "{node_name}: Sync Errors ({Sync_Errors}) > 1000" },
                   { "test" : "TxAIS == 'ON'", "format" : "TxAIS == {TxAIS}" }, 
		   { "test" : "YEL == 'ON'", "format" : "YEL == {YEL}" },
		   { "test" : "Rx_Level_High != '-2.5'", "format" : "Rx Level {Rx_Level_High} != -2.5" }
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
                                                           'type' : 't1',
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
                                                           'type' : 't1',
                                                           'globalId' : 3,
                                                           'deviceId' : 3,
                                                           'targetInterface' : 'fubar_3',
                                                           'state': {'operationalStatus': 'OPER_DOWN'}
                                                     }
                                                },
                                                {
                                                     'node': {
                                                          'name': '4',
                                                           'type' : 't1',
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
                                                           'type' : 't1',
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
                                                           'type' : 't1',
                                                           'globalId' : 3,
                                                           'deviceId' : 3,
                                                           'targetInterface' : 'fubar_3',
                                                           'state': {'operationalStatus': 'OPER_DOWN'}
                                                     }
                                                },
                                                {
                                                     'node': {
                                                          'name': '4',
                                                           'type' : 't1',
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
                                                         'type' : 't1',
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
                                                         'type' : 't1',
                                                         'globalId' : 3,
                                                         'deviceId' : 3,
                                                         'targetInterface' : 'fubar_3',
                                                         'state': {'operationalStatus': 'OPER_DOWN'}
                                                   }
                                              },
                                              {
                                                   'node': {
                                                        'name': '4',
                                                        'type' : 't1',
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
                                                           'type' : 't1',
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

    linux_t1_detail_as_text = """
     ***** w1g1: T1 Rx Alarms (Framer) *****

     ALOS:     OFF     | LOS:  OFF
     RED:      OFF     | AIS:  OFF
     LOF:      OFF     | RAI:  OFF

     ***** w1g1: T1 Rx Alarms (LIU) *****

     Short Circuit:    OFF
     Open Circuit:     OFF
     Loss of Signal:   OFF

     ***** w1g1: T1 Tx Alarms *****

     AIS:      OFF     | YEL:  OFF


    ***** w1g1: T1 Performance Monitoring Counters *****

     Line Code Violation       : 0
     Bit Errors (CRC6/Ft/Fs)   : 16
     Out of Frame Errors       : 7
     Sync Errors               : 0


     Rx Level  : > -2.5db
"""

    linux_t1_sync_errors_as_text = """
     ***** w1g1: T1 Rx Alarms (Framer) *****

     ALOS:     OFF     | LOS:  OFF
     RED:      OFF     | AIS:  OFF
     LOF:      OFF     | RAI:  OFF

     ***** w1g1: T1 Rx Alarms (LIU) *****

     Short Circuit:    OFF
     Open Circuit:     OFF
     Loss of Signal:   OFF

     ***** w1g1: T1 Tx Alarms *****

     AIS:      OFF     | YEL:  OFF


    ***** w1g1: T1 Performance Monitoring Counters *****

     Line Code Violation       : 0
     Bit Errors (CRC6/Ft/Fs)   : 16
     Out of Frame Errors       : 7
     Sync Errors               : 2000


     Rx Level  : > -2.5db
"""

    def setup(self):
        self.default_args(router="corp2", node="corp2A")
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @pytest.mark.parametrize('test_instance,linux_run_output,requests_post_output', [
       (
          {
              "config"      : one_node_config,
              "second_node" : False,
              "headline"    : "0  Check T1 Details              : \x1b[32m\x1b[01mPASS\x1b[0m  All 1 interfaces(s) within parameters"
          },
          {
              "primary"   : prep_output_list(linux_t1_detail_as_text, "t1", "fubar_1"),
              "secondary" : prep_output_list(linux_t1_detail_as_text, "t1", "fubar_1"),
              "solitary"  : prep_output_list(linux_t1_detail_as_text, "t1", "fubar_1")
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
              "config"      : one_node_old_style,
              "second_node" : False,
              "headline"    : "0  Check T1 Details              : \x1b[32m\x1b[01mPASS\x1b[0m  All 1 interfaces(s) within parameters"
          },
          {
              "primary"   : prep_old_output(linux_t1_detail_as_text), 
              "secondary" : prep_old_output(linux_t1_detail_as_text), 
              "solitary"  : prep_old_output(linux_t1_detail_as_text)
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
              "config"      : all_node_config,
              "second_node" : True,
              "headline"    : "0  Check T1 Details              : \x1b[32m\x1b[01mPASS\x1b[0m  All 2 interfaces(s) within parameters"
          },
          {
              "primary"   : prep_output_list(linux_t1_detail_as_text, "t1", "fubar_1"),
              "secondary" : prep_output_list(linux_t1_detail_as_text, "t1", "fubar_1"),
              "solitary"  : prep_output_list(linux_t1_detail_as_text, "t1", "fubar_1")
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
              "config"      : all_node_config,
              "second_node" : False,
              "headline"    : "0  Check T1 Details              : \x1b[31m\x1b[01mFAIL  1 exceptions detected for 1/1 interfaces(s)\x1b[0m"
          },
          {
              "primary"   : prep_output_list(linux_t1_sync_errors_as_text, "t1", "fubar_1"),
              "secondary" : prep_output_list(linux_t1_sync_errors_as_text, "t1", "fubar_1"),
              "solitary"  : prep_output_list(linux_t1_sync_errors_as_text, "t1", "fubar_1")
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
   )


    def test_t1_detail(self, test_instance, local_context, graphql_url, capsys, mock_linux_run, mock_check_user, mock_requests_post):
        config = test_instance["config"]
        test_id = 0
        test = TestT1Detail.create_instance(test_id, config, self.args)
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
        assert all_lines[3] == test_instance["headline"]

