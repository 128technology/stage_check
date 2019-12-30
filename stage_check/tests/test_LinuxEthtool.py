#!/usr/bin/env python3.6
########################################################################################
#   _            _        
#  | |_ ___  ___| |_      
#  | __/ _ \/ __| __|     
#  | ||  __/\__ \ |_      
#   \__\___||___/\__|____ 
#                  |_____|
#   _     _                  _____ _   _     _              _               
#  | |   (_)_ __  _   ___  _| ____| |_| |__ | |_ ___   ___ | |  _ __  _   _ 
#  | |   | | '_ \| | | \ \/ /  _| | __| '_ \| __/ _ \ / _ \| | | '_ \| | | |
#  | |___| | | | | |_| |>  <| |___| |_| | | | || (_) | (_) | |_| |_) | |_| |
#  |_____|_|_| |_|\__,_/_/\_\_____|\__|_| |_|\__\___/ \___/|_(_) .__/ \__, |
#                                                              |_|    |___/ 
########################################################################################
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
    from stage_check import TestEthtool
except ImportError:
    import TestEthtool


class Test_Ethtool(pytest_common.TestBase):
    """
    static-address is specified in parametrized data...
    """
    default_config = {
        "TestModule"   : "Ethtool",
        "OutputModule" : "Text",
        "Description"  : "Check HA interface speed",
        "Parameters"   : {
            "linux_device" : { 
               "__test__" : "enp0s20f0",
               "default"  : "enp0s20f0" 
            },
            "node_type"    : "primary",
            "entry_tests"  : {
               "no_match" : {
                   "status"  : "PASS",
                   "format" : "{linux_device} speed is {Speed}"
               },
               "tests" : [
                  {
                    "test"   : "Speed != '1000Mb/s'",
                    "status" : "FAIL",
                    "format" : "{linux_device} speed is {Speed} < 1000Mb/s"
                  }
               ]
            }
         }
    }

    def setup(self):
        self.default_args(router="corp2", node="corp2A")
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @pytest.mark.parametrize('test_instance,linux_run_output', [
        (
             {
                  "config"  : default_config,
                  "site-id" : "1234",
                  "second_node" :  False,
                  "hosts_secondary" : [],
                  "destination-ip" : "1.2.3.4",
                  "headline" : "0  Check HA interface speed      : \x1b[32m\x1b[01mPASS\x1b[0m  enp0s20f0 speed is 1000Mb/s"
             
             },
             {
                 "primary" : [
                     "Settings for enp0s20f0:",
                     "Supported ports: [ TP ]",
                     "Supported link modes:   10baseT/Half 10baseT/Full",
                     "                        100baseT/Half 100baseT/Full",
                     "                        1000baseT/Full",
                     "Supported pause frame use: Symmetric",
                     "Supports auto-negotiation: Yes",
                     "Supported FEC modes: Not reported",
                     "Advertised link modes:  10baseT/Half 10baseT/Full",
                     "                        100baseT/Half 100baseT/Full",
                     "                        1000baseT/Full",
                     "Advertised pause frame use: Symmetric",
                     "Advertised auto-negotiation: Yes",
                     "Advertised FEC modes: Not reported",
                     "Speed: 1000Mb/s",
                     "Duplex: Full",
                     "Port: Twisted Pair",
                     "PHYAD: 0",
                     "Transceiver: internal",
                     "Auto-negotiation: on",
                     "MDI-X: on (auto)",
                     "Supports Wake-on: pumbg",
                     "Wake-on: g",
                     "Current message level: 0x00000007 (7)",
                     "                       drv probe link",
                     "Link detected: yes"
                  ]
             }
        ),
        (
             {
                  "config"  : default_config,
                  "site-id" : "1234",
                  "second_node" :  False,
                  "hosts_secondary" : [],
                  "destination-ip" : "1.2.3.4",
                  "headline" : "0  Check HA interface speed      : \x1b[31m\x1b[01mFAIL  enp0s20f0 speed is 100Mb/s < 1000Mb/s\x1b[0m"
             
             },
             {
                 "primary" : [
                     "Settings for enp0s20f0:",
                     "Supported ports: [ TP ]",
                     "Supported link modes:   10baseT/Half 10baseT/Full",
                     "                        100baseT/Half 100baseT/Full",
                     "                        1000baseT/Full",
                     "Supported pause frame use: Symmetric",
                     "Supports auto-negotiation: Yes",
                     "Supported FEC modes: Not reported",
                     "Advertised link modes:  10baseT/Half 10baseT/Full",
                     "                        100baseT/Half 100baseT/Full",
                     "                        1000baseT/Full",
                     "Advertised pause frame use: Symmetric",
                     "Advertised auto-negotiation: Yes",
                     "Advertised FEC modes: Not reported",
                     "Speed: 100Mb/s",
                     "Duplex: Full",
                     "Port: Twisted Pair",
                     "PHYAD: 0",
                     "Transceiver: internal",
                     "Auto-negotiation: on",
                     "MDI-X: on (auto)",
                     "Supports Wake-on: pumbg",
                     "Wake-on: g",
                     "Current message level: 0x00000007 (7)",
                     "                       drv probe link",
                     "Link detected: yes"
                  ]
             }
        )
      ] 
   )

    def test_hosts_entry_exists(self, test_instance, local_context, graphql_url, capsys, mock_check_user,mock_linux_run):
        dest_ip = test_instance["destination-ip"]
        # config is irrelevant as test.run is not invoked...
        config = test_instance["config"]
        test_id = 0
        test = TestEthtool.create_instance(test_id, config, self.args)
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

