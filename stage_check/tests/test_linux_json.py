#!/usr/bin/env python3.6

######################################################################################
#   _            _       _ _                         _                               
#  | |_ ___  ___| |_    | (_)_ __  _   ___  __      (_)___  ___  _ __    _ __  _   _ 
#  | __/ _ \/ __| __|   | | | '_ \| | | \ \/ /      | / __|/ _ \| '_ \  | '_ \| | | |
#  | ||  __/\__ \ |_    | | | | | | |_| |>  <       | \__ \ (_) | | | |_| |_) | |_| |
#   \__\___||___/\__|___|_|_|_| |_|\__,_/_/\_\____ _/ |___/\___/|_| |_(_) .__/ \__, |
#                  |_____|                  |_____|__/                  |_|    |___/ 
##
######################################################################################

try:
    from stage_check import Linux
except ImportError:
    import Linux

import os
import re
import json
import time
import datetime
import pprint

import pytest

def set_local_timezone(tz_string):
    """
    Change the local timezone for testing...
    """
    os.environ['TZ'] = tz_string
    time.tzset()

def test_ethtool():
    ethtool_info_text = """
Settings for enp0s20f0:
    Supported ports: [ TP ]
    Supported link modes:   10baseT/Half 10baseT/Full 
                            100baseT/Half 100baseT/Full 
                            1000baseT/Full 
    Supported pause frame use: Symmetric
    Supports auto-negotiation: Yes
    Supported FEC modes: Not reported
    Advertised link modes:  10baseT/Half 10baseT/Full 
                            100baseT/Half 100baseT/Full 
                            1000baseT/Full 
    Advertised pause frame use: Symmetric
    Advertised auto-negotiation: Yes
    Advertised FEC modes: Not reported
    Speed: 1000Mb/s
    Duplex: Full
    Port: Twisted Pair
    PHYAD: 0
    Transceiver: internal
    Auto-negotiation: on
    MDI-X: on (auto)
    Supports Wake-on: pumbg
    Wake-on: g
    Current message level: 0x00000007 (7)
    drv probe link
    Link detected: yes
"""

    expected = {
     'Advertised_FEC_modes': 'Not reported',
     'Advertised_link_modes': '10baseT/Half 10baseT/Full ',
     'Advertised_pause_frame_use': 'Symmetric',
     'Current_message_level': '0x00000007 (7)',
     'Duplex': 'Full',
     'Link_detected': 'yes',
     'PHYAD': '0',
     'Port': 'Twisted Pair',
     'Speed': '1000Mb/s',
     'Supported_FEC_modes': 'Not reported',
     'Supported_link_modes': '10baseT/Half 10baseT/Full ',
     'Supported_pause_frame_use': 'Symmetric',
     'Supported_ports': '[ TP ]',
     'Transceiver': 'internal'
    }

    
    hw_dev_map = { 
        "__test__" : "enp0s20f0", 
        "default" : ":enp0s20f0"
     }
    
    e = Linux.Ethtool(hw_dev_map, debug=True)
    output = ethtool_info_text.splitlines()
    json_dict = e.convert_to_json(output)
    assert json_dict == expected
    #pprint.pprint(json_dict)

@pytest.mark.parametrize("tz_string", [
   "EDT", "UTC"
])
def test_coredumpctl_list(tz_string):
    coredumpctl_list_text = """
TIME                            PID   UID   GID SIG PRESENT EXE
Wed 2019-09-11 10:05:48 EDT    6355  1001  1001  11   /usr/bin/pdmTransportAgent
Wed 2019-09-11 20:58:20 EDT   10825  1001  1001  11   /usr/bin/pdmTransportAgent
Tue 2019-09-24 23:58:53 EDT    4994  1001  1001  11   /usr/bin/pdmTransportAgent
"""
    expected = [
    {
       'EPOCH_TIME': 1568210748,
       'EXE': '/usr/bin/pdmTransportAgent',
       'GID': '1001',
       'PID': '6355',
       'PRESENT': '',
       'SIG': '11',
       'TIME': 'Wed 2019-09-11 10:05:48 EDT',
       'UID': '1001'},
    {
       'EPOCH_TIME': 1568249900,
       'EXE': '/usr/bin/pdmTransportAgent',
       'GID': '1001',
       'PID': '10825',
       'PRESENT': '',
       'SIG': '11',
       'TIME': 'Wed 2019-09-11 20:58:20 EDT',
       'UID': '1001'},
    {
       'EPOCH_TIME': 1569383933,
       'EXE': '/usr/bin/pdmTransportAgent',
       'GID': '1001',
       'PID': '4994',
       'PRESENT': '',
       'SIG': '11',
       'TIME': 'Tue 2019-09-24 23:58:53 EDT',
       'UID': '1001'
    }
    ]

    set_local_timezone(tz_string)

    c = Linux.Coredumpctl(debug=True)
    output = coredumpctl_list_text.splitlines()
    json_dict = c.convert_to_json(output)

    # toothless test: Fix this to independently calculate days, hours, etc.
    list_len = len(c.cores_newer_than_secs(2000000))
    assert list_len == 0
    # print(f"Length: {x}")

    # toothless test: Fix this to independently calculate days, hours, etc.
    keys = [ 'EPOCH_TIME', 'TIME' ]
    for key in keys:   
        for entry in json_dict:
            assert key in entry
    for key in keys:
        for entry in expected:
            entry.pop(key, None)
        for entry in json_dict:
            entry.pop(key, None)

    assert json_dict == expected 
    #pprint.pprint(json_dict)

