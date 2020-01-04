###############################################################################
#   _     _                  
#  | |   (_)_ __  _   ___  __
#  | |   | | '_ \| | | \ \/ /
#  | |___| | | | | |_| |>  < 
#  |_____|_|_| |_|\__,_/_/\_\
#
###############################################################################

try:
    from stage_check import RouterContext
except ImportError:
    import RouterContext

import os
import re
import json
import time
import datetime
import shlex
import subprocess
import pprint
import pytz

import sys

class Callbacks(object):
   def run_linux_progress(self, message):
       return True

class Base(object):
  ""
  ""
  SECONDS_PER_MINUTE = 60
  SECONDS_PER_HOUR   = 3600
  SECONDS_PER_DAY    = 86400

  def __init__(self, debug=False, progobj=None, timeout=None):
      # unlike C++, inheritence works in the python class constructor
      self.debug = debug
      self.progobj = progobj
      self.clear_json()
      self.prog_string = None
      self.__timeout = timeout

  @property 
  def json_data(self):
     return self.__json_data

  @json_data.setter
  def json_data(self, value):
      self.__json_data = value

  @property 
  def debug(self):
     return self.__debug

  @debug.setter
  def debug(self, value):
      self.__debug = value

  @property 
  def progobj(self):
     return self.__progobj

  @progobj.setter
  def progobj(self, value):
      self.__progobj = value

  @property
  def timeout(self):
      return self.__timeout

  def clear_json(self):
      self.json_data = {}

  def is_full_json(self):
      """
      Fully converted to json?
      """
      return False

  def update_by_type(self, dest, source):
      """
      Use inheritence instead?
      """
      if isinstance(dest, list):
          dest.extend(source)
      elif isinstance(dest, dict):
          dest.update(source)

  def convert_to_json(self):
      return self.json_data

  def run_linux(
      self,
      local_info,
      router_context,
      node_type,
      command,
      regex_filter,
      output_lines,
      error_lines
   ):
      """
      """
      
      salt_error_indicators = []
      salt_error_indicators.append(r'^\s*Minion did not return.')
      salt_error_indicators.append(r'^\s*No minions matched the target.')

      router_context.query_node_info()
      asset_id = router_context.get_asset_by_type(node_type)

      if  asset_id is None or asset_id == '':
          error_lines.append(f"Missing asset info for {node_type} node")
          return 0 

      output_lines.clear()
      linux_command = ''
      command_list  = []
      if local_info.get_node_type() == 'conductor':
          if isinstance(command, str):
              linux_command = "t128-salt " + asset_id + " cmd.run '" + command + "'"
              if self.timeout is not None:
                  linux_command += f" timeout={self.timeout}"
          elif isinstance(command, list):
              command_list = ["t128-salt", asset_id, "cmd.run"]
              command_list.extend(command)
              if self.timeout is not None:
                  comand_list.append(f"timeout={self.timeout}")
          else:
              return 1
      else:
          if isinstance(command, str):
              linux_command = command
          elif isinstance(command, list):
              command_list = command.copy()
          else:
              return 1

      if len(command_list) == 0:
          command_list = shlex.split(linux_command) 

      if self.debug:
          if regex_filter is not None:
              print(f'Regex Filter:  {regex_filter}')
          print(f'Linux Command: {linux_command}')
          print(f'Asset ID:      {asset_id}')
          print(f'Command List:  {pprint.pformat(command_list)}')

      # subprocess.DEVNULL is python 3.3+ only
      if self.progobj is not None:
          prog_string = f"Run '{linux_command}'..."
          if self.prog_string is not None:
              prog_string = self.prog_string
          self.progobj.run_linux_progress(prog_string)

      pipe = subprocess.Popen(command_list,
                              stdin=open(os.devnull, 'rb'),
                              bufsize=0,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL,
                              close_fds=True)
      for line in iter(pipe.stdout.readline, b''):
          bline = line.rstrip()
          xline = bline.decode('utf-8') 
          if self.debug:
              print(f'Consider: {xline}')
          if regex_filter is not None and \
             regex_filter != '' and \
             not re.search(regex_filter, xline):
              continue
          output_lines.append(xline)
          if self.debug:
              print(f'*Matched: {xline}')
          for indicator in salt_error_indicators:
              if re.search(indicator, xline):
                  error_lines.append(xline.lstrip())

      if self.debug:
          pprint.pprint(output_lines)

      return_code = pipe.poll()
      return return_code  

  def run_linux_json(
      self,
      local_info,
      router_context,
      node_type,
      command,
      error_lines,
      json_data
  ):
      """  
      """
      output_lines = []
      json_data.clear()

      shell_status = self.run_linux(
          local_info,
          router_context,
          node_type,
          command,
          None,
          output_lines,
          error_lines
      )

      if len(error_lines) == 0:
          jdata = self.convert_to_json(output_lines)
          self.update_by_type(json_data, jdata)
      return shell_status     

  def normalize_datetime(
      self, 
      input_time,
      tz_regex="(.*?) ([^ ]+)$", 
      tz_format="%a %Y-%m-%d %H:%M:%S"
  ):
      """
      Ideally all Linux output converted to json would use UTC datetimes.  However,
      some Linux comands (i.e. systemctl) do not output UTC date / times.  

      This is a hackish workaround for writing addiional command-line python scripts
      that move the conversion work to the remote host. The local timezone name is set
      to the remote timezone name and the datetime converted to UTC, whereupon the original
      timezone name is retored.

      Since timezone names are a poor substitute for GMT offests, there will be times when 
      this approach will not yield the desired results.
      """
      dt_utc = None
      orig_zone = time.strftime("%Z")
      tz_match = re.search(tz_regex, input_time)

      if tz_match is not None: 
          if tz_match.group(1) is None or \
              tz_match.group(2) is None:
              return None
          # set the remote timezone
          time_string = tz_match.group(1)
          tz_string = tz_match.group(2)
          os.environ['TZ'] = tz_string
          time.tzset()
          dt_local = datetime.datetime.strptime(time_string, tz_format)
          dt_utc = dt_local.astimezone(pytz.utc)
          # restore the local timezone
          os.environ['TZ'] = orig_zone
          time.tzset()
          del os.environ['TZ']
      return dt_utc

