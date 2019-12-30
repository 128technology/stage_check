#!/usr/bin/env python36
###############################################################################
#       _                           _               _                  
#   ___| |_ __ _  __ _  ___     ___| |__   ___  ___| | __  _ __  _   _ 
#  / __| __/ _` |/ _` |/ _ \   / __| '_ \ / _ \/ __| |/ / | '_ \| | | |
#  \__ \ || (_| | (_| |  __/  | (__| | | |  __/ (__|   < _| |_) | |_| |
#  |___/\__\__,_|\__, |\___|___\___|_| |_|\___|\___|_|\_(_) .__/ \__, |
#                |___/    |_____|                         |_|    |___/ 
#
###############################################################################
import os
import sys
import getpass
import importlib

import time

import re

import subprocess

import pprint

import ipaddress

import shlex

import argparse

import json
import jmespath
import jsonschema

try:
    from stage_check import paths
except ImportError:
    import paths

try:
    from stage_check import init_helper
except ImportError:
    import init_helper

try:
    from stage_check import gql_helper
except ImportError:
    import gql_helper

try:
    from stage_check import RouterContext
except ImportError:
    import RouterContext

try:
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest

try:
    from stage_check import Output
except ImportError:
    import Output
   

class TestExecutor(object):

  TEST_EXECUTOR_VERSION = '1.4.0'
  
  # Overall test config...
  JSON_SCHEMA_FILE = "config_schema.json"
  JSON_CONFIG_FILE = "config.json"

  def __init__(self, args):
     """
     """
     self.tests                = []
     self.router_dict          = {}
     # dictionary of router lists keyed by pattern
     self.routers_by_pattern   = {}

     self.__paths = paths.Paths(args)
     if args.debug == True:
         self.paths.dump()

     self.local_info = init_helper.NodeInfo()
     if self.local_info.get_node_type() == "conductor":
         self.gql_token  = gql_helper.RestToken(gql_path=self.paths.gql_path)
     else:
         self.gql_token  = None

     self.exclude_list    = args.exclude
     self.primary_regex   = args.primary_regex
     self.secondary_regex = args.secondary_regex
     self._debug          = args.debug
     self.router_patterns = args.router_patterns
     self.start_after     = args.start_after

     self._stage_check_path = self.paths.runtime_path

     self.load_config(args)

     try:
         if self.config_dict["SuppressAboutText"] == False:
             self.print_version()
     except KeyError:
         self.print_version()

     self.load_router_module()
     self.load_banner()
   
     self.create_router_contexts(args)

     if args.debug:
         print(f'Local Node Info:')
         print(f'----------------')
         print(f'Local Router:    {self.local_info.get_router_name()}')
         print(f'Local Node:      {self.local_info.get_node_name()}')
         print(f'Local Peer Node: {self.local_info.get_peer_name()}')
         print(f'Local Type:      {self.local_info.get_node_type()}')

     self.load_tests(self.stage_check_path, args)

     self.tests_by_status = {}

     self._warn_is_fail = args.warn_is_fail

     self.exclude_list = args.exclude

     self.output_file = args.output

     self.status_strings={}
     self.status_strings[Output.Status.OK]   = 'PASS'
     self.status_strings[Output.Status.WARN] = 'WARN'
     self.status_strings[Output.Status.FAIL] = 'FAIL'


  @property
  def warn_is_fail(self):
      return self._warn_is_fail

  @property
  def debug(self):
      return self._debug

  @property 
  def stage_check_path(self):
      return self._stage_check_path

  @property
  def paths(self):
      return self.__paths

  def version(self):
      return self.TEST_EXECUTOR_VERSION

  def print_version(self):
      print(f'---------------------------')
      print(f'stage_check version: {self.version()}')
      print(f'---------------------------')

  def clear_counts(self):
      self.tests_by_status = {}
 
  def count_results(self, status):
      try:
          count = len(self.tests_by_status[status]) 
      except (KeyError, TypeError):
          count = 0
          pass
      return count

  def tally_results(self, test, status):
      """
      To be stored in router context?
      """
      if status not in self.tests_by_status:
          self.tests_by_status[status] = []
      self.tests_by_status[status].append(test.description())

  def tests_shell_status(self):
      shell_status = 1
      if self._warn_is_fail:
          if Output.Status.WARN in self.tests_by_status or \
             Output.Status.FAIL in self.tests_by_status:
              shell_status = 1
      else:
          if Output.Status.FAIL in self.tests_by_status:
              shell_status = 0
      return shell_status


  def get_json_assets(self):
      """
      Loads a list of json assets from the conductor
      """
      qn = gql_helper.NodeGQL("allAuthorities", [ 'assets { assetId routerName nodeName t128Version status assetIdConfigured text failedStatus }' ],
                                                    [ ], top_level=True, debug=self.debug)
      json_reply={}
      query_status = qn.send_query(self.gql_token, json_reply)
      if not query_status == 200:
          print('\n*** Unable to query conductor assets ***\n')
          sys.exit(1)

      match_string=f"node.assets[*]"
      flatter_json = jmespath.search(match_string, json_reply)

      if self.debug:
          print('........ flattened list ..........')
          pprint.pprint(flatter_json)

      self.json_assets = flatter_json
      return query_status
          

  def create_router_contexts(self, args):
      """
      create one or more router assets
      """
      if "PrimaryRegex" in self.config_dict:
           args.primary_regex = self.config_dict["PrimaryRegex"]
      if "SecondaryRegex" in self.config_dict:
           args.secondary_regex = self.config_dict["SecondaryRegex"]
      if len(self.router_patterns) > 0:
          if self.local_info.get_node_type() == 'conductor':
              self.get_json_assets()
              for asset in self.json_assets:
                  try:
                      router_name = asset['routerName']
                  except KeyError:
                      continue
                  matched_router = False
                  for pattern in self.router_patterns:
                      if args.regex_patterns:
                          if re.search(pattern, router_name):
                              matched_router = True
                              break
                      else:
                          if pattern in router_name:
                              matched_router = True
                              break
                  if matched_router:
                      op_string='Add'
                      if router_name not in self.router_dict:
                          rc = self.router_module.create_instance(self.local_info, router_name, args,
                                                                  asset)
                          self.router_dict[router_name] = rc
                          if pattern in self.routers_by_pattern:
                              self.routers_by_pattern[pattern].append(rc)
                          else:
                              self.routers_by_pattern[pattern] = [ rc ]
                      else:
                          op_string='Update'
                          self.router_dict[router_name].update(asset)
                      if args.debug or args.context:
                          print(f'{op_string} router: {router_name}')
                          print(f'==================')
                          rc.format()
          else:
              print('\n*** Only conductors can match router patterns! ***\n')
              sys.exit(1)

      if args.router is not None and \
         len(self.router_dict) == 0:
          rc = self.router_module.create_instance(self.local_info, args.router, args)
          self.router_dict[rc.get_router()] = rc
          self.router_patterns = [ 'placeholder' ]
          self.routers_by_pattern['placeholder'] = [ rc ]
          if args.debug or args.context:
              print(f'Adding default Router')
              rc.format()

  def test_routers(self):
      """
      Output routers matching patterns specified using the order spacified in the -R 
      argument list.  Since multiple routers may match a pattern, sort RouterContexts
      matching a pattern by router name.
      """
  
      def getKey(item):
          """
          Return a router context key for sorting
          """
          return item.get_router()

      router_count = 1

      skip_router = False
      if self.start_after is not None:
          skip_router = True 

      if self.output_file == '':
          for key in self.router_patterns:
              # not pythonic, but readable
              if not key in self.routers_by_pattern:
                  continue
              router_max = len(self.router_dict)
              for router_context in sorted(self.routers_by_pattern[key], key=getKey):
                  if self.start_after is not None and \
                     self.start_after in router_context.get_router():
                      skip_router = False
                      router_count += 1
                      continue
                  if skip_router == True:
                      router_count += 1
                      continue

                  router_context.query_extra_info()
                  self.banner.header(
                      router_context, 
                      router_count, 
                      router_max
                  )
                  self.run_tests(
                      router_context, 
                      router_count)
                  self.banner.trailer(
                      router_context, 
                      router_count, 
                      router_max
                  )
                  router_count += 1
      else:
          with open(self.output_file, "w") as fp:
              for key in self.router_patterns:
                  # not pythonic, but readable
                  if not key in self.routers_by_pattern:
                     continue
                  router_max = len(self.router_dict)
                  for router_context in sorted(self.routers_by_pattern[key], key=getKey):
                      if self.start_after is not None and \
                         self.start_after in router_context.get_router():
                          skip_router = False
                          router_count += 1
                          continue
                          if skip_router == True:
                              router_count += 1
                              continue

                      router_context.query_extra_info()
                      self.banner.header(
                          router_context, 
                          router_count, 
                          router_max, 
                          fp)
                      self.run_tests(
                          router_context, 
                          router_count,
                          fp
                      )
                      self.banner.trailer(
                          router_context, 
                          router_count, 
                          router_max, 
                          fp
                      )
                      fp.write('\n')
                      router_count += 1

  def run_tests(self, router_context, router_count=0, fp=None):
      """
      """
      self.clear_counts()
      router_max = len(self.router_dict)
      test_max   = len(self.tests)
      for test in self.tests:
          if test.enabled == False:
              continue
          if test.test_id not in self.exclude_list:
              test.last_test_id      = test_max
              test.router_index      = router_count
              test.last_router_index = router_max
              status = test.run(
                  self.local_info, 
                  router_context, 
                  self.gql_token, 
                  fp
              )
              self.tally_results(test, status)
      if fp is not None:
          if self.count_results(Output.Status.FAIL) > 0:
              self.banner.header(
                  router_context, 
                  router_count, 
                  router_max
              )
              for test in self.tests:
                  test.test_end_by_status([Output.Status.FAIL])
              self.banner.trailer(
                  router_context, 
                  router_count, 
                  router_max
              )
          else:
              self.banner.header_summary(router_context, self.tests_by_status)
              self.banner.trailer_summary(router_context)

              # create a new output instance to reset state...
      for test in self.tests:
          test.create_output_instance(self.module_dict)


  def load_config(self, args):
      self.config_dict = {}
      self.config_schema_dict = {}

      if self.debug:
          self.paths.dump()

      config_path = self.paths.config_file
      with open(config_path) as config_handle:
          self.config_dict = json.load(config_handle)

      if self.debug:
          print(f"loaded {config_path}")

      schema_path = os.path.join(self.stage_check_path, self.JSON_SCHEMA_FILE)          
      with open(schema_path) as schema_handle:
          self.config_schema_dict = json.load(schema_handle)
      
      if self.debug:
          print(f"loaded {schema_path}")

      try:
          valid = jsonschema.validate(self.config_dict, self.config_schema_dict)
      except Exception as e:
          print("******************************************")
          print("* Error Validating Config! EXITING ")
          print("******************************************")
          print(e)
          sys.exit(1)
      
      # print(f"validated configuration...")

  def load_router_module(self):
      """
      Loads the router context module used to create RouterContext child instances 
      as asset or argument processesing drives router context creation.
      """
      self.router_module = None
      try:
          router_module_name = self.config_dict["RouterContextModule"]
      except KeyError:
          print("******************************************")
          print("* No RouterContextModule defined! EXITING ")
          print("******************************************")
          sys.exit(1)

      try:
          router_module = importlib.import_module(router_module_name)
      except Exception as e:
          print(f"******************************************")
          print(f"* Exception loading {router_module_name}  ")
          print(f"* {e}                                     ")
          print(f"* in: {sys.path}                          ")
          print(f"******************************************")
          print(f"Script-Path:  {os.path.dirname(os.path.realpath(__file__))}")
          print(f"Working-Path: {os.getcwd()}")
          sys.exit(1)

      if hasattr(router_module, "create_instance"):
          self.router_module = router_module
          # print(f"Successfully registered router plugin '{router_module_name}'")
      else:
          print("************************************************")
          print(f"* RouterContextModule {router_context_name}")
          print("* is missing create_instance function; EXITING ")
          print("************************************************")
          sys.exit(1)

  def load_banner(self):
      """
      Loads the Banner module used to create the Banner for each 
      Router's test sequence
      """
      self.banner_module = None
      try:
          banner_module_name = self.config_dict["BannerModule"]
      except KeyError:
          print("***********************************")
          print("* No BannerModule defined! EXITING ")
          print("***********************************")
          sys.exit(1)

      banner_module = importlib.import_module(banner_module_name)

      try:
          banner_module = importlib.import_module(banner_module_name)
      except Exception as e:
          print(f"******************************************")
          print(f"* Exception loading {banner_module_name}  ")
          print(f"* {e}                                     ")
          print(f"* in: {sys.path}                          ")
          print(f"******************************************")
          print(f"Script-Path:  {os.path.dirname(os.path.realpath(__file__))}")
          print(f"Working-Path: {os.getcwd()}")
          sys.exit(1)

      if hasattr(banner_module, "create_instance"):
          self.banner_module = banner_module
          # print(f"Successfully registered banner plugin '{banner_module_name}'")
      else:
          print("************************************************")
          print(f"* BannerModule {banner_context_name}")
          print("* is missing create_instance function; EXITING ")
          print("************************************************")
          sys.exit(1)
      
      # TODO The banner is probably more a property of the router 
      self.banner = self.banner_module.create_instance()

  def load_tests(self, config_path, args):
      """
      Read the json overall test configuration file, and vaidate against
      the schema file.  Process each test contained therein, loading
      the test and output modules, and its json schema.  Validate the
      test instance's json parameters agaimst the test's json schema.
      Finally call the test modules 'create_instance' function to create
      a new test instance derived from AbstractTest.

      TODO:
      This can fail in a bazillion different ways...
      """
      self.tests = []
      self.module_dict = {}
      self.schema_dict = {}
      
      index = 0
      for entry in self.config_dict["Tests"]:
          test_module_base = entry["TestModule"]
          test_module_name = "Test" + test_module_base
          output_name_base = "Output" + test_module_base
          output_module_name = output_name_base + entry["OutputModule"]
          test_schema_key = 'Schema' + test_module_base
          test_schema_file = test_schema_key + '.json'
          if test_module_name not in self.module_dict:
              test_module = importlib.import_module(test_module_name)
              if hasattr(test_module, "create_instance"):
                  self.module_dict[test_module_name] = test_module
                  # print(f"Successfully registered test plugin '{test_module_name}'")
              else:
                  print(f"Module '{test_module_name}' has no create_instance function; skipping")

              if test_module_name not in self.schema_dict:
                  schema_config_path = os.path.join(config_path, test_schema_file)
                  with open(schema_config_path) as schema_handle:
                      self.schema_dict[test_module_name] = json.load(schema_handle)
              json_schema = self.schema_dict[test_module_name]

          valid = jsonschema.validate(entry["Parameters"], json_schema) 
        
          test_module = self.module_dict[test_module_name]
          test = test_module.create_instance(index, entry, args)
          test.create_output_instance(self.module_dict)
          self.tests.append(test)
          index += 1




     