@pytest.mark.parametrize("tz_string", [
   "EDT", "UTC"
])
def test_systemctl_status(tz_string, capsys):
    systemctl_status_text = """
● 128T.service - 128T service
   Loaded: loaded (/usr/lib/systemd/system/128T.service; enabled; vendor preset: disabled)
   Active: active (running) since Wed 2019-09-11 00:25:02 EDT; 1 months 2 days ago
 Main PID: 28049 (processManager)
    Tasks: 2404
   Memory: 25.1G
   CGroup: /system.slice/128T.service
"""

    expected = [ {
    'Main_PID': '28049',
    'Main_Process': 'processManager',
    'Tasks' : 2404,
    'Memory' : 25.1,
    'MemoryModifier' : 'GB',
    'epoch_time': 1568161502.0,
    'service' : '128T',  
    'state_1': 'active',
    'state_2': 'running',
    'time': 'Wed 2019-09-11 00:25:02 EDT',
    'uptime_days': 92,
    'uptime_hours': 20,
    'uptime_minutes': 19,
    'uptime_seconds': 22
    } ]

    set_local_timezone(tz_string)

    s = Linux.SystemctlStatus(debug=True)
    output = systemctl_status_text.splitlines()
    json_list = s.convert_to_json(output)

    captured = capsys.readouterr()
    all_lines = captured.out.splitlines()

    # toothless test: Fix this to independently calculate days, hours, etc.
    keys = [ 'epoch_time', 'uptime_days', 'uptime_hours', 'uptime_minutes', 'uptime_seconds' ]
    for key in keys:
        for entry in json_list:
            assert key in entry
    for key in keys:
        for entry in expected:
            entry.pop(key, None)
        for entry in json_list:
            entry.pop(key, None)

    assert json_list == expected
    #pprint.pprint(json_dict)

def test_uptime_1():
    uptime_text = """
    12:34:35 up 58 days, 10:18,  5 users,  load average: 0.76, 1.28, 1.19  
    """
    expected = {
    'load_1': 0.76,
    'load_15': 1.19,
    'load_5': 1.28,
    'uptime_as_seconds': 5048280,
    'uptime_days': 58,
    'uptime_hours': 10,
    'uptime_minutes': 18,
    'users': 5
     }
 
    u = Linux.Uptime(debug=True)
    output = uptime_text.splitlines()
    json_dict = u.convert_to_json(output)
    assert json_dict == expected
    #pprint.pprint(json_dict)

def test_uptime_2():
    uptime_text = """
    23:11:40 up  8:16,  1 user,  load average: 2.71, 2.30, 2.01 
    """
    expected = {
    'load_1': 2.71,
    'load_15': 2.01,
    'load_5': 2.3,
    'uptime_as_seconds': 29760,
    'uptime_days': 0,
    'uptime_hours': 8,
    'uptime_minutes': 16,
    'users': 1
    }

    u = Linux.Uptime(debug=True)
    output = uptime_text.splitlines()
    json_dict = u.convert_to_json(output)
    assert json_dict == expected
    #pprint.pprint(json_dict)

def test_uptime_3():
    uptime_text = """
    02:25:02 up 73 days, 40 min,  1 user,  load average: 2.01, 1.56, 1.60
    """

    expected = {
    'load_1': 2.01,
    'load_15': 1.6,
    'load_5': 1.56,
    'uptime_as_seconds': 6309600,
    'uptime_days': 73,
    'uptime_hours': 0,
    'uptime_minutes': 40,
    'users': 1
    }

    u = Linux.Uptime(debug=True)
    output = uptime_text.splitlines()
    json_dict = u.convert_to_json(output)
    assert json_dict == expected
    #pprint.pprint(json_dict)

def test_uptime_4():
    uptime_text = """
    20:19:54 up 54 min,  4 users,  load average: 1.69, 1.96, 1.92
    """
    
    expected = {
    'load_1': 1.69,
    'load_15': 1.92,
    'load_5': 1.96,
    'uptime_as_seconds': 3240,
    'uptime_days': 0,
    'uptime_hours': 0,
    'uptime_minutes': 54,
    'users': 4
     }

    u = Linux.Uptime(debug=True)
    output = uptime_text.splitlines()
    json_dict = u.convert_to_json(output)
    assert json_dict == expected
    #pprint.pprint(json_dict)

def test_BGP_summary():
    bgp_summary_text="""

IPv4 Unicast Summary:
BGP router identifier 10.53.151.115, local AS number 65310 vrf-id 0
BGP table version 415
RIB entries 79, using 12 KiB of memory
Peers 2, using 41 KiB of memory

Neighbor        V         AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd
172.27.232.15   4      64794  317684  264701        0    0    0 01w6d21h           40
172.27.233.15   4      64894  260245  217685        0    0    0 3d15h04m           40

Total number of neighbors 2
"""

    expected = [
    {
        'AS': 64794,
        'InQ': 0,
        'MsgRcvd': 317684,
        'MsgSent': 264701,
        'Neighbor': '172.27.232.15',
        'OutQ': 0,
        'PfxRcvd': 40,
        'TblVer': 0,
        'Up/Down': '01w6d21h',
        'Version': 4
    },
    {
        'AS': 64894,
        'InQ': 0,
        'MsgRcvd': 260245,
        'MsgSent': 217685,
        'Neighbor': '172.27.233.15',
        'OutQ': 0,
        'PfxRcvd': 40,
        'TblVer': 0,
        'Up/Down': '3d15h04m',
        'Version': 4
    }
   ]

    b = Linux.BGPSummary(debug=True)
    output = bgp_summary_text.splitlines()
    json_dict = b.convert_to_json(output)
    assert json_dict == expected
    #pprint.pprint(json_dict)