class Ethtool(Base):
  """
  """
  def __init__(self, debug=False, progobj=None):
      super().__init__(debug=debug, progobj=progobj)

  def convert_to_json(
         self,
         text_lines
      ):
      """
      This does a quick and dirty conversion of the output
      text into json...

      For example:
      Advertised link modes:  10baseT/Half 10baseT/Full
                              100baseT/Half 100baseT/Full
                              1000baseT/Full

      is only converted to:
      {
          "Advertised link modes" : "10baseT/Half 10baseT/Full"
      }
      """
      regex=r'^\s*(\w[/\(\)\w\d\s]+[\w\)])\s*:\s*(.*)$'
      self.clear_json()
      index = 0
      for line in text_lines:
          if self.debug:
              print(f"{index}: {line}")
          matches = re.search(regex, line)
          if matches is not None:
              key   = matches.group(1)
              key = key.replace(' ', '_')
              value = matches.group(2)
              if key is not None and \
                  value is not None and \
                  value != '':
                  self.json_data[key] = value
          index += 1 
      return self.json_data
      
  def run_linux_args(
      self,
      local_info,
      router_context,
      node_type,
      intf,
      error_lines,
      json_data
    ):
      """
      Get json output for ethtool command:

      *local_info*     - Local context
      *router_context* - Target router
      *node_type*      - Which node
      *intf*           - Linux interface / device name
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      command = f"ethtool {intf}"
      status = self.run_linux_json(
        local_info,
        router_context,
        node_type,
        command,
        error_lines,
        json_data
       )
      json_data["linux_device"] = intf
      return status
       
    
class Coredumpctl(Base):
  """
  """ 
  def __init__(self, debug=False, progobj=None):
      super().__init__(debug=debug, progobj=progobj)

  def clear_json(self):
      self.json_data = []

  def is_full_json(self):
      return True

  def convert_to_json(
         self,
         text_lines
      ):
      """
      """
      json_fields = [
         "TIME",
         "PID",
         "UID",
         "GID",
         "SIG", 
         "PRESENT",
         "EXE"
      ]
      regex=r'(\w.*?\w)\s+([\d]+)\s+([\d]+)\s+([\d]+)\s+([\d]+)\s+(\*?)\s+(.*)$'
      self.clear_json()
      index = 0
      for line in text_lines:
          if self.debug:
              print(f"{index}: {line}")
          matches = re.search(regex, line)
          group_index = 1
          if matches is not None:          
              data = {}
              for key in json_fields:
                  if matches.groups(group_index) is not None:
                      data[key] = matches.group(group_index)
                  group_index += 1
              if len(data) > 0:
                  if "TIME" in data:
                      dt_core  = self.normalize_datetime(data["TIME"])
                      dt_epoch = datetime.datetime(1970,1,1)
                      dt_epoch = dt_epoch.replace(tzinfo=pytz.UTC)
                      epoch_secs = (dt_core - dt_epoch).total_seconds()
                      data["EPOCH_TIME"] = epoch_secs
                  self.json_data.append(data)
          index += 1 
      return self.json_data

  def run_linux_args(
      self,
      local_info,
      router_context,
      node_type,
      error_lines,
      json_data
    ):
      """
      Get json output for "coedumpctl list" command:

      *local_info*     - Local context
      *router_context* - Target router
      *node_type*      - Which node
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      command = f"coredumpctl list"
      status = self.run_linux_json(
        local_info,
        router_context,
        node_type,
        command,
        error_lines,
        json_data
       )
      return status


  def cores_newer_than_secs(self, seconds):
      """
      Cores: 3 (since last boot)  1 (since last start)
      """
      results = []
      now_in_secs = int(time.time())
      for core in self.json_data:
         if self.debug:
             print(f"{now_in_secs} - {core['EPOCH_TIME']} ({now_in_secs - int(core['EPOCH_TIME'])}) < {seconds}") 
         if now_in_secs - int(core["EPOCH_TIME"]) < seconds:
            results.append(core)
      return results

  def cores_newer_than_epoch(self, epoch_time):
      """
      Cores: 3 (since last boot)  1 (since last start)
      """
      now_in_secs = int(time.time())
      seconds = now_in_secs - epoch_time
      return self.cores_newer_than_secs(seconds)


