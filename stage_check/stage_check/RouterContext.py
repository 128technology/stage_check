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

try:
    from stage_check import init_helper
except ImportError:
    import init_helper

try:
    from stage_check import gql_helper
except ImportError:
    import gql_helper


def create_instance(local_info, router_name, args, asset=None):
    return Base(local_info, router_name, args, asset)

class Base(object):
    """
    """
    def __init__(self, local_info, router, args, asset=None):
        self.gql_token         = gql_helper.RestToken()
        #self.gql_token         = None
        self.primary_regex     = args.primary_regex
        self.secondary_regex   = args.secondary_regex
        self.router            = None
        self.primary_node      = None
        self.primary_asset     = None
        self.primary_version   = None
        self.secondary_node    = None
        self.secondary_asset   = None
        self.secondary_version = None
        self.solitary_node     = None
        self.solitary_asset    = None
        self.solitary_version  = None 
        self.nodes             = []

        if router == '':
            self.router = local_info.get_router_name()
            if local_info.get_node_name() != '':
                self.nodes.append(local_info.get_node_name())
            if local_info.get_peer_name() != '':
                self.nodes.append(local_info.get_peer_name())
        elif args.node != '':
            self.router = router
            self.nodes = [ args.node ]
        elif asset is not None:
            self.router = asset['routerName']
            self.nodes  = [ asset['nodeName'] ]
        else:
            if args.debug:
                print('********* RouterContext: UNSUPPORTED MODE ********')

        # populate nodes list
        if args.primary_regex != '':
            for node in self.nodes:
                if re.search(args.primary_regex, node):
                    self.primary_node = node
                    if asset is not None:
                        self.primary_version = asset['t128Version']
                        self.primary_asset   = asset['assetId']
                else:
                    self.secondary_node = node
                    if asset is not None:
                        self.secondary_version = asset['t128Version']
                        self.secondary_asset   = asset['assetId']
        else:
             self.solitary_node = self.nodes[0]
             if asset is not None:
                 self.solitary_version = asset['t128Version']
                 self.solitary_asset   = asset['assetId']

        self.active_proc_map = {}
        self.active_asset_map = {}

        self._debug = args.debug

    def update(self, asset):
        node = asset['nodeName']
        if node not in self.nodes: 
            self.nodes.append(node)

        if self.primary_regex:	
            if re.search(self.primary_regex, node):
                self.primary_node = node
                self.primary_version = asset['t128Version']
                self.primary_asset   = asset['assetId']
            else:
                self.secondary_node = node
                self.secondary_version = asset['t128Version']
                self.secondary_asset   = asset['assetId']
        else:
             self.solitary_node = node
             self.solitary_version = asset['t128Version']
             self.solitary_asset   = asset['assetId']

    @property
    def debug(self):
        return self._debug

    def get_router(self):
        return self.router

    def primary_name(self):
        return self.primary_node

    def get_primary_asset(self, load=True):
        if load and \
           not self.have_asset_info():
            self.query_node_info()
        return self.primary_asset

    def get_primary_version(self):  
        return self.primary_version

    def secondary_name(self):
        return self.secondary_node

    def get_secondary_asset(self, load=True):
        if load and \
           not self.have_asset_info():
            self.query_node_info()
        return self.secondary_asset

    def get_secondary_version(self):  
        return self.secondary_version

    def solitary_name(self):
        return self.solitary_node

    def get_solitary_asset(self, load=True):
        if load and \
           not self.have_asset_info():
            self.query_node_info()
        return self.solitary_asset

    def get_solitary_version(self):
        return self.solitary_version

    def is_primary(self, node):
        return re.search(self.primary_regex, node)

    def is_secondary(self, node):
        return re.search(self.secondary_regex, node)

    def is_solitary(self, node):
        return not (self.is_primary(node) or \
                    self.is_secondary(node))

    def get_node_by_type(self, node_type):
        if node_type == 'primary':
            return self.primary_name()
        elif node_type == 'secondary':
            return self.secondary_name()
        elif node_type == 'solitary':
            return self.solitary_name()
        else:
            return ''

    def get_asset_by_type(self, node_type, load=True):
        if node_type == 'primary':
            return self.get_primary_asset(load)
        elif node_type == 'secondary':
            return self.get_secondary_asset(load)
        elif node_type == 'solitary':
            return self.get_solitary_asset(load)
        else:
            return ''

    def get_version_by_type(self, node_type):
        if node_type == 'primary':
            return self.get_primary_version()
        elif node_type == 'secondary':
            return self.get_secondary_version()
        elif node_type == 'solitary':
            return self.get_solitary_version()
        else:
            return ''

    def have_asset_info(self):
        return (self.primary_asset is not None or
                self.secondary_asset is not None or
                self.solitary_asset is not None)

    def have_active_info(self):
        return (len(self.active_proc_map) > 0)

    def active_process_node(self, processName):
        """
        Given a process name as input, returns the node name
        for which the process is primary
        """
        try:
            return self.active_proc_map[processName]
        except KeyError:
            return ''

    def active_process_asset(self, processName):
        """
        Given a process name as input, returns the node name
        for which the process is primary
        """
        try:
            return self.active_asset_map[processName]
        except KeyError:
            return ''

    def set_node(self, node):
        """
        TODO throw exception if node type is already set to
             something different? This wouls theoretically only
             ever happen if the wrong node name was specified
             using command line arguments...
        """
        if self.is_primary(node):
            self.primary_node = node
        elif self.is_secondary(node):
            self.secondary_node = node
        else:
            self.solitary_node = node

    def node_type(self, node=''):
        if self.is_primary(node):
            node_type = 'primary'
        elif self.is_secondary(node):
            node_type = 'secondary'
        elif node != '':
            node_type = 'solitary'
        else:
            node_type=''
        return node_type

    def get_nodes(self):
        return self.nodes

    def query_node_info(self):
        """
        If the router name is known, but the nodes are not
        or the nodes are known, but the asset ids are not

        Send a GraphQL query to get the missing information...
        """
        if self.gql_token is None:
            return

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

        match_string = "node.state.processes[]"
        merged_list = self._format_allRouters_reply(json_reply, match_string)

        if self.debug:
            print('........ flattened list ..........')
            pprint.pprint(merged_list)

        for entry in merged_list:
            if  self.get_asset_by_type(entry['node_type'], load=False) is None:
                # create an asset enty with data available
                asset={}
                asset['assetId'] = entry['asset_id']
                asset['nodeName'] = entry['node_name']
                asset['t128Version'] = 'Unknown'
                self.update(asset)
            if entry['primary']:
                self.active_proc_map[entry['name']]  = entry['node_name']
                self.active_asset_map[entry['name']] = entry['asset_id']

    def _format_allRouters_reply(self, json_reply, jmespath_string):
        """
        Process the allRoutes jsonReply, extracting node names and determining
        whether that node is primary, secondary, or solitary and then adding
        node_name and node_type entries to each list entry obtained by applying
        the provided jmespath_string.

        It seems the list of merged entries must be returned as for who knows what
        odd reason, python passes lists by value
        """
        merged_list=[]

        try:
            edges = json_reply['node']['nodes']['edges']
        except KeyError:
            return merged_list

        for edge in edges:
            node_name = None
            asset_id  = None
            try:
                node_name = edge['node']['name']
                self.set_node(node_name)
            except KeyError:
                pass
            try:
                asset_id = edge['node']['assetId']
            except KeyError:
                pass
            matching_json = jmespath.search(jmespath_string, edge)
            if matching_json is None:
                continue
            if self.debug:
                pprint.pprint(matching_json)
            for entry in matching_json:
                if node_name is not None:
                    entry['node_name'] = node_name
                    entry['node_type'] = self.node_type(node_name)
                if asset_id is not None:
                    entry['asset_id'] = asset_id
            merged_list.extend(matching_json)
        if self.debug:
            pprint.pprint(merged_list)
        return merged_list

    def set_allRouters_node_type(self, node_list, node_name_key='router/nodes/name'):
        for entry in node_list:
            try:
                node_name = entry[node_name_key]
                node_type = self.node_type(node_name)
                entry['node_type'] = self.node_type(node_name)
                entry['node_name'] = node_name
            except (KeyError, TypeError):
                pass

    def format(self):
        print(f'Router:            {self.get_router()}')
        print(f'Primary Regex:     {self.primary_regex}')
        print(f'Secondary Regex:   {self.secondary_regex}')
        print(f'Primary Node:      {self.primary_name()}')
        print(f'Secondary Node:    {self.secondary_name()}')
        print(f'Solitary Node:     {self.solitary_name()}')
        print(f'Primary Version:   {self.get_primary_version()}')
        print(f'Secondary Version: {self.get_secondary_version()}')
        print(f'Solitary Version:  {self.get_solitary_version()}')
        print(f'Primary Asset:     {self.get_primary_asset(load=False)}')
        print(f'Secondary Asset:   {self.get_secondary_asset(load=False)}')
        print(f'Solitary Asset:    {self.get_solitary_asset(load=False)}')

    #foreach node:
       # def get_application_stop_start(self):
       # run_linux(TBD, TBD, TBD, "systemctl show 128T", "(Ina|A)ctiveEnterTimestamp=", candidate_lines, error_lines)   

       # def get_os_boot(self):
       # run_linux(TBD, TBD, TBD, "systemctl show 128T", "(In)?ActiveEnterTimestamp=", candidate_lines, error_lines)   

       # highwayManager actual log-level

       # configured:
       #  - monitor mode 
       #  - log-level

       # core dumps since last boot
       
       # memory, cpu, disk

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
         