def test_IPA():
    ip_a_text = """
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: enp0s20f0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq master habr state UP group default qlen 1000
    link/ether 00:90:0b:5b:80:d7 brd ff:ff:ff:ff:ff:ff
6: enp1s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 00:90:0b:5b:80:db brd ff:ff:ff:ff:ff:ff
7: enp2s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 00:90:0b:5b:80:dc brd ff:ff:ff:ff:ff:ff
9: habr: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 00:90:0b:5b:80:d7 brd ff:ff:ff:ff:ff:ff
    inet 30.254.255.1/30 brd 30.254.255.3 scope global noprefixroute habr
       valid_lft forever preferred_lft forever
    inet6 fe80::290:bff:fe5b:80d7/64 scope link 
       valid_lft forever preferred_lft forever
23: kni20: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UNKNOWN group default qlen 1000
    link/ether 42:3d:6f:4d:83:70 brd ff:ff:ff:ff:ff:ff
    inet 169.254.1.2/30 brd 169.254.1.3 scope global kni20
       valid_lft forever preferred_lft forever
    inet6 fe80::403d:6fff:fe4d:8370/64 scope link 
       valid_lft forever preferred_lft forever
24: kni254: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UNKNOWN group default qlen 1000
    link/ether 6e:8e:df:e3:4e:ae brd ff:ff:ff:ff:ff:ff
    inet 169.254.127.127/31 brd 255.255.255.255 scope global kni254
       valid_lft forever preferred_lft forever
    inet6 fe80::6c8e:dfff:fee3:4eae/64 scope link 
       valid_lft forever preferred_lft forever
"""
    expected = [
    {
       'Flags_ALLMULTI': False,
       'Flags_AUTOMEDIA': False,
       'Flags_BROADCAST': False,
       'Flags_DEBUG': False,
       'Flags_DORMANT': False,
       'Flags_DYNAMIC': False,
       'Flags_ECHO': False,
       'Flags_LOOPBACK': True,
       'Flags_LOWER_UP': True,
       'Flags_MASTER': False,
       'Flags_MULTICAST': False,
       'Flags_NOARP': False,
       'Flags_NOTRAILERS': False,
       'Flags_POINTTOPOINT': False,
       'Flags_PORTSEL': False,
       'Flags_PROMISC': False,
       'Flags_RUNNING': False,
       'Flags_SLAVE': False,
       'Flags_UP': True,
       'device': 'lo',
       'group': 'default',
       'index': 1,
       'mtu': '65536',
       'qdisc': 'noqueue',
       'qlen': '1000',
       'state': 'UNKNOWN'
   },
   {
       'Flags_ALLMULTI': False,
       'Flags_AUTOMEDIA': False,
       'Flags_BROADCAST': True,
       'Flags_DEBUG': False,
       'Flags_DORMANT': False,
       'Flags_DYNAMIC': False,
       'Flags_ECHO': False,
       'Flags_LOOPBACK': False,
       'Flags_LOWER_UP': True,
       'Flags_MASTER': False,
       'Flags_MULTICAST': True,
       'Flags_NOARP': False,
       'Flags_NOTRAILERS': False,
       'Flags_POINTTOPOINT': False,
       'Flags_PORTSEL': False,
       'Flags_PROMISC': False,
       'Flags_RUNNING': False,
       'Flags_SLAVE': False,
       'Flags_UP': True,
       'broadcast-mac': 'ff:ff:ff:ff:ff:ff',
       'device': 'enp0s20f0',
       'group': 'default',
       'index': 2,
       'mac': '00:90:0b:5b:80:dc',
       'master': 'habr',
       'mtu': '1500',
       'qdisc': 'mq',
       'qlen': '1000',
       'state': 'UP'
   },
   {
       'Flags_ALLMULTI': False,
       'Flags_AUTOMEDIA': False,
       'Flags_BROADCAST': True,
       'Flags_DEBUG': False,
       'Flags_DORMANT': False,
       'Flags_DYNAMIC': False,
       'Flags_ECHO': False,
       'Flags_LOOPBACK': False,
       'Flags_LOWER_UP': True,
       'Flags_MASTER': False,
       'Flags_MULTICAST': True,
       'Flags_NOARP': False,
       'Flags_NOTRAILERS': False,
       'Flags_POINTTOPOINT': False,
       'Flags_PORTSEL': False,
       'Flags_PROMISC': False,
       'Flags_RUNNING': False,
       'Flags_SLAVE': False,
       'Flags_UP': True,
       'address': '30.254.255.1',
       'address-prefix': '30',
       'broadcast-address': '30.254.255.3',
       'broadcast-mac': 'ff:ff:ff:ff:ff:ff',
       'device': 'habr',
       'group': 'default',
       'index': 9,
       'mac': '00:90:0b:5b:80:d7',
       'mtu': '1500',
       'qdisc': 'noqueue',
       'qlen': '1000',
       'state': 'UP'
    },
    {
       'Flags_ALLMULTI': False,
       'Flags_AUTOMEDIA': False,
       'Flags_BROADCAST': True,
       'Flags_DEBUG': False,
       'Flags_DORMANT': False,
       'Flags_DYNAMIC': False,
       'Flags_ECHO': False,
       'Flags_LOOPBACK': False,
       'Flags_LOWER_UP': True,
       'Flags_MASTER': False,
       'Flags_MULTICAST': True,
       'Flags_NOARP': False,
       'Flags_NOTRAILERS': False,
       'Flags_POINTTOPOINT': False,
       'Flags_PORTSEL': False,
       'Flags_PROMISC': False,
       'Flags_RUNNING': False,
       'Flags_SLAVE': False,
       'Flags_UP': True,
       'address': '169.254.1.2',
       'address-prefix': '30',
       'broadcast-address': '169.254.1.3',
       'broadcast-mac': 'ff:ff:ff:ff:ff:ff',
       'device': 'kni20',
       'group': 'default',
       'index': 23,
       'mac': '42:3d:6f:4d:83:70',
       'mtu': '1500',
       'qdisc': 'pfifo_fast',
       'qlen': '1000',
       'state': 'UNKNOWN'
    },
    {
       'Flags_ALLMULTI': False,
       'Flags_AUTOMEDIA': False,
       'Flags_BROADCAST': True,
       'Flags_DEBUG': False,
       'Flags_DORMANT': False,
       'Flags_DYNAMIC': False,
       'Flags_ECHO': False,
       'Flags_LOOPBACK': False,
       'Flags_LOWER_UP': True,
       'Flags_MASTER': False,
       'Flags_MULTICAST': True,
       'Flags_NOARP': False,
       'Flags_NOTRAILERS': False,
       'Flags_POINTTOPOINT': False,
       'Flags_PORTSEL': False,
       'Flags_PROMISC': False,
       'Flags_RUNNING': False,
       'Flags_SLAVE': False,
       'Flags_UP': True,
       'address': '169.254.127.127',
       'address-prefix': '31',
       'broadcast-address': '255.255.255.255',
       'broadcast-mac': 'ff:ff:ff:ff:ff:ff',
       'device': 'kni254',
       'group': 'default',
       'index': 24,
       'mac': '6e:8e:df:e3:4e:ae',
       'mtu': '1500',
       'qdisc': 'pfifo_fast',
       'qlen': '1000',
       'state': 'UNKNOWN'
     }
    ]

    i = Linux.IPA(debug=True)
    output = ip_a_text.splitlines()
    json_dict = i.convert_to_json(output)
    assert json_dict == expected
    #pprint.pprint(json_dict)

