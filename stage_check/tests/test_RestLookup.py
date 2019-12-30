############################################################################### 
#   _            _        
#  | |_ ___  ___| |_      
#  | __/ _ \/ __| __|     
#  | ||  __/\__ \ |_      
#   \__\___||___/\__|____ 
#                  |_____|
#   ____           _   _                _                             
#  |  _ \ ___  ___| |_| |    ___   ___ | | ___   _ _ __   _ __  _   _ 
#  | |_) / _ \/ __| __| |   / _ \ / _ \| |/ / | | | '_ \ | '_ \| | | |
#  |  _ <  __/\__ \ |_| |__| (_) | (_) |   <| |_| | |_) || |_) | |_| |
#  |_| \_\___||___/\__|_____\___/ \___/|_|\_\\__,_| .__(_) .__/ \__, |
#                                                 |_|    |_|    |___/ 
#
############################################################################### 
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
    from stage_check import paths
except ImportError:
    import paths

try:
    from stage_check import RouterContext
except ImportError:
    import RouterContext

try:
    from stage_check import Profiles_RestLookup
except ImportError:
    import Profile_RestLookup



class MockResponse:
    def __init__(self, json_data={}, status=200):
        self.status_code = status
        self.json_data = json_data
        self.content = "TEST CONTENT"
        self.text = "TEST TEXT"

    def json(self):
        return self.json_data

# These global dictionaries are manipulated by paramtrized test data                                                                                                                                                                                                           
GET_RESPONSE={}

@pytest.fixture
def mock_requests_get(monkeypatch):
    """
    Monkey patch requests.post and return a pseudo response
    object. Note that data returned depends on examination
    of the json graphql request

    TODO:  Find some way to parametrize this.
    """
    def mocked_get(uri, *args, **kwargs):
        global GET_RESPONSE
        return MockResponse(GET_RESPONSE)
    monkeypatch.setattr(requests, 'get', mocked_get)


class RestLookupBase(pytest_common.TestBase):

    rest_map_json = """
    {
      "URL" : "https://127.0.0.1",
      "URLSiteVariable" : "StoreNumber",
      "ProfileKeys" : [ 
          "Profile", 
          "Transport" 
      ],
      "Map" : {
          "mini_clinic_BB_LTE" : "optical_bb_lte"
      }
    }
    """

    @pytest.fixture
    def create_rest_map(self, fs):
        #home_path = os.path.expanduser("~")
        config_path = "/etc/stage_check.d"
        rest_map_path = os.path.join(config_path, "rest_map.json")
        fs.create_file(rest_map_path, contents=self.rest_map_json)

class Test_RestLookup(RestLookupBase):

    rest_reply = {
      "StoreNumber": "01544",
      "Address": "145 Franklin St",
      "City": "Westerly",
      "State": "RI",
      "ZipCode": "02891",
      "LocationCoordinates": "+41.35792-071.81117/",
      "Pod": "1",
      "RXLANNetwork": "172.19.225.0",
      "RXLANAddress": "172.19.225.1",
      "RXLANPrefix": "26",
      "NAT_ADDR_SIP_ALG_A": "172.19.225.3",
      "NAT_ADDR_SIP_ALG_B": "172.19.225.9",
      "NAT_ADDR_RDU": "172.19.225.7",
      "NAT_ADDR_P1_POS": "172.19.225.8",
      "NAT_ADDR_P2_POS_W1_Wireless": "172.19.225.10",
      "NAT_ADDR_P3_POS": "172.19.225.13",
      "NAT_ADDR_P4_POS": "172.19.225.25",
      "NAT_ADDR_W2_Wireless": "172.19.225.23",
      "NAT_ADDR_AppDMZ": "172.19.225.24",
      "NAT_ADDR_DVR": "172.19.225.40",
      "NAT_ADDR_EMS": "172.19.225.61",
      "Store_RX_Server": "172.19.225.11",
      "MCLANAddress": "10.238.10.161",
      "MCLANNetwork": "10.238.10.160",
      "MCLANPrefix": "27",
      "WANIP": "68.109.224.100",
      "WANPrefix": "27",
      "WANGateway": "68.109.224.97",
      "StoreWAN_Tx_Cap": "1540000",
      "DHCP_Opt_191": "pool1=10.18.90.23,10.18.90.24;level=2;level=2",
      "HWTYPE": "SilicomC044L",
      "Profile" : "mini_clinic",
      "Transport" : "BB_LTE",
      "NodeA": {
        "Asset": "RI01544AP1",
        "SN": "9129190040",
        "IMEI": "",
        "ICCID": ""
      },
      "NodeB": {
        "Asset": "RI01544BP1",
        "SN": "9129190036",
        "IMEI": "",
        "ICCID": ""
      }
    }

    config_content = """ 
    {
        "Version"             : "0.0.1",
        "BannerModule"        : "BannerText",
        "RouterContextModule" : "RouterContextZZZ",
        "RouterContextData" : {
           "DeploymentService" : "MISSING"
        },
        "PrimaryRegex"        : "P[0-9]+A$",
        "SecondaryRegex"      : "P[0-9]+B$",
        "SiteNumberRegex"     : "([0-9]+)",
        "ProfileModule"       : "RouterMap"
    }
    """

    profile_content = """
    {
      "Tests" : [
         {
            "TestModule"   : "LinuxServices",
            "OutputModule" : "Text",
            "Description"  : "Check Linux Services",
            "Parameters"   : {
                "node_type" : "secondary",
                "services"  : [ 
                    "128T",
                    "XXX",
                    "YYY"
                ],
                "exclude_tests" : [],
                "entry_tests" : {
                    "defaults" : {
                        "status"  : "FAIL",
                        "format"  : "Service {service} is in state {state_1}/{state_2}"
                    },
                    "tests" : [
                       { "test" : "state_1 != 'active' && 'state_2' != running" }
                    ],
                    "result"    : {
                        "PASS"  : "All {total_count} services checked are Active/Running",
                        "FAIL"  : "{match_count}/{total_count} services checked are NOT Active/Running"
                    }
                }
            }
         }    
      ]
    }
    """

    def setup(self):
        self.default_args()
        sys.path.append(os.path.dirname(__file__))

    def test_RestLookup(
            self,
            create_router_files, 
            local_context,
            create_customization_paths, 
            create_rest_map, 
            map_real_paths,
            mock_requests_get
        ):
        global GET_RESPONSE 
        GET_RESPONSE = self.rest_reply        
        assert self.create_config_file(self.config_content) == True
        assert self.create_test_profile("optical_bb_lte", self.profile_content) == True
        path_info = paths.Paths(self.args)
        router_context = RouterContext.create_instance(local_context, "SITE0001P1", self.args,
                                                       pytest_common.assets[1])
        profile_manager = Profiles_RestLookup.Manager(path_info, self.args)
        profile_manager.load_router(router_context)
        assert router_context.profile_name == "optical_bb_lte"

     
  
    
        
