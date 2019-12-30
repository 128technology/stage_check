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

import argparse
import re
import requests
import json
import rpm

import pprint

try:
    from stage_check import init_helper
except ImportError:
    import init_helper

try:
    from stage_check import RouterContext
except ImportError:
    import RouterContext

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import Linux
except ImportError:
    import Linux

try:
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest

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
     "routerName" : "SITE0002P1",
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

local_init_router = """
    {
        "init": {
            "id": "corp2B"
        },
        "secureCommunication": {
            "interNodeKeepAliveMaxAttempt": 9,
            "interConductorRouterKeepAliveInterval": 1,
            "interConductorRouterKeepAliveMaxAttempt": 9,
            "interNodeKeepAliveInterval": 1
        }
    }
"""

local_init_conductor = """
    {
        "init": {
            "id": "cond_A"
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
                "corp2B": {
                    "host": "10.0.1.28"
                },
                "corp2A": {
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
                "cond_B": {
                    "host": "10.0.1.28"
                },
                "cond_A": {
                    "host": "10.0.1.27"
                }
            }
        }
    }
"""

class MockResponse:
    def __init__(self, json_data={}, status=200):
        self.status_code = status
        self.json_data = json_data
        self.content = "TEST CONTENT"
        self.text = "TEST TEXT"

    def json(self):
        #assert False, pprint.pformat(self.json_data)
        return self.json_data