def test_IPA_ns_lte():
    netns_lte_ip_a_text = """
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
8: enp0s22u1u2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 5e:a9:e0:9f:a4:19 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.128/24 brd 192.168.1.255 scope global enp0s22u1u2
       valid_lft forever preferred_lft forever
    inet6 2600:380:9e1e:6d2a:5ca9:e0ff:fe9f:a419/64 scope global mngtmpaddr dynamic 
       valid_lft 86364sec preferred_lft 14364sec
    inet6 fe80::5ca9:e0ff:fe9f:a419/64 scope link 
       valid_lft forever preferred_lft forever
25: lte: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UNKNOWN group default qlen 1000
    link/ether fa:67:97:45:f3:e1 brd ff:ff:ff:ff:ff:ff
    inet 169.254.151.114/31 brd 255.255.255.255 scope global lte
       valid_lft forever preferred_lft forever
    inet6 fe80::f867:97ff:fe45:f3e1/64 scope link 
       valid_lft forever preferred_lft forever
"""
    expected = [
    {
        'Flags_ALLMULTI': False,
        'Flags_AUTOMEDIA': False,
        'Flags_BROADCAST': False,
        'Flags_DEBUG': False,
        'Flags_DORMANT': False,
        'Flags_DYNAMIC': False,
        'Flags_ECHO': False,
        'Flags_LOOPBACK': True,
        'Flags_LOWER_UP': False,
        'Flags_MASTER': False,
        'Flags_MULTICAST': False,
        'Flags_NOARP': False,
        'Flags_NOTRAILERS': False,
        'Flags_POINTTOPOINT': False,
        'Flags_PORTSEL': False,
        'Flags_PROMISC': False,
        'Flags_RUNNING': False,
        'Flags_SLAVE': False,
        'Flags_UP': False,
        'device': 'lo',
        'group': 'default',
        'index': 1,
        'mtu': '65536',
        'qdisc': 'noop',
        'qlen': '1000',
        'state': 'DOWN'
    },
    {
        'Flags_ALLMULTI': False,
        'Flags_AUTOMEDIA': False,
        'Flags_BROADCAST': True,
        'Flags_DEBUG': False,
        'Flags_DORMANT': False,
        'Flags_DYNAMIC': False,
        'Flags_ECHO': False,
        'Flags_LOOPBACK': False,
        'Flags_LOWER_UP': True,
        'Flags_MASTER': False,
        'Flags_MULTICAST': True,
        'Flags_NOARP': False,
        'Flags_NOTRAILERS': False,
        'Flags_POINTTOPOINT': False,
        'Flags_PORTSEL': False,
        'Flags_PROMISC': False,
        'Flags_RUNNING': False,
        'Flags_SLAVE': False,
        'Flags_UP': True,
        'address': '192.168.1.128',
        'address-prefix': '24',
        'broadcast-address': '192.168.1.255',
        'broadcast-mac': 'ff:ff:ff:ff:ff:ff',
        'device': 'enp0s22u1u2',
        'group': 'default',
        'index': 8,
        'mac': '5e:a9:e0:9f:a4:19',
        'mtu': '1500',
        'qdisc': 'pfifo_fast',
        'qlen': '1000',
        'state': 'UP'
    },
    {
        'Flags_ALLMULTI': False,
        'Flags_AUTOMEDIA': False,
        'Flags_BROADCAST': True,
        'Flags_DEBUG': False,
        'Flags_DORMANT': False,
        'Flags_DYNAMIC': False,
        'Flags_ECHO': False,
        'Flags_LOOPBACK': False,
        'Flags_LOWER_UP': True,
        'Flags_MASTER': False,
        'Flags_MULTICAST': True,
        'Flags_NOARP': False,
        'Flags_NOTRAILERS': False,
        'Flags_POINTTOPOINT': False,
        'Flags_PORTSEL': False,
        'Flags_PROMISC': False,
        'Flags_RUNNING': False,
        'Flags_SLAVE': False,
        'Flags_UP': True,
        'address': '169.254.151.114',
        'address-prefix': '31',
        'broadcast-address': '255.255.255.255',
        'broadcast-mac': 'ff:ff:ff:ff:ff:ff',
        'device': 'lte',
        'group': 'default',
        'index': 25,
        'mac': 'fa:67:97:45:f3:e1',
        'mtu': '1500',
        'qdisc': 'pfifo_fast',
        'qlen': '1000',
        'state': 'UNKNOWN'
      }
    ]

    i = Linux.IPA(debug=True)
    output = netns_lte_ip_a_text.splitlines()
    json_list = i.convert_to_json(output)
    assert json_list == expected
    #pprint.pprint(json_list)

