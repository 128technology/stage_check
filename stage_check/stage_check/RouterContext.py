#!/usr/bin/env python36
"""
"""
import os
import sys
import getpass

import time

import re

import subprocess

import pprint

import ipaddress

import shlex

import argparse

import jmespath

import version_utils

try:
    from stage_check import init_helper
except ImportError:
    import init_helper

try:
    from stage_check import gql_helper
except ImportError:
    import gql_helper

"""
try:
    from stage_check import Linux
except ImportError:
    import Linux
"""

def create_instance(local_info, router_name, args, asset=None, config={}):
    return Base(local_info, router_name, args, asset, config)

# Apply these substitutions when an hw_type is set...
# List [ tuple(match, replace) ]
_HW_TYPE_REGEX_SUBS = [
]

def set_hw_type_regex_subs(regex_subs):
    """
    """
    global _HW_TYPE_REGEX_SUBS
    if len(_HW_TYPE_REGEX_SUBS) > 0:
        return
    if not isinstance(regex_subs, list):
        raise TypeError
    for entry in regex_subs:
        if not isinstance(entry, dict):
            raise TypeError
        if len(entry) != 2:
            raise ValueError
    _HW_TYPE_REGEX_SUBS = regex_subs 

def valid_hw_type(hw_type):
    reserved_words = [
        "default"
    ]
    if hw_type is None or \
       len(hw_type) < 4 or \
       hw_type in reserved_words:
        return False
    return True

