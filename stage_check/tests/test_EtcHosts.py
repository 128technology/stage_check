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
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest

try:
    from stage_check import TestEtcHosts
except ImportError:
    import TestEtcHosts


class Test_EtcHosts(pytest_common.TestBase):
    """
    static-address is specified in parametrized data...
    """
    default_config = {
        "TestModule"   : "EtcHosts",
        "OutputModule" : "Text",
        "Description"  : "Test /etc/hosts entries",
        "Parameters"   : {
            "entry_tests" : {
                "no_match" : {
                    "status"  : "PASS"
                },
                "defaults" : {
                    "status"  : "FAIL"
                },
                "tests"  : [
                    { "test" : "?localhost == False", "format" : "{node_name}: Missing service localhost"},
                    { "test" : "?Service-{site-id} == False", "format" : "{node_name}: Missing service Service-{site-id}"},
                ]        
            }
        }
    }

    def setup(self):
        self.default_args(router="corp2", node="corp2A")
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @pytest.mark.parametrize('test_instance,get_site_id_output,linux_run_output,requests_post_output', [
        (
             {
                  "config"  : default_config,
                  "site-id" : "1234",
                  "second_node" :  False,
                  "hosts_secondary" : [],
                  "destination-ip" : "1.2.3.4",
                  "headline" : "0  Test /etc/hosts entries       : \x1b[32m\x1b[01mPASS\x1b[0m  All 2 service entries present"
             
             },
             "1234",
             {
                  "primary" : [
                      "127.0.0.1    localhost", 
                      "1.2.3.4      Service-1234" 
                   ],
                  "secondary" : []
             },
             [
                 {
                     "regex" : r"\{allRouters.*?nodes.*?state\s*\{\s*processes",
                     "reply" : pytest_common.TestBase.router_info_reply_single
                 }
             ] 
        ),
        (    
             {
                 "config"  : default_config,
                 "site-id" : "1234",
                 "second_node" : True,
                 "destination-ip" : "1.2.3.4",
                 "headline" : "0  Test /etc/hosts entries       : \x1b[32m\x1b[01mPASS\x1b[0m  All 4 service entries present"
             },
             "1234",
             {
                 "primary" : [
                     "127.0.0.1    localhost", 
                     "1.2.3.4      Service-1234" 
                  ],
                  "secondary" : [
                      "127.0.0.1    localhost", 
                      "1.2.3.4      Service-1234" 
                  ],
             },
             [
                 {
                     "regex" : r"\{allRouters.*?nodes.*?state\s*\{\s*processes",
                     "reply" : pytest_common.TestBase.router_info_reply
                 } 
             ]
        ),
        (
            {
                "config"  : default_config,
                "site-id" : "1234",
                "second_node" : True,
                "destination-ip" : "1.2.3.4",
                "headline" : "0  Test /etc/hosts entries       : \x1b[31m\x1b[01mFAIL  Missing 1/4 service entries\x1b[0m"
           },
           "1234",
           {
                "primary" : [
                    "127.0.0.1    localhost"
                 ],
                "secondary" : [
                    "127.0.0.1    localhost", 
                    "1.2.3.4      Service-1234" 
                ],
           },
           [
               {
                   "regex" : r"\{allRouters.*?nodes.*?state\s*\{\s*processes",
                   "reply" : pytest_common.TestBase.router_info_reply
               }
           ] 
        )
      ] 
   )

    def test_hosts_entry_exists(self, test_instance, local_context, graphql_url, capsys, mock_get_site_id, mock_check_user, mock_requests_post, mock_linux_run):
        dest_ip = test_instance["destination-ip"]
        # config is irrelevant as test.run is not invoked...
        config = test_instance["config"]
        test_id = 0
        test = TestEtcHosts.create_instance(test_id, config, self.args)
        test.create_output_instance()
        router_context = RouterContext.create_instance(
            local_context, 
            self.args.router, 
            self.args)
        if test_instance["second_node"]:
            router_context.set_node(name="corp2B")

        test.run(local_context, router_context, None, fp=None)

        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()
        
        #assert False, pprint.pformat(all_lines)
        assert all_lines[3] == test_instance["headline"]