def test_T1Detail_1():
    t1_detail_text_1 = """
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
    expected =  {
       'AIS': 'OFF',
       'ALOS': 'OFF',
       'Bit_Errors_CRC6/Ft/Fs': '16',
       'LOF': 'OFF',
       'LOS': 'OFF',
       'Line_Code_Violation': '0',
       'Loss_of_Signal': 'OFF',
       'Open_Circuit': 'OFF',
       'Out_of_Frame_Errors': '7',
       'RAI': 'OFF',
       'RED': 'OFF',
       'Rx_Level_High': '-2.5',
       'Short_Circuit': 'OFF',
       'Sync_Errors': '0',
       'TxAIS': 'OFF',
       'YEL': 'OFF'
    } 

    t = Linux.T1Detail(debug=True)
    output = t1_detail_text_1.splitlines()
    json_dict = t.convert_to_json(output)
    assert json_dict[0] == expected
    # pprint.pprint(json_dict)

def test_T1Detail_2():
    t1_detail_text_2 = """
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


     Rx Level  : -7.5db to -10db
"""
    expected = {
       'AIS': 'OFF',
       'ALOS': 'OFF',
       'Bit_Errors_CRC6/Ft/Fs': '16',
       'LOF': 'OFF',
       'LOS': 'OFF',
       'Line_Code_Violation': '0',
       'Loss_of_Signal': 'OFF',
       'Open_Circuit': 'OFF',
       'Out_of_Frame_Errors': '7',
       'RAI': 'OFF',
       'RED': 'OFF',
       'Rx_Level_High': '-7.5',
       'Rx_Level_Low': '-10',
       'Short_Circuit': 'OFF',
       'Sync_Errors': '0',
       'TxAIS': 'OFF',
       'YEL': 'OFF'
    } 
    t = Linux.T1Detail(debug=True)
    output = t1_detail_text_2.splitlines()
    json_list = t.convert_to_json(output)
    assert json_list[0] == expected
    # pprint.pprint(json_dict)

def test_LogfilesSince():
    log_files_since_text = """
  JSON: {"files": [{"file": "/var/log/128technology/highwayManager.1.log", "start": "Oct 19 19:53:45", "end": "Oct 19 19:56:14"}, {"file": "/var/log/128technology/highwayManager.22.log", "start": "Oct 29 21:02:28", "end": "Oct 29 21:04:55"}, {"file": "/var/log/128technology/highwayManager.21.log", "start": "Oct 29 21:04:55", "end": "Oct 29 21:07:20"}, {"file": "/var/log/128technology/highwayManager.19.log", "start": "Oct 29 21:09:45", "end": "Oct 29 21:12:15"}, {"file": "/var/log/128technology/highwayManager.log", "start": "Oct 29 21:56:14", "end": "Oct 29 21:56:43"}, {"file": "/var/log/128technology/highwayManager.20.log", "start": "Oct 29 21:07:20", "end": "Oct 29 21:09:45"}, {"file": "/var/log/128technology/highwayManager.11.log", "start": "Oct 29 21:29:20", "end": "Oct 29 21:31:45"}, {"file": "/var/log/128technology/highwayManager.10.log", "start": "Oct 29 21:31:45", "end": "Oct 29 21:34:15"}, {"file": "/var/log/128technology/highwayManager.18.log", "start": "Oct 29 21:12:15", "end": "Oct 29 21:14:40"}, {"file": "/var/log/128technology/highwayManager.23.log", "start": "Oct 29 21:00:00", "end": "Oct 29 21:02:28"}, {"file": "/var/log/128technology/highwayManager.16.log", "start": "Oct 29 21:17:05", "end": "Oct 29 21:19:35"}, {"file": "/var/log/128technology/highwayManager.14.log", "start": "Oct 29 21:22:00", "end": "Oct 29 21:24:25"}, {"file": "/var/log/128technology/highwayManager.12.log", "start": "Oct 29 21:26:55", "end": "Oct 29 21:29:20"}, {"file": "/var/log/128technology/highwayManager.3.log", "start": "Oct 29 21:48:54", "end": "Oct 29 21:51:20"}, {"file": "/var/log/128technology/highwayManager.5.log", "start": "Oct 29 21:44:00", "end": "Oct 29 21:46:25"}, {"file": "/var/log/128technology/highwayManager.24.log", "start": "Oct 29 20:57:35", "end": "Oct 29 21:00:00"}, {"file": "/var/log/128technology/highwayManager.2.log", "start": "Oct 29 21:51:20", "end": "Oct 29 21:53:45"}, {"file": "/var/log/128technology/highwayManager.7.log", "start": "Oct 29 21:39:05", "end": "Oct 29 21:41:35"}, {"file": "/var/log/128technology/highwayManager.6.log", "start": "Oct 29 21:41:35", "end": "Oct 29 21:44:00"}, {"file": "/var/log/128technology/highwayManager.15.log", "start": "Oct 29 21:19:35", "end": "Oct 29 21:22:00"}, {"file": "/var/log/128technology/highwayManager.17.log", "start": "Oct 29 21:14:40", "end": "Oct 29 21:17:05"}, {"file": "/var/log/128technology/highwayManager.13.log", "start": "Oct 29 21:24:25", "end": "Oct 29 21:26:55"}, {"file": "/var/log/128technology/highwayManager.9.log", "start": "Oct 29 21:34:15", "end": "Oct 29 21:36:40"}, {"file": "/var/log/128technology/highwayManager.8.log", "start": "Oct 29 21:36:40", "end": "Oct 29 21:39:05"}, {"file": "/var/log/128technology/highwayManager.4.log", "start": "Oct 29 21:46:25", "end": "Oct 29 21:48:54"}], "now": "Oct 29 21:56:44 2019 [UTC]"}
