#!/usr/bin/env python3.6
########################################################################################
#   _            _      
#  | |_ ___  ___| |_    
#  | __/ _ \/ __| __|   
#  | ||  __/\__ \ |_    
#   \__\___||___/\__|____
#                  |_____|
#   _     _                   ____                  _                             
#  | |   (_)_ __  _   ___  __/ ___|  ___ _ ____   _(_) ___ ___  ___   _ __  _   _ 
#  | |   | | '_ \| | | \ \/ /\___ \ / _ \ '__\ \ / / |/ __/ _ \/ __| | '_ \| | | |
#  | |___| | | | | |_| |>  <  ___) |  __/ |   \ V /| | (_|  __/\__ \_| |_) | |_| |
#  |_____|_|_| |_|\__,_/_/\_\|____/ \___|_|    \_/ |_|\___\___||___(_) .__/ \__, |
#                                                                    |_|    |___/ 
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
    from stage_check import Linux
except ImportError:
    import Linux

try:
    from stage_check import TestLinuxServices
except ImportError:
    import TestLinuxServices

LINUX_SYSTEMCTL_STATUS = 0
LINUX_SYSTEMCTL_ERRORS = []
LINUX_SYSTEMCTL_DATA   = []

@pytest.fixture
def mock_linux_systemctl_status(monkeypatch):
    """
    Monkey patch Linux.SystemctlStatus and return a list
    """
    def mocked_post(uri, *args, **kwargs):
        global LINUX_SYSTEMCTL_STATUS
        global LINUX_SYSTEMCTL_ERRORS
        global LINUX_SYSTEMCTL_DATA
        error_out = args[3]
        data_out  = args[4]
        error_out.clear()
        error_out.extend(LINUX_SYSTEMCTL_ERRORS)
        data_out.clear()
        data_out.extend(LINUX_SYSTEMCTL_DATA)
        return LINUX_SYSTEMCTL_STATUS
    monkeypatch.setattr(Linux.SystemctlStatus, 'run_linux_args', mocked_post) 

class Test_LinuxServices(pytest_common.TestBase):
    default_config =  {
        "TestModule"   : "LinuxServices",
        "OutputModule" : "Text",
        "Description"  : "Check Linux Services",
        "Parameters"   : {
	   "node_type" : "secondary",
	   "services"  : [ "128T", "128TWeb" ],
           "exclude_tests" : [],
           "entry_tests" : {
               "defaults" : {
                   "status"  : "FAIL",
                   "format"  : "Service {service} is in state {state_1}/{state_2}"
               },
               "tests" : [
                   { "test" : "state_1 != 'active' && state_2 != 'running'" }
               ],
               "result"    : {
                   "PASS"  : "All {total_count} services checked are Active/Running",
                   "FAIL"  : "{match_count}/{total_count} services checked are NOT Active/Running"
               }
           }
        }
    }    

    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))
   
    @pytest.mark.usefixtures("create_router_files")
    @pytest.mark.parametrize('test_instance',
    [
       {
           "config" : default_config,
           "output_status" : 200,
           "output_errors" : [],
           "output_data" : [
               {
                   'Main_PID': '11111',
                   'Main_Process': 'processManager',
                   'epoch_time': 1568161502.0,
                   'service' : '128T',  
                   'state_1': 'active',
                   'state_2': 'running',
                   'time': 'Wed 2019-09-11 00:25:02 EDT',
                   'uptime_days': 92,
                   'uptime_hours': 20,
                   'uptime_minutes': 19,
                   'uptime_seconds': 22,
                   'Tasks' : 2404,
                   'Memory' : 25.1,
                   'MemoryModifier' : 'GB'
               },
               {
                   'Main_PID': '22222',
                   'Main_Process': 'node',
                   'epoch_time': 1568161502.0,
                   'service' : '128TWeb',  
                   'state_1': 'active',
                   'state_2': 'running',
                   'time': 'Wed 2019-09-11 00:25:02 EDT',
                   'uptime_days': 92,
                   'uptime_hours': 20,
                   'uptime_minutes': 19,
                   'uptime_seconds': 22,
                   'Tasks' : 2404,
                   'Memory' : 25.1,
                   'MemoryModifier' : 'GB'
               }
           ],
           "message" : "0  Check Linux Services          : \x1b[32m\x1b[01mPASS\x1b[0m  All 2 services checked are Active/Running"
       },
       {
           "config" : default_config,
           "output_status" : 200,
           "output_errors" : [],
           "output_data" : [
               {
                   'Main_PID': '11111',
                   'Main_Process': 'processManager',
                   'epoch_time': 1568161502.0,
                   'service' : '128T',  
                   'state_1': 'active',
                   'state_2': 'running',
                   'time': 'Wed 2019-09-11 00:25:02 EDT',
                   'uptime_days': 92,
                   'uptime_hours': 20,
                   'uptime_minutes': 19,
                   'uptime_seconds': 22
               },
               {
                   'Main_PID': '22222',
                   'Main_Process': 'node',
                   'epoch_time': 1568161502.0,
                   'service' : '128TWeb',  
                   'state_1': 'inactive',
                   'state_2': 'dead',
                   'time': 'Wed 2019-09-11 00:25:02 EDT',
                   'uptime_days': 92,
                   'uptime_hours': 20,
                   'uptime_minutes': 19,
                   'uptime_seconds': 22
               }
           ],
           "message" : "0  Check Linux Services          : \x1b[31m\x1b[01mFAIL  1/2 services checked are NOT Active/Running\x1b[0m"
       }
    ]
    )
    def test_linux_services(self, test_instance, local_context, capsys, mock_check_user, mock_linux_systemctl_status):
        global LINUX_SYSTEMCTL_STATUS
        global LINUX_SYSTEMCTL_ERRORS
        global LINUX_SYSTEMCTL_DATA

        LINUX_SYSTEMCTL_STATUS = test_instance["output_status"]
        LINUX_SYSTEMCTL_ERRORS = test_instance["output_errors"]
        LINUX_SYSTEMCTL_DATA = test_instance["output_data"]

        test_id = 0
        test = TestLinuxServices.create_instance(test_id, test_instance["config"], self.args)
        test.create_output_instance()

        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()

        # assert len(all_lines[0]) == len(test_instance["message"]) 
        assert all_lines[0] == test_instance["message"]

        
