"""
Obtains Local and Global Init Node Information
"""
import os
import subprocess
import socket
import re
import json

"""
    import rpm
    RPM_SITE_PACKAGE_LOADED = True
"""

import version_utils
RPM_SITE_PACKAGE_LOADED = False

INITIAL_CONFIG_PATH = '/etc/128technology'
GLOBAL_INIT         = 'global.init'
LOCAL_INIT          = 'local.init'

class NodeInfo:
  """
  NodeInfo class
  """
  def __init__(self, debug=True):
      self._node_name = ''
      self._node_type = ''
      self._router_name = ''
      self._peer_name = ''
      self._version = None
      self._minion_id = None
      self._debug=debug
      if self._is_128():
          if debug:
              print(f"NodeInfo.__init__: 128T installed on node")
          self._read_local_init()
          self._read_global_init(self.node_name)
          self._get_rpm_version("128T")
          self._read_minion_id()
      else:
          self._node_type = "Unknown"
          self._node_name = socket.gethostname()

  @property
  def debug(self):
      return self._debug

  def _is_128(self):
      paths_to_check = [
          "/usr/lib/systemd/system/128T.service"
      ]
      for path in paths_to_check:
          if not os.path.exists(path):
              return False
      return True

  def _read_local_init(self):
      """
      Read node's name from local init
      """
      local_init_file_path = os.path.join(INITIAL_CONFIG_PATH, LOCAL_INIT)
      try:
          with open(local_init_file_path, "r") as local_init_pointer:
              json_dict = json.load(local_init_pointer)
          self._node_name = json_dict['init']['id']
      except (IOError, FileNotFoundError):
          #assert False, "Cannot open /etc/128technology/local.init"
          self._node_name = ''
          return False
      return True

  def _read_global_init(self, node_name):
      """
      Read node type from global init
      """
      node_types = [ 'conductor', 'control' ]
      global_init_file_path = os.path.join(INITIAL_CONFIG_PATH, GLOBAL_INIT)
      try:
          with open(global_init_file_path, "r") as global_init_pointer:
              json_dict = json.load(global_init_pointer)
      except (IOError, FileNotFoundError):
          return False
      
      # extract node type
      for node_type in node_types:
          try:
              node_data = json_dict['init'][node_type][node_name] 
          except KeyError:
              node_data = {}
              continue 
          if len(node_data) != 0:
              self._node_type = node_type
              break

      # extract peer name
      if self.node_type != '':
          for key in json_dict['init'][node_type]:
              if self._node_name != key:
                  self._peer_name = key
                  break
         
      # extract router name
      try:
          self._router_name = json_dict['init']['routerName']
      except KeyError:
          self._router_name=''
          pass

      return self.node_type != ''

  def _get_rpm_version(self, name):
      global RPM_SITE_PACKAGE_LOADED
      fname = "NodeInfo._get_rpm_version"  

      if not self._version is None:
          if self.debug:
              print(f"{fname}: version already set to '{self._version}'")
          return

      if RPM_SITE_PACKAGE_LOADED:
          if self.debug:
              print(f"{fname}: Extracting version using rpm site-package")
          ts = rpm.TransactionSet()
          mi = ts.dbMatch('name', name)
          try :
              # This is horrible, but since access to rpm bindings is via
              # global site packages, even a pex file cannot control what
              # module version will be used. TODO: Find a better way to
              # access the rpm db using python.
              if hasattr(mi, "next"):
                  h = mi.next()
              else:
                  h = mi.__next__()
              if h['name'] == name:
                  self._version = h['version']
          except StopIteration:
              pass
      else:
          # Even worse -- rpm is a site package (acutally called rpmUtils), 
          # and there is no gurantee its available for python 3.x on a 128T
          # worst thing I've seen in python yet...
          if self.debug:
              print(f"{fname}: Extracting version using version_utils")
          command = ["rpm", "-q", name ]
          try:
              result = subprocess.run(
                   command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
              )
          except Exception as e:
              if self.debug:
                  print(f"{fname}: Exception running shell rpm command!")
                  print(f"{fname}: {e}/{e.__class__.__name__}")
              self._version = None
              return 
                 
          try:
              output = result.stdout.decode()
              output = output.splitlines()
          except Exception as e:
              if self.debug:
                  print(f"{fname}: {e}/{e.__class__.__name__}")
              self._version = None
              return
          if len(output) > 0:
              line = output[0]
              if self.debug:
                  print(f"local_info._get_rpm_version: parse '{line}'")
              rpm_info = version_utils.rpm.package(line)
              self._version = rpm_info.version
      if self.debug:
          print(f"{fname}: version={self._version}")

  def _read_minion_id(self):
      minion_id_path = "/etc/salt/minion_id"
      if os.path.exists(minion_id_path):
          with open(minion_id_path, "r") as fh:
              for line in fh:
                  self._minion_id = line.rstrip('\n')
                  break 

  @property 
  def node_name(self):
      return self._node_name

  @property 
  def node_type(self):
      return self._node_type

  @property 
  def peer_name(self):
      return self._peer_name

  @property 
  def router_name(self):
      return self._router_name

  @property
  def version(self):
      return self._version

  @property 
  def minion_id(self):
       return self._minion_id

  def get_node_name(self):
      return self.node_name

  def get_node_type(self):
      return self.node_type

  def get_peer_name(self):
      return self.peer_name

  def get_router_name(self):
      return self.router_name

  def get_node_count(self):
      count = 1
      if self.get_peer_name() != '':
          count += 1
      return count

  def to_string(self):
      string = f"""\
      Router Name: {self.router_name}
      Node Name:   {self.node_name}
      Node Type:   {self.node_type}
      Peer Name:   {self.peer_name}
      Version:     {self.version}
      Minion ID:   {self.minion_id}
      """
      return string