"""
    expected =  [
       {'end': 'Oct 29 21:56:43',
       'file': '/var/log/128technology/highwayManager.log',
       'start': 'Oct 29 21:56:14'},
       {'end': 'Oct 29 21:53:45',
        'file': '/var/log/128technology/highwayManager.2.log',
        'start': 'Oct 29 21:51:20'},
       {'end': 'Oct 29 21:51:20',
        'file': '/var/log/128technology/highwayManager.3.log',
        'start': 'Oct 29 21:48:54'},
       {'end': 'Oct 29 21:48:54',
        'file': '/var/log/128technology/highwayManager.4.log',
        'start': 'Oct 29 21:46:25'},
       {'end': 'Oct 29 21:46:25',
        'file': '/var/log/128technology/highwayManager.5.log',
        'start': 'Oct 29 21:44:00'},
       {'end': 'Oct 29 21:44:00',
        'file': '/var/log/128technology/highwayManager.6.log',
        'start': 'Oct 29 21:41:35'},
       {'end': 'Oct 29 21:41:35',
        'file': '/var/log/128technology/highwayManager.7.log',
        'start': 'Oct 29 21:39:05'},
       {'end': 'Oct 29 21:39:05',
        'file': '/var/log/128technology/highwayManager.8.log',
        'start': 'Oct 29 21:36:40'},
       {'end': 'Oct 29 21:36:40',
        'file': '/var/log/128technology/highwayManager.9.log',
        'start': 'Oct 29 21:34:15'},
       {'end': 'Oct 29 21:34:15',
        'file': '/var/log/128technology/highwayManager.10.log',
        'start': 'Oct 29 21:31:45'},
       {'end': 'Oct 29 21:31:45',
        'file': '/var/log/128technology/highwayManager.11.log',
        'start': 'Oct 29 21:29:20'},
       {'end': 'Oct 29 21:29:20',
        'file': '/var/log/128technology/highwayManager.12.log',
        'start': 'Oct 29 21:26:55'},
       {'end': 'Oct 29 21:26:55',
        'file': '/var/log/128technology/highwayManager.13.log',
        'start': 'Oct 29 21:24:25'},
       {'end': 'Oct 29 21:24:25',
        'file': '/var/log/128technology/highwayManager.14.log',
        'start': 'Oct 29 21:22:00'},
       {'end': 'Oct 29 21:22:00',
        'file': '/var/log/128technology/highwayManager.15.log',
        'start': 'Oct 29 21:19:35'},
       {'end': 'Oct 29 21:19:35',
        'file': '/var/log/128technology/highwayManager.16.log',
        'start': 'Oct 29 21:17:05'},
       {'end': 'Oct 29 21:17:05',
        'file': '/var/log/128technology/highwayManager.17.log',
        'start': 'Oct 29 21:14:40'},
       {'end': 'Oct 29 21:14:40',
        'file': '/var/log/128technology/highwayManager.18.log',
        'start': 'Oct 29 21:12:15'},
       {'end': 'Oct 29 21:12:15',
        'file': '/var/log/128technology/highwayManager.19.log',
        'start': 'Oct 29 21:09:45'},
       {'end': 'Oct 29 21:09:45',
        'file': '/var/log/128technology/highwayManager.20.log',
        'start': 'Oct 29 21:07:20'},
       {'end': 'Oct 29 21:07:20',
        'file': '/var/log/128technology/highwayManager.21.log',
        'start': 'Oct 29 21:04:55'},
       {'end': 'Oct 29 21:04:55',
        'file': '/var/log/128technology/highwayManager.22.log',
        'start': 'Oct 29 21:02:28'},
       {'end': 'Oct 29 21:02:28',
        'file': '/var/log/128technology/highwayManager.23.log',
        'start': 'Oct 29 21:00:00'},
       {'end': 'Oct 29 21:00:00',
        'file': '/var/log/128technology/highwayManager.24.log',
        'start': 'Oct 29 20:57:35'}
    ]
    # This is a lame test, need actual log files to process
    l = Linux.LogFilesSince(debug=True, past_hours=1)
    output = log_files_since_text.splitlines()
    json_dict = l.convert_to_json(output)
    assert json_dict == expected
    # pprint.pprint(json_dict)

def test_LogFileMatches():
    log_file_matches_text = """
JSON: {"matches": [{"pindex": 0, "pattern": "LPA.*?observer", "matches": 1}, {"pindex": 1, "pattern": "HWMC", "matches": 0}], "total_matches": 1, "total_files": 1, "total_lines": 51159, "matching_lines": 1, "not_matching_lines": 51158, "matching_files": 1}
"""
    expected={'matches': [{'matches': 1, 'pattern': 'LPA.*?observer', 'pindex': 0},
                          {'matches': 0, 'pattern': 'HWMC', 'pindex': 1}],
              'matching_files': 1,
              'matching_lines': 1,
              'not_matching_lines': 51158,
              'total_files': 1,
              'total_lines': 51159,
              'total_matches': 1}
    l = Linux.LogFileMatches(debug=True)
    output = log_file_matches_text.splitlines()
    json_dict = l.convert_to_json(output)
    assert json_dict == expected
    #pprint.pprint(json_dict)

def test_hosts_json():
    etc_hosts_text = """
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6

