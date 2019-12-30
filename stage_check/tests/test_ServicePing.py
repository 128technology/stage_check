#!/usr/bin/env python3.6
##############################################################################################
#   _            _       ____                  _          ____  _                           
#  | |_ ___  ___| |_    / ___|  ___ _ ____   _(_) ___ ___|  _ \(_)_ __   __ _   _ __  _   _ 
#  | __/ _ \/ __| __|   \___ \ / _ \ '__\ \ / / |/ __/ _ \ |_) | | '_ \ / _` | | '_ \| | | |
#  | ||  __/\__ \ |_     ___) |  __/ |   \ V /| | (_|  __/  __/| | | | | (_| |_| |_) | |_| |
#   \__\___||___/\__|___|____/ \___|_|    \_/ |_|\___\___|_|   |_|_| |_|\__, (_) .__/ \__, |
#                  |_____|                                              |___/  |_|    |___/ 
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
    from stage_check import TestServicePing
except ImportError:
    import TestServicePing   


@pytest.fixture
def mock_Linux_HostsFile(monkeypatch, linux_hosts_file_output):
    """
    Linux.HostsFile.run_linux_args() is overriden so it does not
    actually try to execute the command, but instead returns a 
    predetermined json dictionary for test purposes...
    """
    def mocked_hosts_file_run(self, router_context, node_type, error_lines, json_data):
        assert True == isinstance(self, Linux.HostsFile)
        error_lines.clear()
        self.clear_json()
        self.json_data.extend(linux_hosts_file_output)
        #json_data.update(self.json_data)
        json_data.extend(self.json_data)
        return 0
    monkeypatch.setattr(
        Linux.HostsFile, 
        'run_linux_args', 
        mocked_hosts_file_run
    ) 

