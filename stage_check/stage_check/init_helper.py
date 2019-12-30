"""
Obtains Local and Global Init Node Information
"""
import os
import json

INITIAL_CONFIG_PATH = '/etc/128technology'
GLOBAL_INIT         = 'global.init'
LOCAL_INIT          = 'local.init'

class NodeInfo:
  """
  NodeInfo class
  """
  def __init__(self):
      self.node_name=''
      self.node_type=''
      self.router_name=''
      self.peer_name=''
      self._read_local_init()
      self._read_global_init(self.node_name)

  def _read_local_init(self):
      """
      Read node's name from local init
      """
      local_init_file_path = os.path.join(INITIAL_CONFIG_PATH, LOCAL_INIT)
      try:
          with open(local_init_file_path, "r") as local_init_pointer:
              json_dict = json.load(local_init_pointer)
          self.node_name = json_dict['init']['id']
      except (IOError, FileNotFoundError):
          self.node_name = ''
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
              pass 
          if len(node_data) != 0:
              self.node_type = node_type
              break

      # extract peer name
      if self.node_type != '':
          for key in json_dict['init'][node_type]:
              if self.node_name != key:
                  self.peer_name = key
                  break
         
      # extract router name
      try:
          self.router_name = json_dict['init']['routerName']
      except KeyError:
          self.router_name=''
          pass

      return self.node_type != ''

  def get_node_name(self):
      return self.node_name

  def get_node_type(self):
      return self.node_type

  def get_peer_name(self):
      return self.peer_name

  def get_router_name(self):
      return self.router_name