# BEGIN ANSIBLE MANAGED BLOCK
1.2.3.4     Fubar 
# END ANSIBLE MANAGED BLOCK
"""    
    expected = [ {
        "localhost" : [ '127.0.0.1', '::1' ],
        "localhost.localdomain" : [ '127.0.0.1', '::1' ],
        "localhost4" : [ '127.0.0.1' ],
        "localhost4.localdomain4" : [ '127.0.0.1' ],
        "localhost6" : [ '::1' ],
        "localhost6.localdomain6" : [ '::1' ],
        "Fubar" : [ '1.2.3.4' ]
    } ]   
   
    h = Linux.HostsFile(debug=True)
    output = etc_hosts_text.splitlines()
    json_dict = h.convert_to_json(output)
    #assert False, pprint.pformat(json_dict)
    #assert json_dict == expected
    assert h.get_first_address("Fubar") == "1.2.3.4"
    assert h.get_ipv4_address("localhost") == "127.0.0.1"
    assert h.get_ipv6_address("localhost") == "::1"

def test_lte_info_json():
    """
    Because the lte scripts output is already json, this is
    not much of a text...
    """
    lte_info_text="""
    {
        "LTE": {
            "Active Profile From Config": {
                "PDP type": "ipv4",
                "APN": "abc",
                "Auth": "none"
            },
            "usb-port": "/dev/ttyUSB5",
            "Packet Stats": "Error Retrieving Information",
            "RSSI Signal Strength": "-48 dBm",
            "Enabled LTE Bands": "2, 4, 12",
            "Signal Strength": "excellent",
            "Default Profile From SIM": {
                "PDP type": "ipv4-or-ipv6",
                "APN": "broadband",
                "Auth": "none"
            },
            "failure": {
                "code": 33,
                "attempt": 95,
                "reason": "option-unsubscribed",
                "last-failure-time": "Tue Apr  7 12:47:58 2020",
                "type": 6,
                "next-retry-time": "Tue Apr  7 13:47:58 2020"
            },
            "Radio Interface": "lte",
            "Registration Status": "registered",
            "Current Ipv4 Settings": "Error Retrieving Information",
            "SNR Signal Strength": "12.2 dB",
            "Carrier": "AT&T",
            "Connection Status": "disconnected"
        }
    }
    """
    expected = {
        "Active_Profile_From_Config": {
            "PDP_type": "ipv4",
            "APN": "abc",
            "Auth": "none"
        },
        "usb-port": "/dev/ttyUSB5",
        "Packet_Stats": "Error Retrieving Information",
        "RSSI_Signal_Strength": -48.0,
        "Enabled_LTE_Bands": "2, 4, 12",
        "Signal_Strength": "excellent",
        "Default_Profile_From_SIM": {
        "PDP_type": "ipv4-or-ipv6",
            "APN": "broadband",
            "Auth": "none"
        },
        "failure": {
            "code": 33,
            "attempt": 95,
            "reason": "option-unsubscribed",
            "last-failure-time": "Tue Apr  7 12:47:58 2020",
            "type": 6,
            "next-retry-time": "Tue Apr  7 13:47:58 2020"
        },
        "Radio_Interface": "lte",
        "Registration_Status": "registered",
        "Current_Ipv4_Settings": "Error Retrieving Information",
        "SNR_Signal_Strength": 12.2,
        "Carrier": "AT&T",
        "Connection_Status": "disconnected"
    }

    l = Linux.LteInfo(debug=True)
    output = lte_info_text.splitlines()
    json_dict = l.convert_to_json(output)
    assert json_dict == expected 

    expected_2 = [ {
        "Active_Profile_From_Config": {
            "PDP_type": "ipv4",
            "APN": "abc",
            "Auth": "none"
        },
        "usb-port": "/dev/ttyUSB5",
        "Packet_Stats": "Error Retrieving Information",
        "RSSI_Signal_Strength": -48.0,
        "Enabled_LTE_Bands": "2, 4, 12",
        "Signal_Strength": "excellent",
        "Default_Profile_From_SIM": {
        "PDP_type": "ipv4-or-ipv6",
            "APN": "broadband",
            "Auth": "none"
        },
        "failure": {
            "code": 33,
            "attempt": 95,
            "reason": "option-unsubscribed",
            "last-failure-time": "Tue Apr  7 12:47:58 2020",
            "type": 6,
            "next-retry-time": "Tue Apr  7 13:47:58 2020"
        },
        "Radio_Interface": "lte",
        "Registration_Status": "registered",
        "Current_Ipv4_Settings": "Error Retrieving Information",
        "SNR_Signal_Strength": 12.2,
        "Carrier": "AT&T",
        "Connection_Status": "disconnected",
        "namespace" : "lte",
        "linux_device" : "lte"
    } ]

    l = Linux.LteInfos(debug=True)
    json_output = [ { "output" : lte_info_text, "namespace" : "lte", "device" :  "lte" } ]
    json_string = json.dumps(json_output, indent=None)
    test_string = "JSON: " + json_string
    json_list = l.convert_to_json([ test_string ])
    assert json_list == expected_2

def test_lshw_to_json():
    """
    Because the lte scripts output is already json, this is
    not much of a text...
    """
    lshw_output="""
        {
            "id" : "site0001p1a",
            "class" : "system",
            "claimed" : true,
            "handle" : "DMI:0001",
            "description" : "Desktop Computer",
            "product" : "NCA-1515B-WB1 (Default String)",
            "vendor" : "Default string",
            "version" : "V0.3",
            "serial" : "LR202007007444",
            "width" : 64,
            "configuration" : {
                "boot" : "normal",
                "chassis" : "desktop",
                "family" : "Default String",
                "sku" : "Default String",
                "uuid" : "00020003-0004-0005-0006-000700080009"
            },
           "capabilities" : {
               "smbios-3.0.0" : "SMBIOS version 3.0.0",
               "dmi-3.0.0" : "DMI version 3.0.0",
               "smp" : "Symmetric Multi-Processing",
               "vsyscall32" : "32-bit processes"
            },
            "children" : [
                {
                    "id" : "pnp00:00",
                    "class" : "system",
                    "claimed" : true,
                    "product" : "PnP device PNP0c01",
                    "physid" : "1",
                    "configuration" : {
                        "driver" : "system"
                    },
                    "capabilities" : {
                        "pnp" : true
                    }
               },
               {
                   "id" : "pnp00:01",
                   "class" : "system",
                   "claimed" : true,
                   "product" : "PnP device PNP0c02",
                   "physid" : "2",
                   "configuration" : {
                       "driver" : "system"
                   },
                   "capabilities" : {
                       "pnp" : true
                   }
               },
               {
                  "id" : "pnp00:02",
                  "class" : "system",
                  "claimed" : true,
                  "product" : "PnP device PNP0b00",
                  "physid" : "3",
                  "configuration" : {
                     "driver" : "rtc_cmos"
                  },
                  "capabilities" : {
                     "pnp" : true
                   }
               },
               {
                  "id" : "pnp00:03",
                  "class" : "system",
                  "claimed" : true,
                  "product" : "PnP device PNP0c02",
                  "physid" : "4",
                  "configuration" : {
                       "driver" : "system"
                  },
                  "capabilities" : {
                       "pnp" : true
                  }
              },
          {
             "id" : "pnp00:06",
             "class" : "system",
             "claimed" : true,
             "product" : "PnP device PNP0c02",
             "physid" : "7",
             "configuration" : {
                 "driver" : "system"
             },
             "capabilities" : {
                  "pnp" : true
             }
          }
       ]
    }
    """

    lshw_expected = {
            "id" : "site0001p1a",
            "class" : "system",
            "claimed" : True,
            "handle" : "DMI:0001",
            "description" : "Desktop Computer",
            "product" : "NCA-1515B-WB1 (Default String)",
            "vendor" : "Default string",
            "version" : "V0.3",
            "serial" : "LR202007007444",
            "width" : 64,
            "configuration" : {
                "boot" : "normal",
                "chassis" : "desktop",
                "family" : "Default String",
                "sku" : "Default String",
                "uuid" : "00020003-0004-0005-0006-000700080009"
            },
           "capabilities" : {
               "smbios-3.0.0" : "SMBIOS version 3.0.0",
               "dmi-3.0.0" : "DMI version 3.0.0",
               "smp" : "Symmetric Multi-Processing",
               "vsyscall32" : "32-bit processes"
            },
            "children" : [
                {
                    "id" : "pnp00:00",
                    "class" : "system",
                    "claimed" : True,
                    "product" : "PnP device PNP0c01",
                    "physid" : "1",
                    "configuration" : {
                        "driver" : "system"
                    },
                    "capabilities" : {
                        "pnp" : True
                    }
               },
               {
                   "id" : "pnp00:01",
                   "class" : "system",
                   "claimed" : True,
                   "product" : "PnP device PNP0c02",
                   "physid" : "2",
                   "configuration" : {
                       "driver" : "system"
                   },
                   "capabilities" : {
                       "pnp" : True
                   }
               },
               {
                  "id" : "pnp00:02",
                  "class" : "system",
                  "claimed" : True,
                  "product" : "PnP device PNP0b00",
                  "physid" : "3",
                  "configuration" : {
                     "driver" : "rtc_cmos"
                  },
                  "capabilities" : {
                     "pnp" : True
                   }
               },
               {
                  "id" : "pnp00:03",
                  "class" : "system",
                  "claimed" : True,
                  "product" : "PnP device PNP0c02",
                  "physid" : "4",
                  "configuration" : {
                       "driver" : "system"
                  },
                  "capabilities" : {
                       "pnp" : True
                  }
              },
          {
             "id" : "pnp00:06",
             "class" : "system",
             "claimed" : True,
             "product" : "PnP device PNP0c02",
             "physid" : "7",
             "configuration" : {
                 "driver" : "system"
             },
             "capabilities" : {
                  "pnp" : True
             }
          }
       ]
   }

    l = Linux.LSHW(debug=True)
    output = lshw_output.splitlines()
    json_dict = l.convert_to_json(output)
    assert json_dict == lshw_expected

def test_ifconfig_to_json():
    ifconfig_output = """
        wwp0s21u1i8: flags=4305<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>  mtu 9000
        inet 10.96.52.186  netmask 255.255.255.252  destination 10.96.52.186
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 1000  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 13  bytes 624 (624.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
    """
    ifconfig_expected = [ {
       "RX_packets"    : 0,
       "RX_bytes"      : 0,
       "RX_errors"     : 0,
       "RX_dropped"    : 0,
       "RX_overruns"   : 0,
       "RX_frame"      : 0,
       "TX_packets"    : 13,
       "TX_bytes"      : 624,
       "TX_errors"     : 0,
       "TX_dropped"    : 0,
       "TX_overruns"   : 0,
       "TX_carrier"    : 0,
       "TX_collisions" : 0
    } ]
    l = Linux.NetNsIfConfig(debug=True)
    output = ifconfig_output.splitlines()
    json_data = l.convert_entry_to_json(output)
    assert json_data == ifconfig_expected

def test_ipsec_status_to_json():
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
    ipsec_status_expected = [ {
       "loaded"        : 1,
       "active"        : 0,
       "errors"        : []
    } ]
    l = Linux.IPSecStatus(debug=True)
    output = ipsec_status_output.splitlines()
    json_data = l.convert_to_json(output)
    assert json_data == ipsec_status_expected