class TestBase:
    STAGE_CHECK_BASE = ".stage_check"
    STAGE_CHECK_GLOBAL_CONFIG = "/etc/stage_check.d"
    STAGE_CHECK_GLOBAL_LIB = "/usr/lib/stage_check"

    router_info_reply = {
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
                                       'assetId': 'LR201907013898',
                                       'name': 'corp2A',
                                       'state': {
                                           'processes': [
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'accessManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'analyticsReporter',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'applicationFrameworkManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'conflux',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'databaseQueryCoordinator',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'STANDBY',
                                                   'name': 'dynamicPeerUpdateManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'fastLane',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'highwayManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'nodeMonitor',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'persistentDataManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'STANDBY',
                                                   'name': 'redisServerManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'STANDBY',
                                                   'name': 'routingManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'secureCommunicationManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'STANDBY',
                                                   'name': 'securityKeyManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'snmpTrapAgent',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'stateMonitor',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'systemServicesCoordinator',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               }
                                           ]
                                       }
                                   }
                               },
                               {
                                   'node': {
                                       'assetId': 'LR201907013901',
                                       'name': 'corp2B',
                                       'state': {
                                           'processes': [
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'accessManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'analyticsReporter',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'applicationFrameworkManager',
                                                   'primary': False,
                                                   'status' : 'Running'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'conflux',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'databaseQueryCoordinator',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'ACTIVE',
                                                   'name': 'dynamicPeerUpdateManager',
                                                   'primary': True,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'fastLane',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'highwayManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'nodeMonitor',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'persistentDataManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'ACTIVE',
                                                   'name': 'redisServerManager',
                                                   'primary': True,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'ACTIVE',
                                                   'name': 'routingManager',
                                                   'primary': True,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'secureCommunicationManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'ACTIVE',
                                                   'name': 'securityKeyManager',
                                                   'primary': True,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'snmpTrapAgent',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {   
                                                   'leaderStatus': 'NONE',
                                                   'name': 'stateMonitor',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'systemServicesCoordinator',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               }
                                           ]
                                        }
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

    router_info_reply_single = {
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
                                       'assetId': 'LR201907013898',
                                       'name': 'corp2A',
                                       'state': {
                                           'processes': [
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'accessManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'analyticsReporter',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'applicationFrameworkManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'conflux',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'databaseQueryCoordinator',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'STANDBY',
                                                   'name': 'dynamicPeerUpdateManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'fastLane',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'highwayManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'nodeMonitor',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'persistentDataManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'STANDBY',
                                                   'name': 'redisServerManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'STANDBY',
                                                   'name': 'routingManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'secureCommunicationManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'STANDBY',
                                                   'name': 'securityKeyManager',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'snmpTrapAgent',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'stateMonitor',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               },
                                               {
                                                   'leaderStatus': 'NONE',
                                                   'name': 'systemServicesCoordinator',
                                                   'primary': False,
                                                   'status': 'RUNNING'
                                               }
                                           ]
                                       }
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

    @pytest.fixture
    def create_router_files(self, fs):
        global local_init
        global globl_init_router
        fs.create_file("/etc/128technology/local.init", contents=local_init_router)
        fs.create_file("/etc/128technology/global.init", contents=global_init_router)
        token_path = os.path.join(os.environ['HOME'], '.graphql')
        token_file_path = os.path.join(token_path, 'token')
        fs.create_file(token_file_path, contents="this_is_a_bogus_token_for_testing")

    @pytest.fixture
    def create_conductor_files(self, fs):
        global local_init
        global global_init_conductor
        fs.create_file("/etc/128technology/local.init", contents=local_init_conductor)
        fs.create_file("/etc/128technology/global.init", contents=global_init_conductor)
        token_path = os.path.join(os.environ['HOME'], '.graphql')
        token_file_path = os.path.join(token_path, 'token')
        fs.create_file(token_file_path, contents="this_is_a_bogus_token_for_testing")

    @pytest.fixture
    def local_context(self, monkeypatch):
        """
        # Without this one gets the infamous PYPI python bindings error...
        def mocked_rpm_labelCompare(ver1, ver2):
            return 0
        monkeypatch.setattr(
            rpm, 
            'labelCompare', 
            mocked_rpm_labelCompare
        )
        """
        def mocked_init_helper_is_128(self):
            return True
        monkeypatch.setattr(
            init_helper.NodeInfo, 
            '_is_128', 
            mocked_init_helper_is_128
        )
        return init_helper.NodeInfo()

    @pytest.fixture
    def graphql_url(self):
        #return 'https://127.0.0.1:31516/api/v1/graphql'
        return 'http://127.0.0.1:31516/api/v1/graphql'
        
    def default_args(self, router="", node=""):
        self.args = argparse.Namespace()
        self.args.debug = False
        self.args.regex_patterns = False
        self.args.version = False
        self.args.router=router
        self.args.node=node
        self.args.primary_regex="A$"
        self.args.secondary_regex="B$"
        self.args.site_regex="([0-9]+)"
        self.args.pod_regex="[pP]([0-9]+)$"
        self.args.config_path = None
        self.args.json = False
        self.args.generic = False

    @pytest.fixture
    def map_real_paths(self, fs):
        real_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        fs.add_real_directory(real_path)

    @pytest.fixture
    def create_customization_paths(self, fs):
        paths = [
            self.STAGE_CHECK_GLOBAL_LIB + "/python",
            self.STAGE_CHECK_GLOBAL_CONFIG + "/profiles"
        ]
        #home_path = os.path.expanduser("~")
        #stage_check_base = os.path.join(home_path, self.STAGE_CHECK_BASE)
        for path in paths:
            #path = os.path.join(home_path, sub_dir)
            fs.create_dir(path)
        self.__custom_paths_faked = True

    def create_config_file(self, content):
        try:
            print(f"Customizations initialized: {self.__custom_paths_faked}")
        except NameError:
            return False
        #home_path = os.path.expanduser("~")
        #stage_check_base = os.path.join(home_path, self.STAGE_CHECK_BASE)
        config_path = os.path.join(self.STAGE_CHECK_GLOBAL_CONFIG, "config.json")
        with open(config_path, "w") as fh:
            fh.write(content)
        return True

    def create_test_profile(self, name, content):
        try:
            print(f"Customizations initialized: {self.__custom_paths_faked}")
        except NameError:
            return False
        #home_path = os.path.expanduser("~")
        #stage_check_base = os.path.join(home_path, self.STAGE_CHECK_BASE)
        profile_dir = os.path.join(self.STAGE_CHECK_GLOBAL_CONFIG, "profiles")
        if not os.path.exists(profile_dir):
            os.mkdir(profile_dir)
        profile_path = os.path.join(profile_dir, name + ".json")
        with open(profile_path, "w") as fh:
            fh.write(content)
        return True

    def verify_output(self, capsys, test_instance):
        captured = capsys.readouterr()
        all_lines = captured.out.splitlines()
        if "messages" in test_instance: 
            count = 0
            test_messages = test_instance["messages"]
            for line in all_lines:
                assert count < len(test_messages), f'{count}: "' + line + '" == MISSING!'
                assert line == test_messages[count]
                count += 1
            assert count == len(test_messages)
        elif "message" in test_instance:
             assert all_lines[0] == test_instance["message"]
        else:
             assert False, "No control text to compare!!!!"

    @pytest.fixture
    def create_hosts_file(self, fs):
        fs.create_file("/etc/hosts")

    def write_hosts_file(self, content):
        #assert False, "write_hosts_file:  " + content
        with open("/etc/hosts", "w") as fp:
            fp.write(content)
        with open("/etc/hosts", "r") as fp:
            lines = fp.readlines()
        #assert False, "write_hosts_file(r): " + pprint.pformat(lines)    

    @pytest.fixture
    def mock_check_user(self, monkeypatch):
        """
        Linux.HostsFile.run_linux_args() is overriden so it does not
        actually try to execute the command, but instead returns a 
        predetermined json dictionary for test purposes...
        """
        def mocked_check_user(self, required_user=None, required_group="stage_check"):
            assert True == isinstance(self, AbstractTest.Linux)
            return Output.Status.OK
        monkeypatch.setattr(
            AbstractTest.Linux, 
            'check_user', 
            mocked_check_user
        ) 

    @pytest.fixture
    def mock_get_site_id(self, monkeypatch, get_site_id_output):
        """
        Linux.HostsFile.run_linux_args() is overriden so it does not
        actually try to execute the command, but instead returns a 
        predetermined json dictionary for test purposes...
        """
        def mocked_get_site_id(self):
            assert True == isinstance(self, RouterContext.Base)
            self.__site_id = get_site_id_output
            return self.__site_id
        monkeypatch.setattr(
            RouterContext.Base, 
            'get_site_id', 
            mocked_get_site_id
        ) 

    @pytest.fixture
    def mock_linux_run(self, monkeypatch, linux_run_output):
        """
        Linux.Base.run_linux() is overriden so it does not
        actually try to execute the command, but instead returns a
        predetermined python list of simulated linux shell command 
        output for test purposes...
        """
        def mocked_linux_run(self, router_context, node_type, output_lines, error_lines):
            error_lines.clear()
            node_name = router_context.get_node_name(node_type)
            assert node_name is not None, f"No {node_type} node for router {router_context.get_router()}"
            assert node_type in linux_run_output, f"Missing test output for node type {node_type}"
            output_lines.extend(linux_run_output[node_type])
            #assert False, "********** mocked linux_run **********" + pprint.pformat(output_lines)
            return 0

        monkeypatch.setattr(
            Linux.Base,
            'run_linux',
            mocked_linux_run
        )

    @pytest.fixture
    def mock_requests_post(self, monkeypatch, requests_post_output):
        """
        Monkey patch requests.post and return a pseudo response
        object. Note that data returned depends on examination
        of the json graphql request

        TODO:  Find some way to parametrize this.
        """
        def mocked_post(uri, *args, **kwargs):
            json_string = kwargs["data"]
            json_data = json.loads(json_string)
            query_string = json_data["query"]
            #assert False, pprint.pformat(requests_post_output)
            for entry in requests_post_output:
                if "regex" in entry and \
                   re.match(entry["regex"], query_string) and \
                   "reply" in entry:
                    return MockResponse(entry["reply"])
            assert False, "====== Failed to match Query ======\nQUERY=" + query_string + "\nDATA=" + pprint.pformat(requests_post_output)
        monkeypatch.setattr(requests, 'post', mocked_post) 