class SystemctlStatus(Base):
  """
  """ 
  def __init__(self, debug=False, progobj=None):
      super().__init__(debug=debug, progobj=None)

  def convert_to_json(
         self,
         text_lines
      ):
      self.clear_json()
      index = 0
      for line in text_lines:
          if self.debug:
              print(f"{index}: {line}")
          matches = re.match(r'\s+Active:\s+(\w+)\s+\((\w+)\)\s+since\s+([^;]+)', line)
          if matches is not None:
              if matches.group(1) is not None:
                  self.json_data["state_1"] = matches.group(1)
              if matches.group(2) is not None:
                  self.json_data["state_2"] = matches.group(2)
              if matches.group(3) is not None:
                  self.json_data["time"] = matches.group(3)
                  dt_start = self.normalize_datetime(self.json_data["time"])
                  dt_epoch = datetime.datetime(1970,1,1)
                  dt_epoch = dt_epoch.replace(tzinfo=pytz.UTC)
                  epoch_secs = (dt_start - dt_epoch).total_seconds()
                  self.json_data["epoch_time"] = epoch_secs
                  dt_now = datetime.datetime.now(datetime.timezone.utc)
                  delta_secs = (dt_now - dt_start).total_seconds()
                  if self.debug:
                      print(f"dt_epoch: {dt_epoch}")
                      print(f"dt_start: {dt_start}")
                      print(f"dt_now:   {dt_now}")
                  self.json_data["uptime_days"] = int(delta_secs / self.SECONDS_PER_DAY)
                  delta_secs = int(delta_secs % self.SECONDS_PER_DAY)
                  if self.debug:
                      print(f"SystemctlStatus: days: {self.json_data['uptime_days']} remsecs: {delta_secs}")
                  self.json_data["uptime_hours"] = int(delta_secs / self.SECONDS_PER_HOUR)
                  delta_secs = int(delta_secs % self.SECONDS_PER_HOUR)
                  if self.debug:
                      print(f"SystemctlStatus: hours: {self.json_data['uptime_hours']} remsecs: {delta_secs}")
                  self.json_data["uptime_minutes"] = int(delta_secs / self.SECONDS_PER_MINUTE)
                  delta_secs = int(delta_secs % self.SECONDS_PER_MINUTE)
                  if self.debug:
                      print(f"SystemctlStatus: minutes: {self.json_data['uptime_minutes']} remsecs: {delta_secs}")
                  self.json_data["uptime_seconds"] = delta_secs
          matches = re.match(r'\s+Main PID:\s+(\d+)\s+\(([^\)]+)', line)
          if matches is not None:
              if matches.group(1) is not None:
                  self.json_data["Main_PID"] = matches.group(1)
              if matches.group(2) is not None:
                  self.json_data["Main_Process"] = matches.group(2)
          index += 1
      return self.json_data

  def run_linux_args(
      self,
      local_info,
      router_context,
      node_type,
      service,
      error_lines,
      json_data
    ):
      """
      Get json output for ethtool command:

      *local_info*     - Local context
      *router_context* - Target router
      *node_type*      - Which node
      *service*        - Systemd service to query
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      command = f"systemctl status {service}"
      status = self.run_linux_json(
        local_info,
        router_context,
        node_type,
        command,
        error_lines,
        json_data
       )
      json_data["service"] = service
      return status

 
class Uptime(Base):
  def __init__(self, debug=False, progobj=None):
      super().__init__(debug=debug, progobj=progobj)

  def is_full_json(self):
      return True

  def convert_to_json(
         self,
         text_lines
      ):
      patterns = [
         {
             # 02:25:02 up 73 days, 40 min,  1 user,  load average: 2.01, 1.56, 1.60
             "regex" : r"\s*[^\s]+\s+up\s+([\d]+)\s+day[s]?,\s+([\d]+):([\d]+),\s+(\d+)\s+user[s]?,\s+load average:\s+([^,]+), ([^,]+), ([\.\d]+)",
             "keys"  : { "uptime_days" : 1, "uptime_hours" : 2, "uptime_minutes" : 3, "users" : 4, "load_1" : 5, "load_5" : 6, "load_15" : 7 }
         },
         {
             # 23:11:40 up  8:16,  1 user,  load average: 2.71, 2.30, 2.01         
             "regex" : r"\s*[^\s]+\s+up\s+([\d]+):([\d]+),\s+(\d+)\s+user[s]?,\s+load average:\s+([^,]+), ([^,]+), ([\.\d]+)",
             "keys"  : { "uptime_hours" : 1, "uptime_minutes" : 2, "users" : 3, "load_1" : 4, "load_5" : 5, "load_15" : 6 }
         },
         {
             # 02:25:02 up 73 days, 40 min,  1 user,  load average: 2.01, 1.56, 1.60
             "regex" : r"\s*[^\s]+\s+up\s+([\d]+)\s+day[s]?,\s+([\d]+)\s+min,\s+(\d+)\s+user[s]?,\s+load average:\s+([^,]+), ([^,]+), ([\.\d]+)",
             "keys"  : { "uptime_days" : 1, "uptime_minutes" : 2, "users" : 3, "load_1" : 4, "load_5" : 5, "load_15" : 6 }
         },
         {
             # 20:19:54 up 54 min,  4 users,  load average: 1.69, 1.96, 1.92
             "regex" : r"\s*[^\s]+\s+up\s+([\d]+)\s+min,\s+(\d+)\s+user[s]?,\s+load average:\s+([^,]+), ([^,]+), ([\.\d]+)",
             "keys"  : { "uptime_minutes" : 1, "users" : 2, "load_1" : 3, "load_5" : 4, "load_15" : 5 }
         }
      ]
      self.clear_json()
      index = 0
      for line in text_lines:
          secs = 0
          if self.debug:
              print(f"{index}: {line}")
          for pattern in patterns:
              matches = re.match(pattern["regex"], line)
              if matches is not None:
                  self.json_data["uptime_days"] = 0
                  self.json_data["uptime_hours"] = 0
                  self.json_data["uptime_minutes"] = 0
                  self.json_data["uptime_as_seconds"] = 0
                  self.json_data["load_1" ] = 0.0
                  self.json_data["load_5"]  = 0.0
                  self.json_data["load_15"] = 0.0
                  for key in pattern["keys"]:
                      group_index = pattern["keys"][key]
                      try:
                          if key == "uptime_days":
                              self.json_data[key] = int(matches.group(group_index))
                              secs = secs + self.SECONDS_PER_DAY * int(self.json_data[key])                                         
                          elif key == "uptime_hours":
                              self.json_data[key] = int(matches.group(group_index))
                              secs = secs + self.SECONDS_PER_HOUR * int(self.json_data[key])
                          elif key == "uptime_minutes":
                              self.json_data[key] = int(matches.group(group_index))
                              secs = secs + self.SECONDS_PER_MINUTE * int(self.json_data[key])
                          elif key == "users":
                              self.json_data[key] = int(matches.group(group_index))
                          elif key == "load_1": 
                              self.json_data[key] = float(matches.group(group_index))
                          elif key == "load_5":
                               self.json_data[key] = float(matches.group(group_index))
                          elif key == "load_15":
                               self.json_data[key] = float(matches.group(group_index))
                      except IndexError:
                          pass
                  self.json_data["uptime_as_seconds"] = secs
                  break
          index += 1
      return self.json_data

  def run_linux_args(
      self,
      local_info,
      router_context,
      node_type,
      error_lines,
      json_data
    ):
      """
      Get json output for ethtool command:

      *local_info*     - Local context
      *router_context* - Target router
      *node_type*      - Which node
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      command = f"uptime"
      status = self.run_linux_json(
        local_info,
        router_context,
        node_type,
        command,
        error_lines,
        json_data
       )
      return status
   

