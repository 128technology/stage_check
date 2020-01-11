###############################################################################
#
#   _ __  _   _| |_ ___  ___| |_     ___ ___  _ __ ___  _ __ ___   ___  _ __  
#  | '_ \| | | | __/ _ \/ __| __|   / __/ _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \ 
#  | |_) | |_| | ||  __/\__ \ |_   | (_| (_) | | | | | | | | | | | (_) | | | | 
#  | .__/ \__, |\__\___||___/\__|___\___\___/|_| |_| |_|_| |_| |_|\___/|_| |_|
#  |_|    |___/                |_____|       
#
###############################################################################

import os
import pytest
import pyfakefs

try:
    from stage_check import init_helper
except ImportError:
    import init_helper

assets = [
{
     "assetId" : "LR000000000001",
     "routerName" : "SITE0001P1",
     "nodeName"   : "SITE0001P1A",
     "t128Version" : "4.1.1-1.el7.centos",
     "status" : "RUNNING",
     "assetIdConfigured" : True,
     "text" : "",
     "failedStatus" : None
 },
 {
     "assetId" : "LR000000000002",
     "routerName" : "SITE0001P1",
     "nodeName"   : "SITE0001P1B",
     "t128Version" : "4.1.1-1.el7.centos",
     "status" : "RUNNING",
     "assetIdConfigured" : True,
     "text" : "",
     "failedStatus" : None
 },
 {
     "assetId" : "LR000000000003",
     "routerName" : "AAPGA7298P1",
     "nodeName"   : "SITE0002P1A",
     "t128Version" : "4.1.1-1.el7.centos",
     "status" : "RUNNING",
     "assetIdConfigured" : True,
     "text" : "",
     "failedStatus" : None
 },
    {"assetId" : "LR000000000004",
     "routerName" : "SITE0002P1",
     "nodeName"   : "SITE0002P1B",
     "t128Version" : "4.1.1-1.el7.centos",
     "status" : "RUNNING",
     "assetIdConfigured" : True,
     "text" : "",
     "failedStatus" : None
 },
 {
     "assetId" : "LR000000000005",
     "routerName" : "SITE0003P1",
     "nodeName"   : "SITE0003P1A",
     "t128Version" : "4.1.1-1.el7.centos",
     "status" : "RUNNING",
     "assetIdConfigured" : True,
     "text" : "",
     "failedStatus" : None
 },
 {
     "assetId" : "LR000000000006",
     "routerName" : "SITE0003P1",
     "nodeName"   : "SITE0003P1B",
     "t128Version" : "4.1.1-1.el7.centos",
     "status" : "RUNNING",
     "assetIdConfigured" : True,
     "text" : "",
     "failedStatus" : None
 },
 {
     "assetId" : "LR000000000007",
     "routerName" : "SITE0004P1",
     "nodeName"   : "SITE0004P1A",
     "t128Version" : "4.1.1-1.el7.centos",
     "status" : "RUNNING",
     "assetIdConfigured" : True,
     "text" : "",
     "failedStatus" : None
 },
 {  
     "assetId" : "LR000000000008",
     "routerName" : "SITE0004P1",
     "nodeName"   : "SITE0004P1B",
     "t128Version" : "4.1.1-1.el7.centos",
     "status" : "RUNNING",
     "assetIdConfigured" : True,
     "text" : "",
     "failedStatus" : None
 },
 {
     "assetId" : "LR000000000009",
     "routerName" : "SITE0005P1",
     "nodeName"   : "SITE0005P1A",
     "t128Version" : "4.1.1-1.el7.centos",
     "status" : "RUNNING",
     "assetIdConfigured" : True,
     "text" : "",
     "failedStatus" : None
 },
 {
     "assetId" : "LR000000000010",
     "routerName" : "SITE0005P1",
     "nodeName"   : "SITE0005P1B",
     "t128Version" : "4.1.1-1.el7.centos",
     "status" : "RUNNING",
     "assetIdConfigured" : True,
     "text" : "",
     "failedStatus" : None
 }
]

local_init = """
    {
        "init": {
            "id": "corp2-secondary"
        },
        "secureCommunication": {
            "interNodeKeepAliveMaxAttempt": 9,
            "interConductorRouterKeepAliveInterval": 1,
            "interConductorRouterKeepAliveMaxAttempt": 9,
            "interNodeKeepAliveInterval": 1
        }
    }
"""

global_init_router = """
    {
        "init": {
            "routerName": "corp2",
            "control": {
                "corp2-secondary": {
                    "host": "10.0.1.28"
                },
                "corp2-primary": {
                    "host": "10.0.1.27"
                }
            },
            "conductor": {}
        }
    }
"""

global_init_conductor = """
    {
        "init": {
            "routerName": "cond",
            "conductor": {
                "corp2-secondary": {
                    "host": "10.0.1.28"
                },
                "corp2-primary": {
                    "host": "10.0.1.27"
                }
            }
        }
    }
"""

class TestBase:
    @pytest.fixture
    def create_router_files(self, fs):
        global local_init
        global globl_init_router
        fs.create_file("/etc/128technology/local.init", contents=local_init)
        fs.create_file("/etc/128technology/global.init", contents=global_init_router)
        token_path = os.path.join(os.environ['HOME'], '.graphql')
        token_file_path = os.path.join(token_path, 'token')
        fs.create_file(token_file_path, contents="this_is_a_bogus_token_for_testing")

    @pytest.fixture
    def create_conductor_files(self, fs):
        global local_init
        global global_init_conductor
        fs.create_file("/etc/128technology/local.init", contents=local_init)
        fs.create_file("/etc/128technology/global.init", contents=global_init_conductor)
        token_path = os.path.join(os.environ['HOME'], '.graphql')
        token_file_path = os.path.join(token_path, 'token')
        fs.create_file(token_file_path, contents="this_is_a_bogus_token_for_testing")

    @pytest.fixture
    def local_context(self):
        return init_helper.NodeInfo()

    @pytest.fixture
    def graphql_url(self):
        return 'https://127.0.0.1:31516/api/v1/graphql'