class Test_ServicePing(pytest_common.TestBase):
    """
    static-address is specified in parametrized data...
    """
    default_config = {
        "TestModule"   : "ServicePing",
        "OutputModule" : "Text",
        "Description"  : "Test Service Ping",
        "Parameters"   : {
            "node_type"    : "primary|",
            "iterations" : 10,
            "service-list" : [
                { 
                    "tenant"  : "corp.t128",
                    "service" : "google_dns",
                    "destination-ip" : "8.8.8.8"
                }
            ],
        }
    }

    warn_config = {
        "TestModule"   : "ServicePing",
        "OutputModule" : "Text",
        "Description"  : "Test Service Ping",
        "Parameters"   : {
            "node_type"    : "primary|",
            "iterations" : 10,
            "service-list" : [
                { 
                    "tenant"  : "corp.t128",
                    "service" : "google_dns",
                    "destination-ip" : "8.8.8.8"
                }
            ],
            "fail_status"         : "WARN"
        },
    }

    allow_one_failure = {
        "TestModule"   : "ServicePing",
        "OutputModule" : "Text",
        "Description"  : "Test Service Ping",
        "Parameters"   : {
            "node_type"    : "primary|",
            "iterations" : 1,
            "service-list" : [
                { 
                    "tenant"  : "corp.t128",
                    "service" : "google_dns",
                    "destination-ip" : "8.8.8.8"
                }
            ],
            "max_ping_failures"  : 1
        },
    }

    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))

    test_parameters = [
       (
           {
              "config"  : default_config,
              "message" : "0  Test Service Ping             : \x1b[32m\x1b[01mPASS\x1b[0m  corp.t128->google_dns: 10/10 replies from 8.8.8.8; average latency 8.65ms",
               "json_status" : 0
           },
           [
               {
                    "regex"  : r"{ servicePing",
                    "reply"  : {
                        "data": {
                            "servicePing": {
                                'reachable' : True,
                                'status': 'SUCCESS',
                                'statusReason': '',
                                'responseTime': '8.648'
                             }
                         }
                     }
               }
           ]
       ),
       (
           {
               "config"  : default_config,
               "message" : "0  Test Service Ping             : \x1b[31m\x1b[01mFAIL  1/1 service permutations received < 10 replies\x1b[0m",
               "json_status" : 1
           },
           [
              {
                  "regex" : r"{ servicePing",
                  "reply" : {
                       "data": {
                           "servicePing": {
                               "reachable" : True,
                               "status": "ERROR",
                               "statusReason": "Specified service not found",
                               "responseTime": "0"
                           }
                       }
                   }
               }
           ]
       ),
       (
           {
               "config"  : default_config,
               "message" : "0  Test Service Ping             : \x1b[31m\x1b[01mFAIL  1/1 service permutations received < 10 replies\x1b[0m",
               "json_status" : 1
           },
           [
               {
                  "regex" : r"{ servicePing",
                  "reply" : {
                      "data": {
                          "servicePing": None
                      },
                      "errors": [
                          {
                              "locations": [
                                  { 
                                      "column": 3, 
                                      "line": 1
                                  }
                              ],
                              "message": "highwayManager@dc.AZDCBBP1 returned a 404",
                              "path": [
                                  "servicePing"
                              ]
                           }
                        ]
                     }
                 }
             ]
         ),
       (
           {
               "config"  : warn_config,
               "message" : "0  Test Service Ping             : \x1b[34m\x1b[01mWARN  1/1 service permutations received < 10 replies\x1b[0m",
               "json_status" : 2
           },
           [
              {
                  "regex" : r"{ servicePing",
                  "reply" : {
                       "data": {
                           "servicePing": {
                               "reachable" : True,
                               "status": "ERROR",
                               "statusReason": "Specified service not found",
                               "responseTime": "0"
                           }
                       }
                   }
               }
           ]
       ),
       (
           {
               "config"  : allow_one_failure,
               "message" : "0  Test Service Ping             : ",
               "message" : "0  Test Service Ping             : \x1b[32m\x1b[01mPASS\x1b[0m  All 1 service permutations received 1 replies",
               "json_status" : 0
           },
           [
              {
                  "regex" : r"{ servicePing",
                  "reply" : {
                       "data": {
                           "servicePing": {
                               "reachable" : True,
                               "status": "ERROR",
                               "statusReason": "Specified service not found",
                               "responseTime": "0"
                           }
                       }
                   }
               }
           ]
       )
     ]

    @pytest.mark.usefixtures("create_conductor_files")
    @responses.activate
    @pytest.mark.parametrize('test_instance,requests_post_output', test_parameters)

    def test_ping(self, test_instance, local_context, graphql_url, capsys, mock_requests_post):
        test_id = 0
        config = test_instance["config"]
        test = TestServicePing.create_instance(test_id, config, self.args)
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
                progress_str = f"0  Test Service Ping             :       Tenant corp.t128: ping google_dns {cur_it}/{max_count} tmo=2s"
                assert all_lines[cur_index] == progress_str
                cur_it += 1
                cur_index += 1
            cur_index += 1   
            # assert len(all_lines[cur_index]) == len(test_instance["message"]) 
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
        test = TestServicePing.create_instance(test_id, config, self.args)
        test.create_output_instance()
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


    @pytest.mark.usefixtures("create_conductor_files")
    @pytest.mark.parametrize('test_instance,linux_hosts_file_output', [
       (
          {
              "config"  : default_config,
              "entry"   : {
                  "service" : "Fubar",
                  "service-ip-from-hosts" : True
               },
               "destination-ip" : "1.2.3.4"
           },
           [
               {
                   "localhost" : [ "127.0.0.1" ],
                   "Fubar" : [ "1.2.3.4" ]
               }
           ]
        )
    ] 
   )
    def test_hosts_to_ip(self, test_instance, local_context, graphql_url, mock_Linux_HostsFile):
        entry = test_instance["entry"]
        dest_ip = test_instance["destination-ip"]
        # config is irrelevant as test.run is not invoked...
        config = test_instance["config"]
        test_id = 0
        test = TestServicePing.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(local_context, self.args.router, self.args)
        test._update_entry_dest_ip(
            local_context, 
            router_context, 
            config["Parameters"]["node_type"], 
            entry)
        assert entry["destination-ip"] == dest_ip