class BGPSummary(Base): 
  def __init__(self, debug=False, progobj=None):
      super().__init__(debug=debug, progobj=progobj)

  def clear_json(self):
      self.json_data = []

  def is_full_json(self):
      return False

  def convert_to_json(
      self,
      text_lines
  ):
      #Neighbor        V         AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd
      #172.27.232.15   4      64794  317684  264701        0    0    0 01w6d21h           40
      regex=r'\s*([^\s]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([^\s]+)\s+(\d+)'
      string_fields=[
         "Neighbor",
         "Version",
         "AS",
         "MsgRcvd",
         "MsgSent",
         "TblVer",
         "InQ",
         "OutQ",
         "Up/Down",
         "State"
      ]
      int_fields=[
         "Neighbor",
         "Version",
         "AS",
         "MsgRcvd",
         "MsgSent",
         "TblVer",
         "InQ",
         "OutQ",
         "Up/Down",
         "PfxRcvd"
      ]
      self.clear_json()
      index = 0
      for line in text_lines:
          if self.debug:
              print(f"{index}: {line}")
          matches = re.match(regex, line)
          if matches is not None:
              entry = {}
              group_index = 1
              list_index = 0
              for key in string_fields:
                  try:
                      value = matches.group(group_index)
                      try:
                          intkey = int_fields[list_index]
                          entry[intkey] = int(value)
                      except (ValueError, IndexError) as e:
                          entry[key] = value
                  except (KeyError, IndexError) as e:
                      pass
                  group_index += 1
                  list_index += 1
              self.json_data.append(entry)  
          index += 1
      return self.json_data                
  
  def run_linux_args(
      self,
      local_info,
      router_context,
      node_type,
      error_lines,
      json_data
    ):
      """
      Get json output for 'show ip bgp summary' vtysh command

      *local_info*     - Local context
      *router_context* - Target router
      *node_type*      - Which node
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      command = 'vtysh -c "show ip bgp summary"'
      status = self.run_linux_json(
        local_info,
        router_context,
        node_type,
        command,
        error_lines,
        json_data
       )
      return status

class IPA(Base):
  def __init__(self, debug=False, progobj=None):
      super().__init__(debug=debug, progobj=progobj)

  def clear_json(self):
      self.json_data = []

  def is_full_json(self):
      return False

  def convert_to_json(
      self,
      text_lines
  ):
      Flags = [
          "UP",
          "BROADCAST",
          "DEBUG",
          "LOOPBACK",
          "POINTTOPOINT",
          "RUNNING",
          "NOARP",
          "PROMISC",
          "NOTRAILERS",
          "ALLMULTI",
          "MASTER",
          "SLAVE",
          "MULTICAST",
          "PORTSEL",
          "AUTOMEDIA",
          "DYNAMIC",
          "LOWER_UP",
          "DORMANT",
          "ECHO"
      ]
      #8: enp0s22u1u2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
      #link/ether 42:3d:6f:4d:83:70 brd ff:ff:ff:ff:ff:ff
      #inet 169.254.1.2/30 brd 169.254.1.3 scope global kni20
      regex = r'\s*(\d+):\s+(\w+):\s+<([A-Z,_]+)>\s+(.*)'
      regex_link = r'\s*link/ether\s+([^\s]+)\s+brd\s+([^\s]+)'
      regex_inet = r'\s*inet\s+([^\s]+)\s+brd\s+([^\s]+)'
      self.clear_json()
      index = 0
      data = {}
      for line in text_lines:
          if self.debug:
              print(f"{index}: {line}")
          matches = re.match(regex, line)
          if matches is not None:
              if len(data) > 0:
                   self.json_data.append(data)
              data = {}
              try:
                  data["index"] = int(matches.group(1))
              except IndexError:
                  pass
              try:
                  data["device"] = matches.group(2)
              except IndexError:
                  pass
              try:
                  flags = matches.group(3)
                  for flag in Flags:
                      data["Flags_" + flag] = False
                  flag_list = flags.split(',')
                  for flag in flag_list:
                      data["Flags_" + flag] = True
              except IndexError:
                  pass
              try:
                  items = matches.group(4)
                  item_list = items.split(' ')
                  key = None
                  for item in item_list:
                      if key is None:
                          key = item
                      else:
                          try:
                              value = int(item)
                          except ValueError:
                              value = item
                              pass
                          data[key] = item
                          key = None
              except IndexError:
                  pass
          matches = re.match(regex_link, line)
          if matches is not None:
              try:
                  data["mac"] = matches.group(1)
              except IndexError:
                  pass
              try:
                  data["broadcast-mac"] = matches.group(2)
              except IndexError:
                  pass
          matches = re.match(regex_inet, line)
          if matches is not None:
              try:
                  address_string = matches.group(1)
                  address_elements = address_string.split('/')
                  data["address"] = address_elements[0]
                  data["address-prefix"] = address_elements[1]
              except IndexError:
                  pass
              try:
                  data["broadcast-address"] = matches.group(2)
              except IndexError:
                  pass
          index += 1
      if len(data) > 0:
          self.json_data.append(data)
      return self.json_data

  def run_linux_args(
      self,
      local_info,
      router_context,
      node_type,
      namespace,
      error_lines,
      json_data
    ):
      """
      Get json output for 'show ip bgp summary' vtysh command

      *local_info*     - Local context
      *router_context* - Target router
      *node_type*      - Which node
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      if namespace is None or \
         namespaces == '':
          command = "ip address"
      else:
          command = f"netns exec {namespace} ip address"

      status = self.run_linux_json(
        local_info,
        router_context,
        node_type,
        command,
        error_lines,
        json_data
       )

      # update both the class cache and the caller's json data
      if namespace is not None and \
         namespace != '':       
          for entry in self.json_data:
              entry["namespace"] = namespace
          for entry in json_data:
              entry["namespace"] = namespace              

      return status