class Node:
    """
    """
    def __init__(
        self,        
        asset_id=None,
        asset_json=None,
        control_ip=None,
        name=None,
        node_index=None,
        node_type=None,
        processes_json=None,
        role=None,
        router_name=None,
        version=None
        ):
         
        self._asset_id = None
        self._control_ip = None
        self._role = None
        self._version = None
        self._rpm_version = None
        self._processes = {}
        self._node_index = node_index

        self._name = name
        self._router_name = router_name
        self._node_type = node_type

        self.__hw_type = None
     
        self.update(
            asset_id,
            asset_json,
            control_ip,
            processes_json,
            role,
            version
        )

        if self._router_name is None:
            if name is None:
                raise ValueError

        if self._name is None:
            if name is None:
                raise ValueError

    def update(
        self,
        asset_id=None,
        asset_json=None,
        control_ip=None,
        processes_json=None,
        role=None,
        version=None
    ):
        if not asset_json is None:
            self.set_asset_json(asset_json)
        if self._asset_id is None:
            self._asset_id = asset_id
        if not control_ip is None:
            self._control_ip = control_ip   
        if not role is None:
            self._role=role
        if not processes_json is None:
            self.set_processes_json(processes_json)
        if not version is None and \
           not version == '':
            self._version=version
            # This may not be the true rpm verson but a graphql equivalent...
            graphql_version_regex = r"^\s*([0-9]+(?:\.[0-9])*)"
            matches = re.search(graphql_version_regex, version)
            if matches is None:
                try:
                    rpm_info = version_utils.rpm.package(version)
                    self._rpm_version = rpm_info.version
                except Exception as e:
                    # assert False, f"version_utils: {e},{e.__class__.__name__}"
                    if self.debug:
                        print(f"version_utils: {e},{e.__class__.__name__}")
                        print(f"version_utils: version={version}")
                    pass
            else:
                try:
                    #assert False, f"Apply Regex capture group to '{version}'"
                    self._rpm_version = matches.group(1)
                except IndexError:
                    #assert False, f"Regex capture group exception .."
                    pass

    @property
    def router_name(self):
        return self._router_name

    @property 
    def name(self):
        return self._name

    @property 
    def node_type(self):
        return self._node_type

    @property
    def role(self):
        return self._role

    @property
    def version(self):
        return self._version

    @property
    def rpm_version(self):
        return self._rpm_version

    @property
    def asset_id(self):
        return self._asset_id

    @property 
    def control_ip(self):
        return self._control_ip

    @property
    def processes(self):  
        return self._processes

    @property
    def node_index(self):
        return self._node_index

    @property
    def type_label(self):
        node_type_to_label = {
            "0"          : "Node 1",
            "1"          : "Node 2",
            "primary"    : "Primary",
            "secondary"  : "Secondary", 
            "solitary"   : "Solitary"
        }
        label = "Typeless"
        node_type = self.node_type
        if node_type is None:
            node_type = self.node_index
            if node_type is not None:
                node_type = str(node_type)
        if not node_type is None and \
           node_type in node_type_to_label:
           label = node_type_to_label[node_type]
        else:
           label = node_type
        return label

    @property 
    def hw_type(self):
        return self.__hw_type

    @hw_type.setter 
    def hw_type(self, value):
        global _HW_TYPE_REGEX_SUBS
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise TypeError
        for regex_entry in _HW_TYPE_REGEX_SUBS:
            value = re.sub(regex_entry['match'], regex_entry['replace'], value)
        self.__hw_type = value

    @property 
    def hw_vendor(self):
        return self.__hw_vendor

    @hw_type.setter 
    def hw_vendor(self, value):
        if value is None:
            value = "Unknown"
        if not isinstance(value, str):
            raise TypeError
        self.__hw_vendor = value

    @property 
    def hw_version(self):
        return self.__hw_version

    @hw_type.setter 
    def hw_version(self, value):
        if value is None:
            value = "Unknown"
        if not isinstance(value, str):
            raise TypeError
        self.__hw_version = value

    @property 
    def hw_serial_number(self):
        return self.__hw_serial_number

    @hw_type.setter 
    def hw_serial_number(self, value):
        if value is None:
            value = "Unknown"
        if not isinstance(value, str):
            raise TypeError
        self.__serial_number = value

    def valid_hw_type(self):
        return valid_hw_type(self.hw_type)

    def hw_type_regex_subs(self):
        return Node.hwTypeSubs

    def _add_process_entry(
        self,
        name,
        status=None,
        is_active=None,
        leader_status=None
        ):
        proc_entry = {}
        proc_entry['name'] = name
        proc_entry['active'] = is_active
        proc_entry['status'] = status
        proc_entry['leaderStatus'] = leader_status
        self._processes[name] = proc_entry
        return proc_entry

    def clear_solitary_type(self):
        if self.node_type == "solitary":
            self._node_type = None

    def set_process_json(self, process_json):
        """
        node_name is optional but if provided, must match the node's name
        asset_id is optional but if provided, must match the node's asset id
        {
            'asset_id': 'RIST07387AP1',   
            'leaderStatus': 'NONE',
            'name': 'databaseQueryCoordinator',
            'node_name': 'store',
            'node_type': 'solitary',
            'primary': False,
            'status': 'RUNNING'
        }
        """
        if 'node_name' in process_json and \
            self.name != process_json['node_name']:
            return

        if 'asset_id' in process_json and \
            process_json['asset_id'] is not None:
            if self.asset_id is None:
               self._asset_id = process_json['asset_id']
            elif self.asset_id != process_json['asset_id']:
               return 

        return self._add_process_entry(
            process_json['name'],
            is_active=process_json['primary'],
            status=process_json['status'],
            leader_status=process_json['leaderStatus']
        )

    def set_processes_json(self, process_json_list):
        """
        process_json_list is a flattened and possibly enhanced list
        of processes returned from a graphql query...
        [
            {
                'asset_id': 'RIST07387AP1',   
                'leaderStatus': 'NONE',
                'name': 'databaseQueryCoordinator',
                'node_name': 'store',
                'node_type': 'solitary',
                'primary': False,
                'status': 'RUNNING'
            },
            {
                'asset_id': 'RIST07387AP1',
                'leaderStatus': 'NONE',
                'name': 'dnsManager',
                'node_name': 'store',
                'node_type': 'solitary',
                'primary': False,
                'status': 'RUNNING'  
            }
            :
        }
        """
        self._processes.clear()
        for entry in process_json_list:
            if self.asset_id is None:
                self.asset_id = entry['asset_id']
            if not self.asset_id is None and \
                self.asset_id != entry['asset_id']:
                raise ValueError 
            self._add_process_entry(entry)
                         
    def set_asset_json(self, asset_json):
        """
        """
        fields = [
            { "attr" : "_router_name", "jsonkey" : "routerName" },
            { "attr" : "_node_name", "jsonkey" : "nodeName" },
            { "attr" : "_version", "jsonkey" : "t128Version" },
            { "attr" : "_asset_id", "jsonkey" : "assetId" }
        ]
        for field in fields:
            if field["argkey"] in asset_json:
                if getattr(self, field["attr"]) is None:
                    setattr(self, field["attr"], asset_json["jsonkey"])
                else:
                    if getattr(self, field["attr"]) != asset_json["jsonkey"]:
                        raise ValueError
        try:
            process_json_list = asset_json["state"]["processes"] 
            self.set_processes_json(process_json_list)        
        except KeyError:
            pass

    def compare_rpm_version(self, version):
        if self.rpm_version is None:
            return 1
        node_tuple = ("0", self.rpm_version, "0")
        version_tuple = ("0", version, "0")
        # TODO: catch exceptions here?
        result = version_utils.rpm.labelCompare(node_tuple, version_tuple)
        return result

    def display(self):
        print(self.to_string())

    def to_string(self, indent=0, proc_indent=4):
        pad = indent * " "
        proc_pad = proc_indent * " "
        string  = f"{pad}Router:     {self.router_name}\n"
        string += f"{pad}Name:       {self.name}\n"
        string += f"{pad}Index:      {self.node_index}\n"
        string += f"{pad}Type:       {self.node_type}\n"
        string += f"{pad}Role:       {self.role}\n"
        string += f"{pad}Software:   {self.version} ({self.rpm_version})\n"
        string += f"{pad}Asset ID:   {self.asset_id}\n"
        string += f"{pad}Control IP: {self.control_ip}\n"
        string += f"{pad}Processes:\n"
        for proc_key in self._processes:
            proc = self._processes[proc_key]
            string += pad
            string += f"{proc_pad}{proc['name']:20.20} "
            string += f"{proc.get('status', 'None'):10.10} "
            string += f"{str(proc.get('active', 'None')):6.6} "
            string += f"{proc.get('leader_status', 'None'):10.10}\n"
        return string

