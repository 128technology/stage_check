#!/usr/bin/env python36
##############################################################################
#
#   _ __   __ _| |_| |__  ___   _ __  _   _
#  | '_ \ / _` | __| '_ \/ __| | '_ \| | | |
#  | |_) | (_| | |_| | | \__ \_| |_) | |_| |
#  | .__/ \__,_|\__|_| |_|___(_) .__/ \__, |
#  |_|                         |_|    |___/
#
#  Path initialization and a single source for all paths currently used.
#
###############################################################################

import os
import sys
import shutil

class Paths:
  def __init__(self, args):
      self.__runtime_path   = None
      self.__user_home_path = None
      self.__base_path      = None
      self.__config_file    = None
      self.__module_path    = None
      self.__gql_path       = None
      self.__gql_token_file = None

      self._init_base_paths(args)
      self._init_token_path()

  @property
  def runtime_path(self):
      return self.__runtime_path

  @property
  def user_home_path(self):
      return self.__user_home_path

  @property
  def base_path(self):
      return self.__base_path

  @property
  def config_file(self):
      return self.__config_file

  @property
  def module_path(self):
      return self.__module_path

  @property
  def gql_path(self):
      return self.__gql_path

  @property
  def gql_token_file(self):
      return self.__gql_token_file

  def _init_base_paths(self, args):
      """
      HOME/
      |-.stage_check/
        |-config.json (site specific config)
        |-python/
          |- <site-specific-modules>
        |-graphql/
          |-token

      The config file used can be overrriden using a commandline argument.
        args.config_file
      """
      self.__user_home_path = os.path.expanduser("~")

      self.__runtime_path = os.path.dirname(os.path.realpath(__file__))
      sys.path.insert(0, self.runtime_path)

      self.__base_path = os.path.join(self.user_home_path, ".stage_check")
      self.__module_path = os.path.join(self.base_path, "python")
      default_config_file = os.path.join(self.base_path, "config.json")

      if not os.path.exists(self.base_path):
          os.mkdir(self.base_path)
      if not os.path.exists(self.module_path):
          os.mkdir(self.module_path)

      sys.path.insert(0, self.module_path)

      script_config_file = os.path.join(self.runtime_path, "config.json")
      default_config_file = os.path.join(self.base_path, "config.json")
      if not os.path.exists(default_config_file):
          shutil.copyfile(script_config_file, default_config_file)

      if args.config_path is None:
          if args.debug == True:
              print(f"Set config path {default_config_file}")
          self.__config_file = default_config_file
      else:
          self.__config_file = args.config_path

  def _init_token_path(self):
      """
      In order to be backwards compatible, HOME/.graphql/token if it exists,
      is copied to HOME/.stage_check/graphql/token.
      """
      old_token_path = os.path.join(self.user_home_path, ".graphql")
      old_token_file = os.path.join(old_token_path, "token")
      self.__gql_path = os.path.join(self.base_path, "graphql")
      if not os.path.exists(self.gql_path):
          os.mkdir(self.gql_path)
      new_token_file = os.path.join(self.gql_path, "token")
      if os.path.exists(old_token_file):
          shutil.copyfile(old_token_file, new_token_file)
      self.__gql_token_file = new_token_file

  def dump(self):
      print(f"+--------------------")
      print(f"| stage_check paths  ")
      print(f"+--------------------")
      print(f"user_home_path: {self.user_home_path}")
      print(f"base_path:      {self.base_path}")
      print(f"config_file:    {self.config_file}")
      print(f"module_path:    {self.module_path}")
      print(f"gql_path:       {self.gql_path}")
      print(f"gql_token_file: {self.gql_token_file}")