class T1Detail(Base):
  def __init__(self, debug=False, progobj=None):
      super().__init__(debug=debug, progobj=progobj)

  def is_full_json(self):
      return True

  def convert_to_json(self, text_list):
      """
      Override

      *text_list*    - List of output lines
      *json_data*    - Output dictionary of exracted key/value pairs
      """
      patterns = [
         {
             "pattern"  : r'^\s*(\w[/\(\)\w\d\s]+[\w\)])\s*:\s*([\w\d]+)(\s*\|\s*([\w\s]+\w)\s*:\s*([\w\d]+)){0,1}',
             "formats"  : [ 
                 {"key_index" : 1, "value" : 2}, 
                 {"key_index" : 4, "value" : 5} 
              ]
         },
         {
             "pattern"  : r'^\s*(Rx Level)\s*:\s*[><=]\s*([0-9\.-]+)db',
             "formats"  : [ 
                 {"key_name" : "Rx_Level_High",  "value" : 2} 
             ]
         },
         #Rx Level  : -7.5db to -10db
         {
            "pattern"  : r'^\s*(Rx Level)\s*:\s*([0-9\.-]+)db\s*to\s*([0-9\.-]+)db',
             "formats"  : [ 
                 {"key_name" : "Rx_Level_High", "value" : 2}, 
                 {"key_name" : "Rx_Level_Low", "value" : 3}  
             ]
         }
      ]

      count=0
      self.clear_json()
      for line in text_list:
          if self.debug:
              print(f"{count}:...{line}")
          count += 1
          for entry in patterns:
              matches = re.search(entry["pattern"], line)
              if matches is not None:
                  for item in entry["formats"]:
                      try:
                          if 'key_index' in item:
                              key_index = item["key_index"]
                              key = matches.group(key_index)
                          else:
                              key = item['key_name']
                          if key is None:
                              continue
                          # in order to be used as a variable in expressions, keys cannot contain
                          # spaces.  Thus ' ' will be replaced by '_'.  Ultimately an escape
                          # character of some sort may be required...
                          key = key.replace(' ', '_')
                          key = re.sub(r'[\(\)]', '', key)
                          # Unfortunately the output contains 2 identical keys, this
                          # is how its resolved for now, which pretty much breaks it
                          # for the abstract case :-(
                          if key in self.json_data:
                              key = 'Tx' + key
                          value_index = item["value"]
                          if self.debug:
                              print(f"json_data[{key}] = {matches.group(value_index)}")
                          self.json_data[key] = matches.group(value_index)
                      except (KeyError, ValueError, IndexError) as e:
                          if self.debug:
                              print(f"EXCEPTION: {e}")
                          pass
                  break
              else:
                  if self.debug:
                      print(f"Mismatch {entry['pattern']}")

      return self.json_data

  def get_command(self, namespace, linux_device):
      if namespace is None or \
         namespace == '':
          command = "ip address"
      else:
          command = f"netns exec {namespace} ip address"

      command = 'ip netns exec ' + namespace + ' wanpipemon -i ' + linux_device + ' -c Ta'
      return command

  def run_linux_args(
      self,
      local_info,
      router_context,
      node_type,
      namespace,
      linux_device,
      error_lines,
      json_data
    ):
      """
      Get json output for 'show ip bgp summary' vtysh command

      *local_info*     - Local context
      *router_context* - Target router
      *node_type*      - Which node
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      if namespace is None or \
         namespace == '':
          command = "ip address"
      else:
          command = f"netns exec {namespace} ip address"

      command = self.get_command(namespace, linux_device)

      status = self.run_linux_json(
        local_info,
        router_context,
        node_type,
        command,
        error_lines,
        json_data
       )

      # update both the class cache and the caller's json data
      if namespace is not None and \
         namespace != '':       
              self.json_data["namespace"] = namespace
              json_data["namespace"] = namespace
      if linux_device is not None and \
         linux_device != '':       
              self.json_data["linux_device"] = linux_device
              json_data["linux_device"] = linux_device

      return status

class LogFilesSince(Base):
  def get_entry_key(item):
      key = 0
      matches = re.search(r'\.([^\.]*)\.log', item['file'])
      if matches is not None:
          try:
              key = int(matches.group(1))
          except (KeyError, ValueError, IndexError) as e:
              pass
      return key
      
  def __init__(self, debug=False, progobj=None, past_hours=0):
      super().__init__(debug=debug, progobj=progobj)
      self.past_hours = past_hours
      self.indent_string = 'None'
      self.now_pattern = "%b %d %H:%M:%S %Y [%Z]"
      self.date_pattern = "%b %d %H:%M:%S %Y"
      self.date_regex = r"\s*([A-Za-z]+\s+\d+\s+\d+:\d+:\d+)"
      self.json_prefix = "JSON: "
      self.json_indent = "None"
      self.prog_string = "Finding logfiles to match..."

  def clear_json(self):
      self.json_data = []

  def is_full_json(self):
      return True

  def convert_to_json(self, text_lines):
      regex  = r'\s*JSON:\s*(.*)'
      look_back_seconds = self.past_hours * self.SECONDS_PER_HOUR

      self.debug = True

      self.clear_json()
      local_data = {}
      index = 0
      for line in text_lines:
          if self.debug:
              print(f"{index}: {line}")
          try:
              matches = re.match(regex, line)
              if matches is not None:
                  json_string = matches.group(1)
                  local_data = json.loads(json_string)
                  break
          except Exception as e:
              print("JSON Parser Exception")
              continue
          index += 1
      try:
          dt_now = self.normalize_datetime(
              local_data["now"], 
              tz_regex="(.*?) \\[([^\\]]+)\\]$", 
              tz_format="%b %d %H:%M:%S %Y"
          )
      except Exception as e:
          print(f"NowTime exception {e} {e.__class__.__name__}")
          dt_now = None

      if dt_now is not None:
          year = dt_now.year
          for entry in local_data["files"]:
              try:
                  end_string = entry["end"]
                  # force this year for now...
                  end_string += f" {year}"
                  dt_end = datetime.datetime.strptime(end_string, self.date_pattern)
                  dt_end = dt_end.replace(tzinfo=pytz.UTC)
              except (KeyError, ValueError) as e:
                  print(f"File Entry Exception {e}")
                  continue

              delta_secs = (dt_now - dt_end).total_seconds()
              if self.debug: 
                  print(f"LogFilesSince: {entry['file']}: delta_hours: {delta_secs / self.SECONDS_PER_HOUR} past_hours: {self.past_hours}")

              if look_back_seconds == 0:
                  self.json_data.append(entry)
                  continue

              if delta_secs < look_back_seconds:
                  self.json_data.append(entry)
                  continue
      self.json_data = sorted(self.json_data, key=LogFilesSince.get_entry_key)
      if self.debug:
          print("======= Linux.LogFilesSince.convert2json start =======")
          pprint.pprint(self.json_data)
          print("======= Linux.LogFilesSince.convert2json end =======")
      return self.json_data

              
  def run_linux_args(
      self,
      local_info,
      router_context,
      node_type,
      log_path,
      log_glob,
      past_hours,
      error_lines,
      json_data
  ):
      date_pattern = self.date_pattern
      self.past_hours = past_hours
      self.prog_string = f"Search for {log_glob} newer than {past_hours}h..."
      #
      # print(f"{variable"} cannot be used
      # single quotes cannot be used... (possibly if escaped)
      #
      # Data is output as a json string for ease of converting to json...
      #
      # Python indention in lieu of proper scoping sucks, just saying 
      command = f"""python3.6 -c 'exec(\"\"\"import pathlib, os, time, re, datetime, json