class Base(object):
    """
    """
    def __init__(self, local_info, router, args, asset=None, config={}):
        """
        so long as the local graphql url is used, no authenticaion 
        is requried:

        if local_info.get_node_type() == "conductor":
            self.gql_token  = gql_helper.RestToken()
        else:
            self.gql_token  = None
        """
        self.gql_token         = None
        self.primary_regex     = args.primary_regex
        self.secondary_regex   = args.secondary_regex
        self.router            = None
        self.__tests           = []
        self._nodes_by_name    = {}
        self.__profile_name    = "UNDEFINED"
        self.__config          = config
        self.__site_regex      = args.site_regex
        self.__site_id         = None
        self.__pod_regex       = args.pod_regex
        self.__pod_id          = None
      
        self.__exclude_tags    = []
        self.__include_tags    = []
        self.__dev_states      = []

        self._nodes            = []
        self._nodes_by_name    = {}
        self._nodes_by_type    = {}
        self._nodes_by_asset   = {}
        self._type_map              = {}
        self._type_map["primary"]   = {"type" : "primary",   "regex" : args.primary_regex}
        self._type_map["secondary"] = {"type" : "secondary", "regex" : args.secondary_regex}
        self._type_map["solitary"]  = {"type" : "solitary",  "regex" : ".*"}
        self._type_list             = []
        self._type_list.append(self._type_map["primary"])
        self._type_list.append(self._type_map["secondary"])
        self._type_list.append(self._type_map["solitary"])

        self._local_info = local_info

        if router == '':
            if args.debug:
                print("RouterContext.Base.__init__: Create context using local_info")
            self.router = local_info.get_router_name()
            if local_info.get_node_name() != '':
                self.set_node(
                    name=local_info.get_node_name(), 
                    version=local_info.version,
                    asset_id=local_info.minion_id
                )
            if local_info.get_peer_name() != '':
                self.set_node(name=local_info.get_peer_name())
        elif args.router != '':
            if args.debug:
                print("RouterContext.Base.__init__: Create context using args.router")
            self.router = args.router
            self.set_node(name=args.node)
        elif asset is not None:
            if args.debug:
                print("RouterContext.Base.__init__: Create context using asset info")
            self.router = asset['routerName']
            self.set_node(asset_json=asset)
        else:
            if args.debug:
                print('********* RouterContext: UNSUPPORTED MODE ********')

        self._active_proc_map = {}

        self._debug = args.debug


    @property
    def debug(self):
        return self._debug

    @property 
    def tests(self):
        return self.__tests

    @tests.setter
    def tests(self, value):
        if not isinstance(value, list):
            raise ValueError
        self.__tests = value

    @property 
    def profile_name(self):
        return self.__profile_name

    @profile_name.setter
    def profile_name(self, value):
        if not isinstance(value, str):
            raise ValueError
        self.__profile_name = value

    @property 
    def config(self):
        return self.__config

    @property 
    def local_role(self):
        return self._local_info.get_node_type().lower()

    @property
    def local_node_name(self):
        return self._local_info.get_node_name()

    @property
    def local_router_name(self):
        return self._local_info.get_router_name()

    @property
    def local_node_type(self):
        node_type = None
        node_name = self.local_node_name
        try:
            node = self._nodes_by_name[node_name]
            node_type = node.node_type
        except KeyError:
            pass
        return node_type

    @property
    def is_conductor(self):
        return (self.get_router() == self._local_info.get_router_name() and \
                self.local_role == "conductor")

    @property
    def from_conductor(self):
        return self.local_role == "conductor"

    @property 
    def skip_single_node(self):
        """
        A test which is to be explicitly (generally a linux test with more than one test entry
        in the config profile) run against a second node only.  Currently this test can only
        be run from the conductor. 
        """
        if not self.from_conductor:
            return True
        if len(self.get_nodes()) < 2:
            return True
        return False

    @property
    def exclude_tags(self):
        return self.__exclude_tags

    @property
    def include_tags(self):
        return self.__include_tags

    @property 
    def name(self):
        return self.router

   # @include_tags.setter
   # def include_tags(self, value):
   #     """
   #     As a hard fought reminder, a setter written
   #     this way does not work, self.__include_tags
   #     is assigned value directly.
   #     """
   #     if not value in self.__include_tags:
   #         self.__include_tags.append(value)


    def add_exclude_tag(self, value):
        if not value in self.__exclude_tags:
            self.__exclude_tags.append(value)


    def add_include_tag(self, value):
        if not value in self.__include_tags:
            self.__include_tags.append(value)


    def get_expected_connections(self):
        """
        connectivity count = router_node_count - 1 + 
                router_node_count * conductor_node_count
        """
        node_count = 0
        cond_count = 0
        node_count = len(self.get_nodes())
        count = (node_count - 1) * node_count
        if self._local_info.get_router_name() != self.get_router():
            if self.from_conductor:
                cond_count = self._local_info.get_node_count() 
        count += cond_count * len(self.get_nodes())
        return count       
               
    def get_router(self):
        return self.router

    def _get_node(self, node_type_string : str):
        node = None
        if not isinstance(node_type_string, str):
            raise TypeError
        node_types_to_check = set(node_type_string.split('|'))
        for node_type in node_types_to_check:
            if len(node_type) == 0:
                node_type="solitary"
            try:
                node = self._nodes_by_type[node_type]
                break
            except KeyError:
                pass
        return node

    def _get_node_attribute(self, node_type_string : str, attribute : str):
        if not isinstance(attribute, str):
            raise TypeError
        node = self._get_node(node_type_string)
        if node is not None:
            try:
                return getattr(node, attribute, None)
            except KeyError:
                pass
        return None

    def get_node_name(self, node_type):
        return self._get_node_attribute(node_type, "name")

    def get_node_asset(self, node_type, load=True):
        result = self._get_node_attribute(node_type, "asset_id")
        if result is None and load:
            self.query_node_info()
            result = self._get_node_attribute(node_type, "asset_id")
        return result

    def get_node_hw_type(self, node_type):
        return self._get_node_attribute(node_type, "hw_type")

    def get_node_hw_vendor(self, node_type):
        return self._get_node_attribute(node_type, "hw_vendor")

    def get_node_hw_version(self, node_type):
        return self._get_node_attribute(node_type, "hw_version")

    def get_node_hw_serial_number(self, node_type):
        return self._get_node_attribute(node_type, "hw_serial_number")

    def get_node_version(self, node_type):  
        return self._get_node_attribute(node_type, "version")

    def get_node_rpm_version(self, node_type):
        return self._get_node_attribute(node_type, "rpm_version")

    def compare_node_rpm_version(self, node_type, rpm_version):
        node = self._get_node(node_type)
        return node.compare_rpm_version(rpm_version)

    def nodes_with_lesser_rpm_version(self, rpm_version):
        count = 0
        for node in self._nodes:
            if node.compare_rpm_version(rpm_version) < 0:
                count += 1
        return count


    def nodes_with_hw_type  (self, hw_types=[]):
        if isinstance(hw_types, str):
            hw_types = [ hw_types ]
        elif not isinstance(hw_types, list):
            raise TypeError
        count=0
        for node in self._nodes:
            if node.hw_type in hw_types:
                count += 1
        return count

    def valid_hw_type(self):
        for node in self._nodes:
            if not node.valid_hw_type():
                return False
        return True

    def is_primary(self, node_name):
        return re.search(self._type_map["primary"]["regex"], node_name)

    def is_secondary(self, node_name):
        return re.search(self._type_map["secondary"]["regex"], node_name)

    def is_solitary(self, node_name):
        if len(self.get_nodes) > 1:
            return False
        return not (self.is_primary(node_name) or \
                    self.is_secondary(node_name))

    def have_asset_info(self):
        for node in self._nodes:
            if node.asset_id is None:
                return False
        return True

    def have_active_info(self):
        return (len(self._active_proc_map) > 0)

    def get_node_types(self):
        """
        Returns 1 or 2 types for this router's nodes. Note that if
        primary, secondary, solitary was not assigned, the node index
        is added
        """
        type_list = []
        for node in self._nodes:
            if not node.node_type is None:
                type_list.append(node.node_type)
            elif not node.node_index is None:
                type_list.append(str(node.node_index))
            
        return type_list

    def active_process_node(self, process_name):
        """
        Given a process name as input, returns the node name
        for which the process is primary
        """
        try:
            node = self._active_proc_map[process_name]
            return node.name
        except KeyError:
            return ''

    def active_process_asset(self, process_name):
        """
        Given a process name as input, returns the node name
        for which the process is primary
        """
        try:
            node = self._active_proc_map[process_name]
            return node.asset_id
        except KeyError:
            return ''

    def check_node_index(self, node_index):
        for node in self.get_nodes():
            if node.node_index == node_index:
                assert False, f"Node Index {node_index} already in use:\n" + \
                    self.to_string()

    def get_node_info(self):
        """
        """
        node_list = []
        for node in self.get_nodes():
            node_item = {}
            node_item["name"]       = node.name
            node_item["type"]       = node.node_type
            node_item["role"]       = node.role
            node_item["asset"]      = node.asset_id
            node_item["rpmVersion"] = node.rpm_version
            node_item["hwType"]     = node.hw_type
            node_list.append(node_item.copy())
        return node_list
    
    def set_node(
        self, 
        asset_id=None,
        asset_json=None,
        control_ip=None,
        name=None,
        processes_json=None,
        role=None,
        version=None
        ):
        """
        set node information using individual parameters or graphql
        asset data.
        """
        if name is None:
            if asset_json is None or \
               not "nodeName" in asset_json:
                assert False, pprint.pformat(asset_json)
                raise ValueError

        node_name = name
        if node_name is None:
           node_name = asset_json["nodeName"]
        node_asset = asset_id
        if node_asset is None and \
           not asset_json is None and \
           "assetId" in asset_json:
            node_asset = asset_json["assetId"]
        node_version = version
        if node_version is None and \
           not asset_json is None and \
           "t128Version" in asset_json:
            node_version = asset_json["t128Version"]

        if node_asset in self._nodes_by_asset and \
           self._nodes_by_asset[node_asset].name != node_name:
            raise ValueError

        node = None
        if node_name in self._nodes_by_name:
            node = self._nodes_by_name[node_name]
        
        if node is None:
            match=None
            for entry in self._type_list:
                if re.search(entry["regex"], node_name):
                    match=entry
                    break
            if match is None:
                raise ValueError
            node_type = match["type"]
            if "solitary" in self._nodes_by_type:
               node_type = None
               for other in self.get_nodes():
                   other.clear_solitary_type()
            node_index = len(self.get_nodes())
            self.check_node_index(node_index)
            node = Node(
                asset_id=node_asset,
                control_ip=control_ip,
                name=node_name,
                node_index=node_index,
                node_type=node_type,
                processes_json=processes_json,
                role=role,
                router_name=self.get_router(),
                version=node_version
            )
            if node_type is not None:
                self._nodes_by_type[node_type] = node
            self._nodes_by_name[node_name] = node
            if not node in self._nodes:
                self._nodes.append(node)
                self._nodes_by_type[str(node_index)] = node
        else:
            node.update(
                asset_id=node_asset,
                control_ip=control_ip,
                processes_json=processes_json,
                role=role,
                version=node_version
            )

        if node_asset is not None and \
           node_asset not in self._nodes_by_asset:
            self._nodes_by_asset[node_asset] = node


    def node_type(self, node_name=''):
        for type_key in self._type_map:
            entry = self._type_map[type_key]
            if re.search(entry["regex"], node_name):
                return entry["type"]
        # TODO -- Return None instead of ''?
        return None

    def get_nodes(self):
        return self._nodes

    def query_node_info(self):
        """
        If the router name is known, but the nodes are not
        or the nodes are known, but the asset ids are not

        Send a GraphQL query to get the missing information...
        """
        """
        so long as the local graphql url is used, no authenticaion 
        is required
        if self.gql_token is None:
            return
        """

        if self.have_asset_info() and \
           self.have_active_info():
            return

        qr = gql_helper.NodeGQL("allRouters", ['name'], [ self.get_router() ],
                                                         debug=self.debug)
        qn = gql_helper.NodeGQL("nodes", ['name', 'assetId', 'state { processes { name status primary leaderStatus } }'])

        qr.add_node(qn)

        json_reply={}
        api_errors=[]
        query_status = qr.send_query(self.gql_token, json_reply, api_errors)

        if query_status != 200 or \
            len(api_errors) > 0:
            return

        # _format_allRouters_reply adds the assetId and other parameters
        # to each process entry...
        #match_string = "node.state.processes[]"
        #merged_list = self._format_allRouters_reply(json_reply, match_string)
        process_list = qr.flatten_json(json_reply, "allRouters/nodes/state/processes")
        self.set_allRouters_node_type(process_list)
        #assert False, "RCQueryInfo: " + pprint.pformat(process_list)

        if self.debug:
            print('........ flattened list ..........')
            pprint.pprint(process_list)

        for entry in process_list:
            try:
                node_name = entry['node_name']
                node = self._nodes_by_name[node_name]
                node.set_process_json(entry)
                if entry['primary']:
                    self._active_proc_map[entry['name']] = node
            except KeyError:
                pass

        #assert False, pprint.pformat(self.active_proc_map)
        #assert False, pprint.pformat(self.active_asset_map)
        #assert False, self.to_string()


    def set_allRouters_node_type(self, node_list, node_name_key='allRouters/nodes/name'):
        """
        node_name_key, or any flattened name should no longer be prefixed with '/' as
        this causes is confused with division by ExParser. '/' can still be used as a 
        seperator, so node_name_key='allRouters/nodes/name' can be processed in 
        test expressons, but node-_name_key='/allRouters/node/name' cannot!
        """
        dev_states = self._get_dev_states_copy()
        for entry in node_list:
            try:
                node_name = entry[node_name_key]
                node_type = self.node_type(node_name)
                entry['node_type'] = self.node_type(node_name)
                entry['node_name'] = node_name
                entry['rpm_version'] = self.get_node_rpm_version(node_type)
                entry['hw_type'] = self.get_node_hw_type(node_type)
                if not dev_states is None and \
                   not "dStates" in entry:
                   entry["dStates"] = dev_states
            except (KeyError, TypeError):
                pass

    def display(self):
        print(f"{self.to_string()}")

    def to_string(self):
        first_line  = f"Router:            {self.get_router()}"
        seperator_1 = "=" * len(first_line)
        seperator_2 = '-' * len(first_line)
        string  = f"{seperator_1}\n"
        string += f"{first_line}\n"
        string += f"Local Router:      {self.local_router_name} (role: {self.local_role})\n"
        string += f"Primary Regex:     {self.primary_regex}\n"
        string += f"Secondary Regex:   {self.secondary_regex}\n"
        string += f"Site ID:           {self.get_site_id()}\n"
        string += f"Pod  ID:           {self.get_pod_id()}\n"
        string += f"{seperator_1}\n"
        string += "Active Process Map:\n"
        if len(self._active_proc_map) > 0:
            for proc_key in self._active_proc_map:
                node = self._active_proc_map[proc_key]
                string += f"    {proc_key:20.20}: {node.name:15.15} {node.asset_id}\n"
                #string += f"    {proc_key:15.15}: {node.name:15.15} {node.asset_id:15.15}\n"
        string += "Nodes:\n"
        node_count = 0
        for node in self._nodes:
            if node_count > 0:
                string += " " *4 + "-" * len(self.get_router())
                string += "\n"
            string += node.to_string(indent=4)
            node_count += 1
        return string

    def set_tests(self, profile_name, tests):
        self.profile_name = profile_name
        self.tests = tests

    def get_site_id(self):
        """
        """
        if self.__site_id is None:
            router_name = self.get_router()
            matches = re.search(self.__site_regex, router_name)
            if matches is None:
                return None
            try:
                self.__site_id = matches.group(1) 
            except IndexError:
                return None
        return self.__site_id

    def get_pod_id(self):
        """
        """
        if self.__pod_id is None:
            router_name = self.get_router()
            matches = re.search(self.__pod_regex, router_name)
            if matches is None:
                return None
            try:
                self.__pod_id = matches.group(1) 
            except IndexError:
                return None
        return self.__pod_id

    ######################################################################
    #
    # To be populated by derived classes...
    #
    #######################################################################
    def query_extra_info(self):
        """
        By inheriting from this class, partner or customer specific info
        can be queried and then displayed in the header for each router's
        test.

        In the base class, this does nothing...
        """
        return True

    def display_extra_info_header(self, extra_info_lines):
        """
        This can be overriden by derived RouterContext classes
        to display site state and additional information in
        the header output before tests are run.
        """
        return True

    def display_extra_info_summary(self):
        """
        This can be overriden by derived RouterContext classes
        to summarize site state and additional information in
        an extremely brief format for use with the -o flag
        """
        return None

    def _populate_error_to_string(self):
        """
        Return an error string which does not cause Lexar / Parser errors
        when using the EntryTester module.
        """
        return "POPULATE_ERROR"

    def _populate_string(self, string, data_source):
        pattern = r'\{([^\{\}]+)\}'
        result = string
        matches = re.findall(pattern, result)
        for key in matches:
            if key in data_source:
                value = data_source[key]
                target = "{" + f"{key}" + "}"
                if isinstance(value, str) and \
                   len(value) > 0:
                    result = result.replace(target, f"{value}")
                else:
                    result = result.replace(target, f"{self._populate_error_to_string()}")
        return result

    def populate_items(self, entry):
        """
        recursively scans a dictionary or list looking for strings
        with patterns to replce with data from the RouterContext

        This could replace _populate_config_fields and
        _populate_entry_tests 
        """
        data_source = {}
        data_source["pod-id"]  = self.get_pod_id()
        data_source["site-id"] = self.get_site_id()

        if isinstance(entry, str):
            return self._populate_string(entry, data_source)
        elif isinstance(entry, dict):
            for key in entry:
                entry[key] = self.populate_items(entry[key])
        elif isinstance(entry, list):
            key = 0
            stop_key = len(entry)
            while key < stop_key:
                entry[key] = self.populate_items(entry[key])
                key += 1
        return entry

    def _populate_config_fields(self, entry):
        """   
        This is an experiment in support of deployments which contain router 
        or site-specific data in service names or other information which is used 
        for test input parameters.
      
        The specific use case is:
        {
             "service" : "Store-{site-id}-POS"
        }

        If this proves useful enough, RouterContext may provide a dctionary of all of its 
        data for use in input fields.

        WARNING: At this time here is no way to indicate whether a test parameter
                 should or should not be populated / replaced.  A reguar expression
                 which happened to have "{site-id}" in it would be replaced with
                 prejudice. 
        """
        data_source = {}
        data_source["site-id"] = self.get_site_id()
        data_source["pod-id"]  = self.get_pod_id()
        pattern = r'\{([^\{\}]+)\}'

        for field in entry:
            result = entry[field]
            if not isinstance(result, str):
                continue
            matches = re.findall(pattern, result)
            for key in matches:
                if key in data_source:
                    value = data_source[key]
                    target = "{" + f"{key}" + "}"
                    if isinstance(value, str) and \
                       len(value) > 0:
                        result = result.replace(target, f"{value}")
                    else:
                        result = result.replace(target, f"{self._populate_error_to_string()}")
            entry[field] = result

    def _populate_entry_tests(self, entry_tests):
        """   
        This is an experiment in support of deployments which contain router 
        or site-specific data in service names or other information which is used 
        for test input parameters.
      
        Populate a format string.  Use case, where the test controls what fields
        the population of {variable}s is applied to:
        "entry_tests" : {
            "tests" : [
                { "test" : "Service-One" },
                { "test" : "Service-Two" },
                { "test" : "Service-{site-id}" }
            ]
        }
        """
        data_source = {}
        data_source["site-id"] = self.get_site_id()
        pattern = r'\{([^\{\}]+)\}'
        
        fields = [ "test", "format" ]
        #assert False, pprint.pformat(data_source)

        try:
            tests = entry_tests["tests"]
        except KeyError:
            return
        for entry in tests:
            for field_name in fields:
                try:
                    result = entry[field_name]
                    if not isinstance(result, str):
                        continue
                    matches = re.findall(pattern, result)
                    for key in matches:
                        target = "{" + f"{key}" + "}"
                        # if the key is not present, it might be replaced by the normal
                        # format population... 
                        if key in data_source:
                           value = data_source[key]
                           if isinstance(value, str) and \
                              len(value) > 0:
                               result = result.replace(target, f"{value}")
                           else:
                               result = result.replace(target, f"{self._populate_error_to_string()}")
                    entry[field_name] = result
                except KeyError:
                    continue
        #assert False, pprint.pformat(entry_tests)            
    
    def profile_name_defined(self):
        if self.profile_name is not None and \
           self.profile_name != 'UNDEFINED':
            return True
        return False

    def get_alt_lshw_class(self):
        return "bus"

    def set_lshw_info(self, json_data):
        """                                                                                                            
        json_data is a list of Linux.LSHW entries, each of which is the output                                         
        of lshw -json, extended with stage_check info including node_name,                                             
        node_type etc.                                                                                                 
        [                                                                                                              
            {                                                                                                          
                "lshw output 1"                                                                                        
            },                                                                                                         
            {                                                                                                          
                "lshw output 2"                                                                                        
            }                                                                                                          
        ]                                                                                                              
        """
        # reserved words must be lower-case
        retval = True 
        if self.debug:
            print("----------- set_lshw_info -----------")
            pprint.pprint(json_data)
        for entry in json_data:
            try:
                product_string = entry["product"]
                product_elements = product_string.split(" ")
                product = product_elements[0]
                node_type = entry["node_type"]
            except (KeyError, IndexError) as e:
                if self.debug:
                    print(f"set_ls_hw: EXCEPTION {e} {e.__class__.__name__}")
                retval = False
                continue
            node = self._nodes_by_type[node_type] 
            if self.debug: 
                print(f"{node_type}: HW_TYPE = {product}", flush=True) 
            if valid_hw_type(product):
                if self.debug:
                    print(f"{node_type} SET HW_TYPE={product}")
                node.hw_type = product
            else:
                if self.debug:
                    print(f"{node_type}: Bad HW_TYPE", flush=True) 

        return retval

    def set_hw_info(self, json_data):
        """
        Used to set HW data obtained by GraphQL
        """
        if self.debug:
            print("----------- set_hw_info -----------")
            pprint.pprint(json_data)
        for entry in json_data:
            try:
                product_string = entry["product"]
                product_elements = product_string.split(" ")
                product = product_elements[0]
                node_type = entry["node_type"]
            except (KeyError, IndexError) as e:
                if self.debug:
                    print(f"set_ls_info: EXCEPTION {e} {e.__class__.__name__}")
                continue
            node = self._nodes_by_type[node_type]
            node.hw_type = product
            try:
                node.hw_serial_number = entry["serialNumber"]
                node.hw_vendor = entry["vendor"]
                node.hw_version = entry["version"]
            except KeyError:
                continue

    def query_hw_info(self):
        """
        GraphQL queries are more responsive than salt, so this is
        preferred over TestExecutor.query_hw_type()
        """
        if self.debug:
            print(f"{self.get_router()}: Query HWINFO...")
        qr = gql_helper.NewGQL(
            api_name="allRouters", 
            api_args={"name" : self.get_router()}, 
            api_fields=["name"], 
            api_has_edges=True,
            debug=self.debug
        )
        qn = gql_helper.NewGQL(
            api_name="nodes", 
            api_fields=["name", "platform{ vendor{ product serialNumber vendor version } }"], 
            api_has_edges=True
        )
        qr.add_node(qn)
        json_reply = {}
        api_errors = []
        status_code = qr.send_query(self.gql_token, json_reply, api_errors)
        #assert False, pprint.pformat(json_reply)
        if status_code < 400 and len(json_reply) > 0:
            flattened_json = qr.flatten_json(json_reply, "allRouters/nodes/platform/vendor")
            self.set_allRouters_node_type(flattened_json)
            if self.debug:
                print("---- query_hw_info: flattened_hw_info ----")
                pprint.pprint(flattened_json)
            self.set_hw_info(flattened_json)
            
    def add_entry_tags(self, test_result, entry):
        # skip non-matching entries        
        if test_result is None:
            return
        if not "test_matched" in entry or \
           not isinstance(entry["test_matched"], dict):
            return
        test_entry = entry["test_matched"]
        if self.debug:
            print(f"*** {self.get_router()}: add_entry_tags({test_result}) ***")
            pprint.pprint(test_entry)
        if "exclude_tags" in test_entry:
            for tag in test_entry["exclude_tags"]:
                self.add_exclude_tag(tag)
                if self.debug:
                    print(f"*** {self.get_router()}: add exclude tag {tag} ***")
        if "include_tags" in test_entry:
            for tag in test_entry["include_tags"]:
                self.add_include_tags(tag)
                if self.debug:
                    print(f"*** {self.get_router()}: add include tag {tag} ***")
        
    def set_device_states(self, dev_states):
        """
        Currently this is maintained at the Base (RouterContext) level
        so it can be copied into a list of elements as required
        """
        if not isinstance(dev_states, dict):
            raise TypeError
        self.__dev_states = dev_states.copy()      

    def _get_dev_states_copy(self):
        if not self.__dev_states is None: 
            return self.__dev_states.copy()
        return None

    def populate_extra_info(self, info):
        """
        Overload this method in a RouterContext Subclass to add 
        fields to the 
        """ 
        pass
