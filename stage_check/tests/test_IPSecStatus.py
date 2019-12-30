#!/usr/bin/env python3.6
##############################################################################################
#  _            _       ___ ____  ____            ____  _        _               
# | |_ ___  ___| |_    |_ _|  _ \/ ___|  ___  ___/ ___|| |_ __ _| |_ _   _ ___   
# | __/ _ \/ __| __|    | || |_) \___ \ / _ \/ __\___ \| __/ _` | __| | | / __|  
# | ||  __/\__ \ |_     | ||  __/ ___) |  __/ (__ ___) | || (_| | |_| |_| \__ \_ 
#  \__\___||___/\__|___|___|_|   |____/ \___|\___|____/ \__\__,_|\__|\__,_|___(_)
#                |_____|                                                        
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
    from stage_check import TestIPSecStatus
except ImportError:
    import TestIPSecStatus

def prepare_linux_output(text):
    return text.splitlines()

class Test_IPSecStatus(pytest_common.TestBase):
    """
    static-address is specified in parametrized data...
    """
    default_config = {
        "TestModule"   : "IPSecStatus",
        "OutputModule" : "Text",
        "Description"  : "Test IPSec Connections",
        "Parameters"   : {
            "node_type" : "all",
            "entry_tests" : {
                "no_match" : {
                    "status"  : "PASS"
                },
                "defaults" : {
                    "status"  : "FAIL",
                    "format"  : "{node_name}: IPSec Connections loaded={loaded} > active={active}"
                },
                "tests"  : [
                    { "test" : "loaded > active"},
                ],
                "result": {
                    "PASS" : "All loaded IPSec connections are active",
                    "FAIL" : "{FAIL} nodes with inactive IPSec Connections"
               }
            }
        }
    }

    ipsec_status_ok = """
    000  
    000 "paloalto-tunnel-ipsec-cipher-0":   IKE algorithms: AES_CBC_128-HMAC_SHA1-MODP1024
    000 "paloalto-tunnel-ipsec-cipher-0":   ESP algorithms: NULL-HMAC_MD5_96-MODP1024
    000  
    000 Total IPsec connections: loaded 2, active 2
    000  
    000 State Information: DDoS cookies not required, Accepting new IKE connections
    000 IKE SAs: total(1), half-open(1), open(0), authenticated(0), anonymous(0)
    000 IPsec SAs: total(0), authenticated(0), anonymous(0)
    000  
    """

    ipsec_status_output = """
    000  
    000 Connection list:
    000  
    000 "paloalto-tunnel-ipsec-cipher-0": 0.0.0.0/0===169.254.129.2<169.254.129.2>[0771@128t.com]...165.1.203.57<165.1.203.57>[prisma@paloaltonetworks.com]===0.0.0.0/0; unrouted; eroute owner: #0
    000 "paloalto-tunnel-ipsec-cipher-0":     oriented; my_ip=unset; their_ip=unset; my_updown=/usr/libexec/updown_128t.sh --route y --kni paloalto-0;
    000 "paloalto-tunnel-ipsec-cipher-0":   xauth us:none, xauth them:none,  my_username=[any]; their_username=[any]
    000 "paloalto-tunnel-ipsec-cipher-0":   our auth:secret, their auth:secret
    000 "paloalto-tunnel-ipsec-cipher-0":   modecfg info: us:none, them:none, modecfg policy:push, dns:unset, domains:unset, banner:unset, cat:unset;
    000 "paloalto-tunnel-ipsec-cipher-0":   labeled_ipsec:no;
    000 "paloalto-tunnel-ipsec-cipher-0":   policy_label:unset;
    000 "paloalto-tunnel-ipsec-cipher-0":   ike_life: 28800s; ipsec_life: 3600s; replay_window: 32; rekey_margin: 540s; rekey_fuzz: 100%; keyingtries: 0;
    000 "paloalto-tunnel-ipsec-cipher-0":   retransmit-interval: 500ms; retransmit-timeout: 60s;
    000 "paloalto-tunnel-ipsec-cipher-0":   sha2-truncbug:no; initial-contact:no; cisco-unity:no; fake-strongswan:no; send-vendorid:no; send-no-esp-tfc:no;
    000 "paloalto-tunnel-ipsec-cipher-0":   policy: PSK+ENCRYPT+TUNNEL+UP+IKEV2_ALLOW+IKEV2_PROPOSE+SAREF_TRACK+IKE_FRAG_ALLOW+ESN_NO;
    000 "paloalto-tunnel-ipsec-cipher-0":   conn_prio: 0,0; interface: sfc-ipsec; metric: 100; mtu: unset; sa_prio:auto; sa_tfc:none;
    000 "paloalto-tunnel-ipsec-cipher-0":   nflog-group: unset; mark: 576996181/0xffffffff, 576996181/0xffffffff; vti-iface:vti576996181; vti-routing:yes; vti-shared:no; nic-offload:auto;
    000 "paloalto-tunnel-ipsec-cipher-0":   our idtype: ID_USER_FQDN; our id=0771@128t.com; their idtype: ID_USER_FQDN; their id=prisma@paloaltonetworks.com
    000 "paloalto-tunnel-ipsec-cipher-0":   dpd: action:restart; delay:10; timeout:15; nat-t: encaps:auto; nat_keepalive:yes; ikev1_natt:both
    000 "paloalto-tunnel-ipsec-cipher-0":   newest ISAKMP SA: #0; newest IPsec SA: #0;
    000 "paloalto-tunnel-ipsec-cipher-0":   IKE algorithms: AES_CBC_128-HMAC_SHA1-MODP1024
    000 "paloalto-tunnel-ipsec-cipher-0":   ESP algorithms: NULL-HMAC_MD5_96-MODP1024
    000  
    000 Total IPsec connections: loaded 1, active 0
    000  
    000 State Information: DDoS cookies not required, Accepting new IKE connections
    000 IKE SAs: total(1), half-open(1), open(0), authenticated(0), anonymous(0)
    000 IPsec SAs: total(0), authenticated(0), anonymous(0)
    000  
    000 #233: "paloalto-tunnel-ipsec-cipher-0":500 STATE_PARENT_I1 (sent v2I1, expected v2R1); EVENT_v2_RETRANSMIT in 15s; idle; import:admin initiate
    000 #233: pending Phase 2 for "paloalto-tunnel-ipsec-cipher-0" replacing #0
    000  
    000 Bare Shunt list:
    000  
    """

    ipsec_status_error = """
    whack: Pluto is not running (no "/run/pluto/pluto.ctl")
    """

    def setup(self):
        self.default_args(router="corp2", node="corp2A")
        sys.path.append(os.path.dirname(__file__))

    @pytest.mark.usefixtures("create_conductor_files")
    @pytest.mark.parametrize('test_instance,linux_run_output', [
        (
             {
                  "config"  : default_config,
                  "second_node" :  False,
                  "headline" : [
                      "0  Test IPSec Connections        : \x1b[31m\x1b[01mFAIL  1 nodes with inactive IPSec Connections\x1b[0m",
                      "   :                                     corp2A: IPSec Connections loaded=1 > active=0"
                  ]
             },
             {
                  "primary" : prepare_linux_output(ipsec_status_output),
                  "secondary" : []
             },
        ),
        (    
             {
                 "config"  : default_config,
                 "second_node" : True,
                 "headline" : [
                      "0  Test IPSec Connections        : \x1b[31m\x1b[01mFAIL  2 nodes with inactive IPSec Connections\x1b[0m",
                      "   :                                     corp2A: IPSec Connections loaded=1 > active=0",
                      "   :                                     corp2B: IPSec Connections loaded=1 > active=0"
                 ]
             },
             {
                  "primary" : prepare_linux_output(ipsec_status_output),
                  "secondary" : prepare_linux_output(ipsec_status_output)
             },
        ),
        (    
             {
                 "config"  : default_config,
                 "second_node" : True,
                 "headline" : [ 
                     "0  Test IPSec Connections        : \x1b[31m\x1b[01mFAIL  1 nodes with inactive IPSec Connections\x1b[0m",
                     '   :                                     whack: Pluto is not running (no "/run/pluto/pluto.ctl")'
                 ]
             },
             {
                  "primary" : prepare_linux_output(ipsec_status_ok),
                  "secondary" : prepare_linux_output(ipsec_status_error)
             },
        )

      ] 
   )

    def test_hosts_entry_exists(self, test_instance, local_context, capsys, mock_check_user, mock_linux_run):
        # config is irrelevant as test.run is not invoked...
        config = test_instance["config"]
        test_id = 0
        test = TestIPSecStatus.create_instance(test_id, config, self.args)
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
        output_index = 3
        for headline in test_instance["headline"]:
            assert all_lines[output_index] == headline
            output_index += 1