debug={self.debug}
path_list=pathlib.Path("{log_path}").glob("{log_glob}")
first_str=""
last_str=""
pattern="{self.date_regex}"
local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
dt_now = datetime.datetime.now(tz=local_tz)
now_string = dt_now.strftime("%b %d %H:%M:%S %Y [%Z]")
json_out = dict()
json_list = []
json_out["files"] = json_list
json_out["now"] = now_string

for path in path_list:
    fpath=str(path)
    with open(fpath, "rb") as fh:
        next(fh)
        next(fh)
        first=next(fh).decode()
        matches=re.search(pattern,first)
        if matches is not None:
            first_str=matches.group(1)
        fh.seek(-1024, os.SEEK_END)
        last=fh.readlines()[-1].decode()
        matches=re.search(pattern, last)
        if matches is not None:
             last_str=matches.group(1)
             entry=dict()
             entry["file"]  = fpath
             entry["start"] = first_str
             entry["end"]   = last_str
             json_list.append(entry)
print("{self.json_prefix}" + json.dumps(json_out, indent={self.json_indent})) \"\"\")'
"""
      command_list = [ command ]
      status = self.run_linux_json(
         local_info,
         router_context,
         node_type,
         command_list,
         error_lines,
         json_data
      )
      return status

class LogFileMatches(Base):
  def __init__(
          self, 
          debug=False, 
          progobj=None, 
          past_hours=0, 
          max_lines=0,
          extra_granularity=False
  ):
      super().__init__(debug=debug, progobj=progobj)

      self.past_hours = past_hours
      self.max_lines = max_lines
      self.extra_granularity = extra_granularity

      self.date_pattern = "%b %d %H:%M:%S %Y"
      self.date_regex = r"\s*([A-Za-z]+\s+\d+\s+\d+:\d+:\d+)"

      self.json_prefix = "JSON: "
      self.json_indent = "None"
      self.prog_string = "Matching patterns..."

  def convert_to_json(self, text_lines):
      regex  = r'\s*JSON:\s*(.*)'

      self.clear_json()      
      index = 0
      for line in text_lines:
          if self.debug:
              print(f"{index}: {line}")
          try:
              matches = re.match(regex, line)
              if matches is not None:
                  json_string = matches.group(1)
                  local_data = json.loads(json_string)
                  self.json_data.update(local_data)
                  break
          except (KeyError, IndexError) as e:
              print("JSON Parser Exception")
              continue
          index += 1

      return self.json_data

  def run_linux_args(
      self,
      local_info,
      router_context,
      node_type,
      log_path,
      log_file_list,
      include_patterns,
      exclude_patterns,
      error_lines,
      json_data
  ):
      pattern_fstring = ""
      pattern_count_fstring = ""
      for pattern in include_patterns:
          if len(pattern_fstring) > 0:
              pattern_fstring += ","
          pattern_fstring += '"' + pattern  + '"'
          if len(pattern_count_fstring) > 0:
              pattern_count_fstring += ","
          pattern_count_fstring += "0"
      exclude_fstring = ""
      exclude_count_fstring = ""
      for pattern in exclude_patterns:
          if len(exclude_fstring) > 0:
              exclude_fstring += ","
          exclude_fstring += '"' + pattern  + '"'
          if len(pattern_count_fstring) > 0:
              exclude_count_fstring += ","
          exclude_count_fstring += "0"
      file_fstring = ""
      for fn in log_file_list:
          if len(file_fstring) > 0:
              file_fstring += ","
          file_fstring += '\"' + fn  + '\"'
      seconds_past = self.past_hours * self.SECONDS_PER_HOUR
      command = f"""python3.6 -c 'exec(\"\"\"import re, os, json, datetime
