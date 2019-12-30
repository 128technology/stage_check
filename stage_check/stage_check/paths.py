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
  def __init__(self, args, debug=False):
      self.__debug             = debug
      self.__runtime_path      = None
      self.__user_home_path    = None
      self.__user_base_path    = None
      self.__base_path         = None
      self.__config_file       = None
      self.__module_paths      = []
      self.__gql_path          = None
      self.__gql_token_file    = None

      # system-wide paths.  
      self.__app_name             = "stage_check"
      self.__global_path_library  = os.path.join("/usr/lib", self.__app_name)
      self.__global_path_python   = os.path.join(self.__global_path_library, "python")
      self.__global_path_config   = os.path.join("/etc", self.__app_name + ".d")
      self.__global_path_profiles = os.path.join(self.__global_path_config, "profiles")

      self._init_base_paths(args)
      self._init_token_path()

  @property
  def debug(self):
      return self.__debug

  @property
  def runtime_path(self):
      return self.__runtime_path

  @property
  def user_home_path(self):
      return self.__user_home_path

  @property
  def user_base_path(self):
      return self.__user_base_path

  @property
  def base_path(self):
      return self.__base_path

  @property
  def config_file(self):
      return self.__config_file

  @property
  def module_paths(self):
      return self.__module_paths

  @property
  def profile_path(self):
      return self.__profile_path

  @property
  def gql_path(self):
      return self.__gql_path

  @property
  def gql_token_file(self):
      return self.__gql_token_file

  @property
  def app_name(self):
      return self.__app_name

  @property
  def global_path_library(self):
      return self.__global_path_library

  @property
  def global_path_python(self):
      return self.__global_path_python

  @property
  def global_path_config(self):
      return self.__global_path_config

  @property
  def global_path_profiles(self):
      return self.__global_path_profiles

  def _init_base_paths(self, args):
      """
      /usr/lib/stage_check/
        |- python/  (1)
           |- <site-specific-modules>
      /etc/stage_check
        config.json (2)
        |- profiles (2)
      $HOME/
        |- .stage_check/
          |- graphql/
            |- token

      Prior versions of stage_check copied either the globally available
      or the script's default configuration to the user's stage_check
      directory, which was then used as the preferred source for
      stage_check configuration.

      There are two problems with the past approach:

      (1) As there is now a global config location populated by rpms, upgrades
      to the rpm and included test configuration / suites should be visible to users 
      unless they specifically opt out of using global test configuration / suites.
     
      (2) As stage_check now supports being run as a non-privileged user using
      sudo, there is a security risk in allowing users to specify their own python
      modules to be executed as user root.

      For these reasons, all user configuration will be ignored by stage_check
      for the time being.

      The config file used can still be overriden using a commandline argument, 
      args.config_file, but that config file must utilize the resources provided
      in the global stage_check configuration -- and as such it's value is somewhat
      limited. 
      """
      myname = self.__class__.__name__ + "._init_base_paths"
      self.__user_home_path = os.path.expanduser("~")

      self.__runtime_path = os.path.dirname(os.path.realpath(__file__))
      if os.path.exists(self.__runtime_path):
          self.__module_paths.append(self.__runtime_path)

      if os.path.exists(self.global_path_python):
          self.__module_paths.append(os.path.join(self.global_path_python))

      self.__base_path = os.path.join(self.user_home_path, "." + self.app_name)
      self.__user_base_path = os.path.join(self.user_home_path, "." + self.app_name)
      self.__profile_path = os.path.join(self.base_path, "profiles")

      if not os.path.exists(self.user_base_path):
          os.mkdir(self.user_base_path)

      for path in self.module_paths:
          sys.path.insert(0, path)

      app_config_file = os.path.join(self.global_path_config, "config.json")
      script_config_file = os.path.join(self.runtime_path, "config.json")
      user_config_file = os.path.join(self.user_base_path, "config.json")
      config_file = ""

      if not args.config_path is None:
          config_file = args.config_path
      elif args.generic: 
          config_file = os.path.join(self.__runtime_path, "config.json")  

      self.__base_path    = self.global_path_config
      self.__profile_path = self.global_path_profiles
      if len(config_file) == 0:
            config_file = app_config_file

      self.__config_file = config_file

      if not os.path.exists(self.config_file):
          print(f"\n#######################################################")
          print(f"# Unable to continue, Configuration not found at:")
          print(f"# {self.config_file}")
          print(f"# ")
          print(f"{self.to_string('# ')}")
          print(f"#######################################################")
          sys.exit(1)



  def _init_token_path(self):
      """
      In order to be backwards compatible, HOME/.graphql/token if it exists,
      is copied to HOME/.stage_check/graphql/token.
      """
      old_token_path = os.path.join(self.user_home_path, ".graphql")
      old_token_file = os.path.join(old_token_path, "token")
      if self.debug:
          print(f"OLD_TOKEN_FILE={old_token_file}")
      self.__gql_path = os.path.join(self.user_base_path, "graphql")
      if self.debug:
          print(f"GQL_PATH={self.gql_path}")
      if not os.path.exists(self.gql_path):
          os.mkdir(self.gql_path)
      new_token_file = os.path.join(self.gql_path, "token")
      if self.debug:
          print(f"NEW_TOKEN_FILE={new_token_file}")
      if os.path.exists(old_token_file):
          shutil.copyfile(old_token_file, new_token_file)
      self.__gql_token_file = new_token_file

  def to_string(self, prefix=''):
      retstr  = f"{prefix}+---------------------+\n"
      retstr += f"{prefix}| stage_check paths   |\n"
      retstr += f"{prefix}+---------------------+\n"
      retstr += f"{prefix}user_home_path:       {self.user_home_path}\n"
      retstr += f"{prefix}user_base_path:       {self.user_base_path}\n"
      retstr += f"{prefix}base_path:            {self.base_path}\n"
      retstr += f"{prefix}config_file:          {self.config_file}\n"

      path_count = 1
      module_prefix = f"{prefix}module_paths:         "
      for path in self.module_paths:
          retstr += f"{module_prefix}{path}"
          if path_count == 1:
              module_prefix=f"{prefix}{' ' * 22}"
          path_count += 1

      retstr += f"{prefix}gql_path:             {self.gql_path}\n"
      retstr += f"{prefix}gql_token_file:       {self.gql_token_file}\n"
      retstr += f"{prefix}app_name:             {self.app_name}\n"
      retstr += f"{prefix}global_path_library:  {self.global_path_library}\n"
      retstr += f"{prefix}global_path_python:   {self.global_path_python}\n"
      retstr += f"{prefix}global_path_config:   {self.global_path_config}\n"
      retstr += f"{prefix}global_path_profiles: {self.global_path_profiles}\n"
      return retstr

  def dump(self, prefix=''):
      print(self.to_string(prefix=prefix))

