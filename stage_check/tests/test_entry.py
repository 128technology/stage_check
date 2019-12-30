#!/usr/bin/env python3.6

import re
import json
import time
import datetime
import pprint
import sly
import pytest

try:
    from stage_check import EntryTester
except ImportError:
    import EntryTester

try:
    from stage_check import Output
except ImportError:
    import Output

test_data = [
    {
         "exclude_tests" : [
              "route/tenant == 'null-tenant'"
         ],
         "entry_tests" : { 
             "no_match" : {
                 "status" : "PASS"
             },
             "defaults" : {
                 "status" : "FAIL"
             },
             "tests" : [
                 {
                     "test"    : "@Loss_Of_Signal == 'Undefined'",
                     "status"  : "FAIL",
                     "format"  : "Test Undefined Variable", 
                 },
                 {
                     "test"    : "@Loss_Of_Signal == 'None'",
                     "status"  : "FAIL",
                     "format"  : "Test None Variable", 
                 },
                 {
                     "test"    : "@Loss_Of_Signal != 'Undefined' && Loss_Of_Signal > 1000",
                     "status"  : "FAIL",
                     "format"  : "Test Loss_Of_Signal > 1000", 
                 },
                 {
                     "test"    : "?gateway == False",
                     "status"  : "WARN",
                     "format"  : "Test Gateway Undefined", 
                 },
                 {
                     "test"   : "route/ipPrefix == '0.0.0.0/0' && gateway == '172.23.5.1' && route/l4Port < 1000",
                     "status" : "FAIL",
                     "format" : "Test Compound expression for {gateway}", 
                 },
                 {
                     "test"   : "route/ipPrefix == '0.0.0.0/8'",
                     "status" : "PASS",
                     "format" : "Test PASS for route/ipPrefix"
                 },
                 {
                     "test"   : "route/ipPrefix == '0.0.0.0/8'",
                     "status" : "FAIL",
                     "format" : "Test FAIL for route/ipPrefix"
                 },
                 {
                     "test"   : "route/tenant =~ 'bar$'",
                     "status" : "FAIL",
                     "format" : "Test regex match router/tenant"
                 },
                 {
                     "test"   : "Loss_Of_Signal < -99",
                     "status" : "FAIL",
                     "format" : "Test negative value"
                 }
             ]
         }
    }
]

@pytest.mark.parametrize('entry,expected', 
[
    (
        {
            "Loss_Of_Signal" : "50000",
            "serviceName": "internet_service",
            "route/ipPrefix": "0.0.0.0/0",
            "route/l4Port": 0,
            "route/l4PortUpper": 0,
            "route/protocol": 'null',
            "route/tenant": "null-tenant",
            "devicePort": 110,
            "gateway": "172.23.5.1",
            "nodeId": 2,
            "vlan": 1011,
            "deviceInterface": "PUBLIC_S",
            "networkInterface": "public_1011",
        },
        {
            "status" : "SKIP"
        }
    ),
    (
        {
            "Loss_Of_Signal" : "50000",
            "serviceName": "internet_service",
            "route/ipPrefix": "0.0.0.0/0",
            "route/l4Port": 0,
            "route/l4PortUpper": 0,
            "route/protocol": 'null',
            "route/tenant": "unconstrained.wireless",
            "devicePort": 110,
            "gateway": "172.23.5.1",
            "nodeId": 2,
            "vlan": 1011,
            "deviceInterface": "PUBLIC_S",
            "networkInterface": "public_1011"
        },
        {
             "status" : "FAIL"
        }
    ),
    (
        {
            "Loss_Of_Signal" : "100",
            "serviceName": "<ControlMessageService>",
            "route/ipPrefix": "0.0.0.0/8",
            "route/l4Port": 0,
            "route/l4PortUpper": 0,
            "route/protocol": 'null',
            "route/tenant": "<global>"
        },
        {
             "status" : "WARN"
        }
    ),
    (
        {
            "Loss_Of_Signal" : "100",
            "serviceName": "<ControlMessageService>",
            "route/ipPrefix": "0.0.0.0/8",
            "route/l4Port": 0,
            "route/l4PortUpper": 0,
            "route/protocol": 'null',
            "route/tenant": "<global>",
            "gateway": "172.23.5.1"
        },
        {
             "status" : "PASS"
        }
    ),
    (
        {
        },
        {
             "status" : "FAIL"
        }
   ),
    (
        {
             "Loss_Of_Signal" : None
        },
        {
            "status" : "FAIL",
        }
   ),
    (
        {
            "Loss_Of_Signal" : "500",
            "serviceName": "internet_service",
            "route/ipPrefix": "0.0.0.0/0",
            "route/l4Port": 1001,
            "route/l4PortUpper": 0,
            "route/protocol": 'null',
            "route/tenant": "bar",
            "devicePort": 110,
            "gateway": "172.23.5.1",
            "nodeId": 2,
            "vlan": 1011,
            "deviceInterface": "PUBLIC_S",
            "networkInterface": "public_1011",
        },
        {
            "status" : "FAIL",
            "format" : "Test regex match router/tenant"
        }
    ),
    (
        {
            "Loss_Of_Signal" : "600",
            "serviceName": "internet_service",
            "route/ipPrefix": "0.0.0.0/0",
            "route/l4Port": 1001,
            "route/l4PortUpper": 0,
            "route/protocol": 'null',
            "route/tenant": "nomatch",
            "devicePort": 110,
            "gateway": "172.23.5.1",
            "nodeId": 2,
            "vlan": 1011,
            "deviceInterface": "PUBLIC_S",
            "networkInterface": "public_1011",
        },
        {
            "status" : "PASS"
        }
    ),
    (
        {
            "Loss_Of_Signal" : -100,
            "serviceName": "internet_service",
            "route/ipPrefix": "0.0.0.0/0",
            "route/l4Port": 1001,
            "route/l4PortUpper": 0,
            "route/protocol": 'null',
            "route/tenant": "nomatch",
            "devicePort": 110,
            "gateway": "172.23.5.1",
            "nodeId": 2,
            "vlan": 1011,
            "deviceInterface": "PUBLIC_S",
            "networkInterface": "public_1011",
        },
        {
            "status" : "FAIL",
            "format" : "Test negative value"
        }
    )
]
)

def test_entry_matching(entry, expected):
    global test_data
    print("#######################################")
    pprint.pprint(entry)
    print("#######################################")
    parser = EntryTester.Parser(debug=True)
    matched = parser.exclude_entry(entry, test_data[0]["exclude_tests"])
    pprint.pprint(matched)
    if matched:
        # ensure we really meant this entry to be skipped
        assert expected["status"] == "SKIP"
        #print(f"Excluded entry:")
        #print(f"==================")
        #pprint.pprint(entry)
    else:
        test_status = parser.eval_entry_by_tests(entry, test_data[0]["entry_tests"]) 
        print(f"Matched Entry Status: {Output.status_to_text(test_status)}({test_status})")
        print("%%%#######################################")
        pprint.pprint(entry)
        print("%%%#######################################")
        assert Output.status_to_text(test_status) == expected["status"]
        if "format" in expected:
            assert entry["test_format"] == expected["format"]
     