max_lines={self.max_lines}
dt_now = datetime.datetime.now()
now_year = dt_now.year
debug={self.debug}
extra_granularity = {self.extra_granularity}
patterns=[{pattern_fstring}]
re_patterns = []
for pattern in patterns:
    re_patterns.append(re.compile(pattern))
re_date = re.compile("{self.date_regex}")
excludes=[{exclude_fstring}]
re_excludes = []
for exclude in excludes:
    re_excludes.append(re.compile(exclude))
files=[{file_fstring}]
match_counts=[{pattern_count_fstring}]
match_discard_counts=[{pattern_count_fstring}]
json_out=dict()
matches = []
json_out["matches"] = matches
matching_files = dict()
matching_patterns = dict()
total_matches = 0
total_lines = 0
no_match_lines = 0
match_lines = 0
total_excludes = 0
break_max_lines = False
for fn in files:
    fn = os.path.join("{log_path}", fn)
    with open(fn, "r", buffering=(2<<20) + 8) as fh:
        line_count=0
        skip_time_test=False
        for line in fh:
            if max_lines > 0 and \
               total_lines >= max_lines:
                break_max_lines = True
                break
            pindex=0
            matched=False
            dt_line = None
            delta_secs = 0
            skip_match = False
            for re_exclude in re_excludes:
                if re_exclude.search(line):
                    total_excludes += 1
                    skip_match = True
                    break
            if skip_match == True:
                continue
            for re_pattern in re_patterns:
                pattern = re_pattern.pattern
                if re_pattern.search(line):
                    # print("MATCH[" + str(pindex) + "]: " + str(match_counts[pindex]) + "/" + str(total_matches) + " "  + pattern + " " + str(line_count) + ":" + line)
                    if extra_granularity == True and \
                        dt_line is None:
                        dt_matches = re_date.search(line)
                        if dt_matches is not None:
                            try:
                                dt_string = dt_matches.group(1)
                                dt_string += " " + str(now_year)
                                dt_line = datetime.datetime.strptime(dt_string, "{self.date_pattern}")
                                delta_secs = (dt_now - dt_line).total_seconds()
                                #print("CHECK[" + str(pindex) + "]: " + str(match_counts[pindex]) + "/" + str(total_matches) + " "  + pattern + " " + str(line_count) + ": delta_secs=" + str(delta_secs))
                            except (ValueError, IndexError) as e:
                                pass
                    if skip_time_test == False and \
                       delta_secs > {seconds_past}:
                        match_discard_counts[pindex] += 1
                        #print("DISCARD[" + str(pindex) + "]: " + str(match_counts[pindex]) + "/" + str(total_matches) + " "  + pattern + " " + str(line_count) + ": delta_secs=" + str(delta_secs))
                        continue
                    skip_time_test = True
                    match_counts[pindex] += 1
                    matched=True
                    total_matches += 1
                    matching_files[fn] = True
                    matching_patterns[pattern] = True
                pindex += 1
            if not matched:
                no_match_lines += 1
            else:
                 match_lines += 1
            line_count += 1
            total_lines += 1
        if break_max_lines == True:
           break
pindex = 0
json_out["total_excludes"] = total_excludes
json_out["total_matches"] = total_matches
json_out["total_files"] = len(files)
json_out["total_lines"] = total_lines
json_out["matching_lines"] = match_lines
json_out["not_matching_lines"] = no_match_lines
json_out["matching_files"] = len(matching_files)
json_out["matching_patterns"] = len(matching_patterns)
for pattern in patterns:
    entry=dict()
    entry["pindex"]  = pindex
    entry["pattern"] = pattern
    entry["matches"] = match_counts[pindex]
    entry["discards"] = match_discard_counts[pindex]
    matches.append(entry)
    pindex += 1
json_string = json.dumps(json_out, indent={self.json_indent})
print("{self.json_prefix}" + json_string)\"\"\")'
"""
      command_list = [ command ]
      status = self.run_linux_json(
         local_info,
         router_context,
         node_type,
         command_list,
         error_lines,
         json_data
      )

      return status
