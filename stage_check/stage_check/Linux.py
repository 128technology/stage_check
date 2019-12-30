###############################################################################
#   _     _                  
#  | |   (_)_ __  _   ___  __
#  | |   | | '_ \| | | \ \/ /
#  | |___| | | | | |_| |>  < 
#  |_____|_|_| |_|\__,_/_/\_\
#
# TODO: All classes must return a list of dictonaries which might be the result 
#       of querying one or more router nodes.
#
###############################################################################

try:
    from stage_check import init_helper
except ImportError:
    import init_helper

try:
    from stage_check import RouterContext
except ImportError:
    import RouterContext

import os
import sys
import re
import json
import time
import datetime
import shlex
import subprocess
import pprint
import pytz
import ipaddress


class Callbacks:
   def run_linux_progress(self, message):
       return True

class Base:
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
      self._router_context = None
      self._node_type = None
      self._any_node_command = None
      self._any_node_regex = None
      self._stderr_to_output = False
      self._error_patterns = [];

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

  @property 
  def stderr_to_output(self):
      return self._stderr_to_output

  @stderr_to_output.setter
  def stderr_to_output(self, value):
      if not isinstance(value, bool):
          raise TypeError 
      self._stderr_to_output = value

  @property
  def error_patterns(self):
      return self._error_patterns

  @error_patterns.setter
  def error_patterns(self, value):
      if not isinstance(value, list):
          raise TypeError 
      self._error_patterns = value

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
      if source is None:
          return
      if isinstance(dest, list):
          dest.extend(source)
      elif isinstance(dest, dict):
          dest.update(source)

  def convert_to_json(self):
      return self.json_data

  def _get_shell_command(self, router_context, node_type):
      if self._any_node_command is None:
          raise ValueError
      return self._any_node_command

  def _get_output_regex(self, router_context, node_type):
      return self._any_node_regex

  def _get_display_command(self, router_context, node_type):
      return None

  def run_linux(
      self,
      router_context,
      node_type,
      output_lines,
      error_lines
   ):
      """
      """
      
      error_patterns = self.error_patterns
      error_patterns.append(r'^\s*Minion did not return.')
      error_patterns.append(r'^\s*No minions matched the target.')
      error_patterns.append(r'^\s*/bin/sh:[^:]* command not found')
      error_patterns.append(r'ERROR: Minions returned with non-zero exit code')

      router_context.query_node_info()
      asset_id = router_context.get_node_asset(node_type)

      command = self._get_shell_command(router_context, node_type)
      regex_filter = self._get_output_regex(router_context, node_type)

      output_lines.clear()
      linux_command = ''
      command_list  = []
      if router_context.local_role == 'conductor':
          if  asset_id is None or asset_id == '':
              error_lines.append(f"Missing asset info for {node_type} node")
              return 0 

          if isinstance(command, str):
              linux_command = "t128-salt " + asset_id + " cmd.run " + shlex.quote(command)
              if self.timeout is not None:
                  linux_command += f" timeout={self.timeout}"
          elif isinstance(command, list):
              command_list = ["t128-salt", asset_id, "cmd.run"]
              command_list.extend(command)
              if self.timeout is not None:
                  command_list.append(f"timeout={self.timeout}")
          else:
              return 1
      else:
          if isinstance(command, str):
              linux_command = command
          elif isinstance(command, list):
              command_list = command.copy()
          else:
              return 1
  
      display_command = self._get_display_command(router_context, node_type)
      if len(command_list) == 0:
          command_list = shlex.split(linux_command)
          if display_command is None:
              display_command = linux_command
      else:
          if display_command is None:
              display_command = " ".join(command_list)

      if self.debug:
          if regex_filter is not None:
              print(f'Regex Filter:  {regex_filter}')
          print(f'Linux Command: {linux_command}')
          print(f'Asset ID:      {asset_id}')
          print(f'Command List:  {pprint.pformat(command_list)}')

      # subprocess.DEVNULL is python 3.3+ only
      if self.progobj is not None:
          prog_string = f"Run '{display_command}'..."
          if self.prog_string is not None:
              prog_string = self.prog_string
          self.progobj.run_linux_progress(prog_string)

      try:
          pipe = subprocess.Popen(command_list,
                                  stdin=open(os.devnull, 'rb'),
                                  bufsize=0,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
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
              for pattern in error_patterns:
                  if re.search(pattern, xline):
                      error_lines.append(xline.lstrip())

          if self.stderr_to_output:
              for line in iter(pipe.stderr.readline, b''):
                  bline = line.rstrip()
                  xline = bline.decode('utf-8')
                  output_lines.append(xline)

          if self.debug:
              print("Linux Output List:")
              print("------------------")
              pprint.pprint(output_lines)

          return_code = pipe.poll()

      except FileNotFoundError as e:
          error_lines.append(f"{e.__class__.__name__}: {e}") 
          if self.debug:
              print("Linux Error List:")
              print("------------------")
              pprint.pprint(error_lines)
          return_code = 1

      return return_code

  def _class_mismatch_text(self, class_name):
      message  = "\n"
      message += f"***********************************************************\n"
      message += f"* ERROR:\n"
      message += f"* Argument json_data is type '{class_name}'\n"
      message += f"* {self.__class__.__name__} uses data type {self.json_data.__class__.__name__}\n"
      message += f"***********************************************************\n"
      return message

  def run_linux_json(
      self,
      router_context,
      node_type,
      error_lines,
      json_data
  ):
      """  
      node_type -- 'primary', 'secondary', 'solitary', or the special designator,
                   'all' which matches all router nodes when run from the 
                   conductor.
      """
      class_1 = json_data.__class__.__name__
      class_2 = self.json_data.__class__.__name__
      assert class_1 == class_2, self._class_mismatch_text(class_1)

      shell_status = 0
      json_data.clear()

      node_type_list = []
      if node_type == 'all':
          if router_context.from_conductor:
              node_type_list = router_context.get_node_types()
          else:
              local_node_type = router_context.local_node_type
              # use whatever this current node's type is...
              if local_node_type is not None:
                  node_type_list.append(local_node_type)
      else:
          node_type_list.append(node_type)

      self._router_context = router_context
      for cur_type in node_type_list:
          output_lines = []
          self._node_type = cur_type
          start_count  = len(error_lines)
          shell_status = self.run_linux(
              router_context,
              cur_type,
              output_lines,
              error_lines
          )

          #assert False, "********* Base.run_linux_json **********\n" + pprint.pformat(output_lines)

          if len(error_lines) == start_count:
              jdata = self.convert_to_json(output_lines)
              #assert False, "********* Base.run_linux_json (jdata) **********\n" + pprint.pformat(jdata)
              if isinstance(jdata, dict):
                  jdata['node_type'] = cur_type
                  jdata['shell_status'] = shell_status
              elif isinstance(jdata, list) and \
                   len(jdata) == 1 and \
                   isinstance(jdata[0], dict):
                  # node type 'all' is expected to return a list of entries usually
                  # (but not always) this is one per node... 
                  jdata[0]['node_type'] = cur_type
                  jdata[0]['shell_status'] = shell_status
              else:
                  if self.debug:
                      print(f"********** WARNING Cannot add node_type to {jdata.__class__.__name__} **************")
              if node_type == 'all' and \
                  isinstance(json_data, list):
                     if isinstance(jdata, dict):
                         json_data.append(jdata)
                     else:
                         json_data.extend(jdata)
              else:
                  # json_data is a list
                  self.update_by_type(json_data, jdata)
          
      # assert False, "********* Base.run_linux_json (error_lines) **********\n" + pprint.pformat(error_lines)
                
      self.json_data = json_data
      #assert False, "********* Base.run_linux_json **********\n" + pprint.pformat(json_data)
      #assert False, pprint.pformat(self.json_data)
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

  def _update_entry_info(self, entry : dict):
      """
      Add current node_type, node_name to the current entry
      """
      if self._node_type is not None:
          entry['node_type'] = self._node_type
          if self._router_context is not None:
              node_name = self._router_context.get_node_name(self._node_type)
              entry['node_name'] = node_name


class Ethtool(Base):
  """
  """
  def __init__(self, devmap=None, debug=False, progobj=None):
      super().__init__(debug=debug, progobj=progobj)
      self.__cur_intf = ''
      if not isinstance(devmap, dict):
           raise TypeError
      if len(devmap) == 0 or \
         not 'default' in devmap:
           raise ValueError
      self.__hw_dev_map = devmap
      # for testing only, in real scenarios this will be 
      # overwritten by _get_shell_command()
      if "__test__" in self.__hw_dev_map:
          self.__cur_intf = self.__hw_dev_map["__test__"]

  def _get_shell_command(self, router_context, node_type):
      hw_type = router_context.get_node_hw_type(node_type)
      if hw_type in self.__hw_dev_map:
          intf = self.__hw_dev_map[hw_type]
      else:
          intf = self.__hw_dev_map['default']
      self.__cur_intf = intf
      return f"ethtool {intf}"

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
      router_context,
      node_type,
      error_lines,
      json_data
    ):
      """
      Get json output for ethtool command:

      *router_context* - Target router
      *node_type*      - Which node
      *intf*           - Linux interface / device name
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      status = self.run_linux_json(
        router_context,
        node_type,
        error_lines,
        json_data
       )
      json_data["linux_device"] = self.__cur_intf
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
      router_context,
      node_type,
      error_lines,
      json_data
    ):
      """
      Get json output for "coedumpctl list" command:

      *router_context* - Target router
      *node_type*      - Which node
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      self._any_node_command = f"coredumpctl list"
      status = self.run_linux_json(
        router_context,
        node_type,
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

  def clear_json(self):
      self.json_data = []

  def new_entry(self, service):
      entry = dict()
      entry["service"] = service
      entry["Main_PID"] = "0"
      entry["Main_Process"] = "NotFound"
      entry["epoch_time"] = 0.0
      entry["state_1"] = "missing"
      entry["state_2"] = "missing"
      entry["time"] = "Wed 0000-00-00 00:00:00 EDT"
      entry["uptime_days"] = 0
      entry["uptime_hours"] = 0
      entry["uptime_minutes"] = 0
      entry["uptime_seconds"] = 0
      entry["Tasks"] = 0
      entry["Memory"] = float(0)
      entry["MemoryModifier"] = "GB"
      return entry

  def convert_to_json(
         self,
         text_lines
      ):
      start_line_regex=r"^.*?([A-Za-z0-9_@-]+)\.service -"
      # Unit fubar.service could not be found.
      error_line_regex=r"^\s*Unit (.*?)\.service could not be found"
      self.clear_json()
      index = 0
      service_name = None
      entry = dict()
      for line in text_lines:
          if self.debug:
              print(f"{index}: {line}")
          matches = re.match(start_line_regex, line)
          if matches is None:
              matches = re.match(error_line_regex, line)
          if matches is not None:
              try:
                  service_name = matches.group(1)
                  if len(entry) > 1:
                      self.json_data.append(entry)
                  entry = self.new_entry(service_name)
              except IndexError:
                  assert False, "Start Line Index Error.."
                  continue
          matches = re.match(r'\s+Active:\s+(\w+)\s+\((\w+)\)\s+since\s+([^;]+)', line)
          if matches is not None:
              try:
                  entry["state_1"] = matches.group(1)
                  entry["state_2"] = matches.group(2)
                  entry["time"] = matches.group(3)
                  dt_start = self.normalize_datetime(entry["time"])
                  dt_epoch = datetime.datetime(1970,1,1)
                  dt_epoch = dt_epoch.replace(tzinfo=pytz.UTC)
                  epoch_secs = (dt_start - dt_epoch).total_seconds()
                  entry["epoch_time"] = epoch_secs
                  dt_now = datetime.datetime.now(datetime.timezone.utc)
                  delta_secs = (dt_now - dt_start).total_seconds()
                  if self.debug:
                      print(f"dt_epoch: {dt_epoch}")
                      print(f"dt_start: {dt_start}")
                      print(f"dt_now:   {dt_now}")
                  entry["uptime_days"] = int(delta_secs / self.SECONDS_PER_DAY)
                  delta_secs = int(delta_secs % self.SECONDS_PER_DAY)
                  if self.debug:
                      print(f"SystemctlStatus: days: {entry['uptime_days']} remsecs: {delta_secs}")
                  entry["uptime_hours"] = int(delta_secs / self.SECONDS_PER_HOUR)
                  delta_secs = int(delta_secs % self.SECONDS_PER_HOUR)
                  if self.debug:
                      print(f"SystemctlStatus: hours: {entry['uptime_hours']} remsecs: {delta_secs}")
                  entry["uptime_minutes"] = int(delta_secs / self.SECONDS_PER_MINUTE)
                  delta_secs = int(delta_secs % self.SECONDS_PER_MINUTE)
                  if self.debug:
                      print(f"SystemctlStatus: minutes: {entry['uptime_minutes']} remsecs: {delta_secs}")
                  entry["uptime_seconds"] = delta_secs
                  #assert False, f"entry[1]: {entry}"
              except IndexError:
                  assert False, "Line 1 Index Error.."
                  continue
          matches = re.match(r'\s+Main PID:\s+(\d+)\s+\(([^\)]+)', line)
          if matches is not None:
              try:
                  entry["Main_PID"] = matches.group(1)
                  entry["Main_Process"] = matches.group(2)
                  #assert False, f"entry[2]: {entry}"
              except IndexError:
                  assert False, "Line 2 Index Error.."
                  continue
          matches = re.match(r'\s+Tasks:\s+(\d+)$', line)
          if matches is not None:
              try:
                  entry["Tasks"] = int(matches.group(1))
              except (IndexError, ValueError) as e:
                  continue
          matches = re.match(r'\s+Memory:\s+([0-9\.]+)([MGK])$', line)
          if matches is not None:
              try:
                  entry["Memory"] = float(matches.group(1))
                  entry["MemoryModifier"] = matches.group(2) + "B"
              except (IndexError, ValueError) as e:
                  continue
          index += 1
      if len(entry) > 1:
          self.json_data.append(entry)
          # assert False, f"post: {entry}"
      return self.json_data

  def run_linux_args(
      self,
      router_context,
      node_type,
      services,
      error_lines,
      json_data
    ):
      """
      Get json output for ethtool command:

      *router_context* - Target router
      *node_type*      - Which node
      *service*        - Systemd service to query
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      self._any_node_command = f"systemctl status"
      for service in services:
          self._any_node_command = self._any_node_command + f" {service}"

      status = self.run_linux_json(
        router_context,
        node_type,
        error_lines,
        json_data
       )
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
      router_context,
      node_type,
      error_lines,
      json_data
    ):
      """
      Get json output for ethtool command:

      *router_context* - Target router
      *node_type*      - Which node
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      self._any_node_command = f"uptime"
      status = self.run_linux_json(
        router_context,
        node_type,
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
      router_context,
      node_type,
      error_lines,
      json_data
    ):
      """
      Get json output for 'show ip bgp summary' vtysh command

      *router_context* - Target router
      *node_type*      - Which node
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      self._any_node_command = 'vtysh -c "show ip bgp summary"'
      status = self.run_linux_json(
        router_context,
        node_type,
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
      router_context,
      node_type,
      namespace,
      error_lines,
      json_data
    ):
      """
      Get json output for 'show ip bgp summary' vtysh command

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
      self._any_node_command = command

      status = self.run_linux_json(
        router_context,
        node_type,
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
  """
  TODO: Relocate convert_to_json_base() to T1Details and deprecate
  """
  def __init__(self, debug=False, progobj=None):
      super().__init__(debug=debug, progobj=progobj)

  def clear_json(self):
      self.json_data = [ ]

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

      #assert False, "T1Detail text: " + pprint.pformat(text_list)

      count=0
      self.clear_json()
      dev_entry = {}
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
                          if key in dev_entry:
                              key = 'Tx' + key
                          value_index = item["value"]
                          if self.debug:
                              print(f"json_data[{key}] = {matches.group(value_index)}")
                          dev_entry[key] = matches.group(value_index)
                      except (KeyError, ValueError, IndexError) as e:
                          if self.debug:
                              print(f"EXCEPTION: {e}")
                          pass
                  break
              else:
                  if self.debug:
                      print(f"Mismatch {entry['pattern']}")

      #assert False, pprint.pformat(dev_entry)
      self.json_data = [ dev_entry ]
      return self.json_data

  def _build_command(self, namespace, linux_device):
      if namespace is None or \
         namespace == '':
          command = "ip address"
      else:
          command = f"netns exec {namespace} ip address"

      command = 'ip netns exec ' + namespace + ' wanpipemon -i ' + linux_device + ' -c Ta'
      return command

  def get_device_command(self, router_context, node_type):
      """
      For display only, to be invoked only after run_linux_args is invoked 
      Revisit at a later date...
      """
      return self._any_node_command
 
  def run_linux_args(
      self,
      router_context,
      node_type,
      namespace,
      linux_device,
      error_lines,
      json_data
    ):
      """
      Get json output for 'show ip bgp summary' vtysh command

      *router_context* - Target router
      *node_type*      - Which node
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      self._any_node_command = self._build_command(namespace, linux_device)

      status = self.run_linux_json(
        router_context,
        node_type,
        error_lines,
        json_data
       )

      # update both the class cache and the caller's json data
      if namespace is not None and \
         namespace != '' and \
         len(self.json_data) == 1:
              self.json_data[0]["namespace"] = namespace
              json_data[0]["namespace"] = namespace
      if linux_device is not None and \
         linux_device != '' and \
         len(self.json_data) == 1: 
              self.json_data[0]["linux_device"] = linux_device
              json_data[0]["linux_device"] = linux_device

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
      self._any_node_command = [ command ]

      status = self.run_linux_json(
         router_context,
         node_type,
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
      self._any_node_command = [ command ]
      status = self.run_linux_json(
         router_context,
         node_type,
         error_lines,
         json_data
      )

      return status


class HostsFile(Base):
    """
    Locally or remotely execute 'cat /etc/hosts' and convert the
    output into a json dictionary for hostname -> ip address
    lookup

    Input is a typical /etc/hosts file from one or two 128T nodes:
    ----- cut here ----
    127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
    ::1         localhost localhost.localdomain localhost6 localhost6.localdomain6                                                                                                                                                                                   
    # BEGIN ANSIBLE MANAGED BLOCK
    1.2.3.4     Fubar
    # END ANSIBLE MANAGED BLOCK
    ----- cut here ------

    Python result is of the form (in the case of 2 nodes):
    [
       {
           node_name:  node_1
           node_type:  primary
           host_name_1 : [ ip1, ... , ipN ],
           host_name_2 : [ ip1, ... , ipN ],
           :
           :
           host_name_N : [ ip1, ... , ipN ]
       },
       {
           node_name:  node_2
           node_type:  secondary
           host_name_1 : [ ip1, ... , ipN ],
           host_name_2 : [ ip1, ... , ipN ],
           :
           :
           host_name_N : [ ip1, ... , ipN ]
       }
    ]
    """
    def __init__(self, debug=False, progobj=None):
        super().__init__(debug=debug, progobj=progobj)
        self._node_type_map  = {}

    def clear_json(self):
        self.json_data = []

    def _get_shell_command(self, router_context, node_type):
        command = 'cat /etc/hosts'
        return command

    def convert_to_json(self, text_list):
        """
        """
        hosts_file = {}
        for line in text_list:
            line = line.rstrip()
            fields = line.split()
            try:
                if len(fields) < 2:
                    continue
                ipa = ipaddress.ip_address(fields[0])
                index = 1
                while index < len(fields):
                    if not fields[index] in hosts_file:
                        hosts_file[fields[index]] = []
                    hosts_file[fields[index]].append(fields[0])
                    index += 1
            except (IndexError, ValueError) as e:
                continue

        self._update_entry_info(hosts_file)
        if self._node_type is not None:
            self._node_type_map[self._node_type] = hosts_file   

        # Required for unit tests to work, overwritten by run_linux_json...
        self.json_data.extend([ hosts_file ])

        # required to merge content correctly...
        return [ hosts_file ] 
                        
    def run_linux_args(
        self,
        router_context,
        node_type,
        error_lines,
        json_data
     ):
        status = self.run_linux_json(
            router_context,
            node_type,
            error_lines,
            json_data
        )

        #assert False, pprint.pformat(json_data)
        return status

    def get_list_entry(self, index=0, node_type=None):
        """
        """
        try:
            if node_type is None:
                return self.json_data[index]
            else:
                return self._node_type_map[node_type]
        except IndexError:
            pass
        return None

    def lookup_host(self, name:str, index=0, node_type=None):
        """
        """
        address_list = None
        try:
            host_entry = self.get_list_entry(index, node_type)
            if host_entry is not None:
                address_list = host_entry[name]
        except KeyError:
            address_list = None
        return address_list 

    def get_ipv4_address(self, name:str, index=0, node_type=None):
        entry = None
        address_list = self.lookup_host(name, index, node_type)
        if address_list is not None:
            for entry in address_list:
                try:
                    ipv4 = ipaddress.IPv4Address(entry)
                    break
                except ValueError:
                    continue
        return entry

    def get_ipv6_address(self, name:str, index=0, node_type=None):
        entry = None
        address_list = self.lookup_host(name, index, node_type)
        if address_list is not None:
            for entry in address_list:
                try:
                    ipv6 = ipaddress.IPv6Address(entry)
                    break
                except ValueError:
                    continue
        return entry

    def get_first_address(self, name:str, index=0, node_type=None):
        address_list = self.lookup_host(name, index, node_type)
        if address_list is not None:
            return address_list[0]
        return None   

    def to_string(self):
        return pprint.pformat(self.json_data)

    def dump(self):
        pprint.pprint("............")
        pprint.pprint(self.json_data)
        pprint.pprint("............")

class LteInfo(Base):
    """
    lte-state script Should not be used with 128T version > 4.3.9
    """
    def __init__(self, debug=False, progobj=None):
        super().__init__(debug=debug, progobj=progobj)
        self._namespace = None
        self._device = None
        self._script = "lte-state"
        self.json_indent = None
        self.json_prefix = "JSON:"

    def _get_shell_command(self, router_context, node_type):
        command = f"ip netns exec {self._namespace} {self._script} {self._device}"
        return command

    def _fix_json_field_names(self, json_data):
        if isinstance(json_data, dict):
            keys_to_delete=[]
            new_dict={}
            for key in json_data:
                fixed_key = key.replace(' ', '_')
                if fixed_key != key:
                    new_dict[fixed_key] = json_data[key]
                    keys_to_delete.append(key)
            for key in json_data:
                self._fix_json_field_names(json_data[key])
            for key in keys_to_delete:
                del json_data[key]
            for key in new_dict:
                json_data[key] = new_dict[key]
        elif isinstance(json_data, list):
            for entry in json_data:
                self.fix_json_field_names[entry]
 
    def _remove_json_value_units(self, json_data):
        key_list = [
            "RSSI_Signal_Strength",
            "SNR_Signal_Strength"
        ]
        for key in key_list:
            try:
                matches = re.search(r"^([-]?[0-9]+(?:\.[0-9]+)?)\s+", json_data[key])
                if matches is not None:
                    value_string = matches.group(1)
                    float_value = float(value_string)
                    json_data[key] = float_value
                else:
                    assert False, f"{key} -- failed to match against {json_data[key]}"
            except (IndexError, TypeError, ValueError, KeyError) as e:
                continue
                              

    def convert_to_json(self, text_list):
        self.clear_json()
        big_string=""
        for line in text_list:
            big_string += line
        self.json_data = json.loads(big_string)
        self.json_data = self.json_data["LTE"]
        # assert False, pprint.pformat(self.json_data)
        self._fix_json_field_names(self.json_data)
        self._remove_json_value_units(self.json_data)
        return self.json_data
                        
    def run_linux_args(
        self,
        router_context : RouterContext.Base,
        node_type : str,
        script : str,
        namespace : str,
        device  : str,
        error_lines : list,
        json_data
     ):
      
        self._script = script
        self._namespace = namespace
        self._device = device

        status = self.run_linux_json(
            router_context,
            node_type,
            error_lines,
            json_data
        )

        return status

    def to_string(self):
        return pprint.pformat(self.json_data)


class NetNsCommand(Base):
    """
    namespace = "(t1-ns-[0-9]+) "
    device = "^[0-9]+: (w1.*?[0-9]+):"
 
    On the local or remote system:
    - execute ip netns list
    - for each matching namespace, execute ip netns exec namespace ip address
    -    for each matchineg device:
    -        execute wanpipemon -i device -c Ta
    - Package it all up into a nice json list of T1 details per matching
      namespace / device
    """

    MESSAGE_LIST_KEY = "stage_check_messages"

    def __init__(self, debug=False, progobj=None):
        super().__init__(debug=debug, progobj=progobj)
        self._namespace_regex = None
        self._device_regex = None
        self.json_indent = None
        self.json_prefix = "JSON:"

    def _get_display_command(self, router_context, node_type):
        return "ip netns exec <namespace> " + self._get_display_suffix()

    def _get_display_suffix(self):
        return "ip show <device>"

    def _get_namespace_command(self):
        """
        Return a string which is appended to 
        linux_command = ip netns exec <namespace> + <this-string>
        Example:
            '"wanpipemon -i " + dev + " -c Ta"'
        Where dev is the linux device name...

        The variable dev is available to work with.  The returned string 
        is executed as part of a command-line python script -- and dev is not 
        available when this method is invoked (dev is not passed to this 
        method, instead dev is determined when the returned string is
        evaluated by the python interpeter on the router.
        """
        assert False, "*** NetNsCommand::_get_namespace_command(): Must be Overriden ***"
        return '"ip address show " + dev'

    def get_device_command(self, router_context, node_type):
        """
        The default command executed by this class is:
        linux_command = ip netns exec <namespace> + self._get_namespace_command()

        Recent events have made it necessary to seek state information outside of
        the ip netns exec framework.  To this end, a subclass may now define the entire
        command.

        Two variables: 'ns', and 'dev' are available to work with (as determined by the
        command-line python script returned by self._get_shell_command()).  The returned
        string is executed as part of the command-line python script -- and for this
        reason ns and dev are not actually variables in the context of this method but
        instead just tokens in a python string.

        router_context:  Router state  
        node_type:       Abstract identifier for a specific router node

        Returns:         A command string to be executed by the command line python
                         script returned by self.get_shell_command().  
        """
        netns_command_suffix = self._get_namespace_command() 
        linux_command = f'"ip netns exec " + ns + " " + {netns_command_suffix}'
        return linux_command

    def _get_shell_command(
        self,
        router_context,
        node_type
    ):
        device_regex = "^[0-9]+: (" + self._device_regex + "):"
        namespace_regex = "^(" + self._namespace_regex + ") "
        
        status_command = self.get_device_command(router_context, node_type)
        command = f"""python3.6 -c 'exec(\"\"\"import os, subprocess, shlex, re, json
ns_regex = "{namespace_regex}"
dev_regex = "{device_regex}"
ns_list = []
linux_command = "ip netns list"
command_list = shlex.split(linux_command)
pipe = subprocess.Popen(command_list,
                        stdin=open(os.devnull, "rb"),
                        bufsize=0,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        close_fds=True)
for line in iter(pipe.stdout.readline, b""):
    if {self.debug}:
        print(line)
    bline = line.rstrip()
    xline = bline.decode("utf-8")
    matches = re.search(ns_regex, xline)
    if matches is not None:
        try:
            ns_list.append(matches.group(1))
        except IndexError:
            pass
entry_list = []
command_list = shlex.split(linux_command)
for ns in ns_list:
    linux_command = "ip netns exec " + ns + " ip a" 
    command_list = shlex.split(linux_command)
    pipe = subprocess.Popen(command_list,
                            stdin=open(os.devnull, "rb"),
                            bufsize=0,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            close_fds=True)
    for line in iter(pipe.stdout.readline, b""):
        if {self.debug}:
            print(line)
        bline = line.rstrip()
        xline = bline.decode("utf-8")
        dev_matches = re.search(dev_regex, xline)
        if dev_matches is not None:
            try:
                dev = dev_matches.group(1)
                linux_command = {status_command}
                if {self.debug}:
                    print(ns + "/" + dev + ": run " + linux_command)
                command_list = shlex.split(linux_command)
                pipe2 = subprocess.Popen(command_list,
                                        stdin=open(os.devnull, "rb"),
                                        bufsize=0,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL,
                                        close_fds=True)
                strdata = ""
                for ipline in iter(pipe2.stdout.readline, b""):
                    xline = ipline.decode("utf-8")
                    strdata += xline
                entry = dict()
                entry["namespace"] = ns
                entry["device"]    = dev
                entry["output"]    = strdata
                entry_list.append(entry.copy())
            except IndexError:
                pass
json_string = json.dumps(entry_list, indent={self.json_indent})
print("{self.json_prefix}" + json_string)\"\"\")'
"""
        return command 

    def _device_output_to_json(self, dev_entry):
        """
        Override this to return a dictionary with data from the output
        of 'ip netns exec <namespace>' command against a single device
        """
        assert False, "Override NetNsCommand._device_output_to_json() !!!"

    def convert_to_json(self, text_list): 
        json_regex  = r"\s*" + self.json_prefix + r"\s*(.*)"
        aggregate_data = []
        for line in text_list:
            matches = re.search(json_regex, line)
            try:
                if matches is not None:
                    json_string = matches.group(1)
                    json_details = json.loads(json_string)
                    assert isinstance(json_details, list), "json_details is type " + \
                        json_details.__class__.__name__ + ":\n" + pprint.pformat(json_details)
                    for dev_entry in json_details:
                        #assert False, pprint.pformat(json_details)
                        dev_dict = self._device_output_to_json(
                            dev_entry
                        )
                        if 'namespace' in dev_entry:
                            dev_dict['namespace'] = dev_entry['namespace']
                        if 'device' in dev_entry:
                            dev_dict['linux_device'] = dev_entry['device']
                        #assert False, pprint.pformat(dev_dict)
                        aggregate_data.append(dev_dict.copy())
            except IndexError:
                continue
        self.json_data = aggregate_data
        return aggregate_data    

    def clear_json(self):
        self.json_data = []  


class LteInfos(NetNsCommand):
    """
    namespace = "(lte-ns-[0-9]+) "
    device = "^[0-9]+: (wwp.*?[0-9]+):"
 
    On the local or remote system:
    - execute ip netns list
    - for each matching namespace, execute ip netns exec namespace ip address
    -    for each matching device:
    -        execute lte-state  device
    - Package it all up into a nice json list of lte info per matching
      namespace / device
    """
    def __init__(self, debug=False, progobj=None):
        super().__init__(debug=debug, progobj=progobj)

    def _get_namespace_command(self):
        """
        This creates the command:
        ip netns exec <namespace> lte-state <device>
        """
        return '"lte-state " + dev'  

    def _get_display_suffix(self):
        return "lte-state <device>"

    def _fix_json_field_names(self, dev_entry, json_data):
        """
        The output of lte-state includes spaces in the json/dictionary keys
        which are incompatible with the stage_check test expression parser
        All spaces in keys are replaced with '_'s
        """
        if isinstance(json_data, dict):
            keys_to_delete=[]
            new_dict={}
            for key in json_data:
                fixed_key = key.replace(' ', '_')
                if fixed_key != key:
                    new_dict[fixed_key] = json_data[key]
                    keys_to_delete.append(key)
            for key in json_data:
                self._fix_json_field_names(dev_entry, json_data[key])
            for key in keys_to_delete:
                del json_data[key]
            for key in new_dict:
                json_data[key] = new_dict[key]
        elif isinstance(json_data, list):
            for entry in json_data:
                self._fix_json_field_names(dev_entry, entry)
 
    def _remove_json_value_units(self, dev_entry, json_data):
        """
        Some numeric fields are expressed as string because there is a
        unit type appended to the value.  This method extracts the number
        only and converts it to a float. 
        """
        key_list = [
            "RSSI_Signal_Strength",
            "SNR_Signal_Strength"
        ]
        namespace="missing"
        device="missing"
        if 'namespace' in dev_entry:
            namespace = dev_entry['namespace']
        if 'device' in dev_entry:
            device = dev_entry['device']
        for key in key_list:
            try:
                matches = re.search(r"^([-]?[0-9]+(?:\.[0-9]+)?)\s+", json_data[key])
                if matches is not None:
                    value_string = matches.group(1)
                    float_value = float(value_string)
                    json_data[key] = float_value
                else:
                    # What to do here... this can be an error string or a value...
                    # For now, remove this key, this will cause an field value
                    # exception error for any tests using it...
                    # assert False, f"{key} -- failed to match value='{json_data[key]}'"
                    del json_data[key]
                    if not self.MESSAGE_LIST_KEY in json_data:
                        json_data[self.MESSAGE_LIST_KEY] = []
                    message = f"{namespace}/{device}/{key}: Error Obtaining Data"
                    json_data[self.MESSAGE_LIST_KEY].append(message)
            except (IndexError, TypeError, ValueError, KeyError) as e:
                continue
      
    def _device_output_to_json(self, dev_entry):
        """
        Overrides parent method to parse the output from a single
        device interface...
        """
        json_data = {}
        try:
            json_data = json.loads(dev_entry["output"])
            json_data = json_data["LTE"]
        except Exception as e:
            if self.debug:
                print(f"LteInfos._device_output_to_json: {e}, {e.__class__.__name__}")
            return json_data
        self._fix_json_field_names(dev_entry, json_data)
        self._remove_json_value_units(dev_entry, json_data)
        self._update_entry_info(json_data)
        return json_data

    def run_linux_args(
        self,
        router_context,
        node_type,
        namespace_regex,
        device_regex,
        error_lines,
        json_data
     ):

        self._namespace_regex = namespace_regex
        self._device_regex = device_regex

        status = self.run_linux_json(
            router_context,
            node_type,
            error_lines,
            json_data
        )

        # assert False, "********** LteInfos.run_linux_args **********\n " + pprint.pformat(json_data)

        return status

class LteFiles(LteInfos):
    """
    namespace = "(lte-ns-[0-9]+) "
    device = "^[0-9]+: (wwp.*?[0-9]+):"
 
    On the local or remote system:
    - execute ip netns list
    - for each matching namespace, execute ip netns exec namespace ip address
    -    for each matching device:
    -        execute "cat /var/run/128technology/lte/<device>.state"
    - Package it all up into a nice json list of lte info per matching
      namespace / device
    """
    def __init__(self, debug=False, progobj=None):
        super().__init__(debug=debug, progobj=progobj)

    def _get_display_command(self, router_context, node_type):
        return "cat /var/run/128technology/lte/<device>.state"

    def get_device_command(self, router_context, node_type):
        """
        Two variables ns, and dev are available to work with.  The returned
        string is executed as part of a command-line python script -- and
        ns and dev are not available when this method is invoked. 
        """
        return '"cat /var/run/128technology/lte/" + dev + ".state"'  

class LteStatus(LteFiles):
    """
    Implements Linux LTE status command which is sensitive to the 128T version of 
    the node which it is executed against.
    """
    VERSION_128T_FILE_API = "4.3.9"

    def __init__(self, debug=False, progobj=None):
        super().__init__(debug=debug, progobj=progobj)

    def _get_display_command(self, router_context, node_type):
        if router_context.compare_node_rpm_version(node_type, self.VERSION_128T_FILE_API) < 0:
            command =  LteInfos.get_device_command(self, router_context, node_type)
        else:
            command =  LteFiles.get_device_command(self, router_context, node_type)
        return command

    def get_device_command(self, router_context, node_type):
        fname = f"{self.__class__.__name__}.get_device_name"
        rpm_version = router_context.get_node_rpm_version(node_type)
        if router_context.compare_node_rpm_version(node_type, self.VERSION_128T_FILE_API) < 0:
            command =  LteInfos.get_device_command(self, router_context, node_type)
            if self.debug:
                print(f"{fname}: version={rpm_version} => Use LteInfos")
        else:
            command =  LteFiles.get_device_command(self, router_context, node_type)
            if self.debug:
                print(f"{fname}: version={rpm_version} => Use LteFiles")
        return command
 

class T1Details(NetNsCommand,T1Detail):
    r"""
    namespace = "(t1-ns-[0-9]+) "
    device = "^[0-9]+: (w1.*?[0-9]+):"
 
    On the local or remote system:
    - execute ip netns list
    - for each matching namespace, execute ip netns exec namespace ip address
    -    for each matchineg device:
    -        execute wanpipemon -i device -c Ta
    - Package it all up into a nice json list of T1 details per matching
      namespace / device
  
    This must inherit first from NetMsCommand and then T1Detail as when 
    convert_to_json() is invoked, the first class in the:
                 Base
               /      \
      NetNsCommand  T1Detail
               \      /
               T1Details
    diamond is used to override Base.convert_to_json.
    """
    def __init__(self,  debug=False, progobj=None):
        super().__init__(debug=debug, progobj=progobj)

    def _get_namespace_command(self):
        """
        This creates the command:
        ip netns exec <namespace> lte-state <device>
        """
        return '"wanpipemon -i " + dev + " -c Ta"'  

    def _get_display_suffix(self):
        return "wanpipemon <device>"

    def _get_display_command(self, router_context, node_type):
        return "ip netns exec <t1-namespace> wanpipemon <device>"

    def _device_output_to_json(self, dev_entry): 
        #assert False, "*******\n " + pprint.pformat(dev_entry)
        text_blob = dev_entry["output"]
        text_lines = text_blob.splitlines()
        # diamond hierarchy complicates use of super()
        json_list = T1Detail.convert_to_json(self, text_lines)
        # There should be only list entry
        json_data = json_list.pop()
        self._update_entry_info(json_data)
        return json_data

    def run_linux_args(
        self,
        router_context,
        node_type,
        namespace_regex,
        device_regex,
        error_lines,
        json_data
     ):

        self._namespace_regex = namespace_regex
        self._device_regex = device_regex

        status = self.run_linux_json(
            router_context,
            node_type,
            error_lines,
            json_data
        )

        return status


class LSHW(Base):
  """
  This class is currently used ofr infomation gathering and not
  as part of a test.  As such the json results are a list of
  flattened dictionaries.  They are exactly what lshw -json -s <system>
  returns...
  """ 
  def __init__(self, debug=False, progobj=None, class_type="system"):
      super().__init__(debug=debug, progobj=None)

  def clear_json(self):
      self.json_data = []

  def convert_to_json(
         self,
         text_lines
      ):
      """
      One of the few Linux commands that output in json. Output is a
      single dictionary
      """
      json_lines = []
      # strip non-json lines like the salt heading...
      for line in text_lines:
          if re.search(r"^\s*[\{\]].*", line) or \
             len(json_lines) > 0:
              json_lines.append(line)        
      # eliminate extra kruft after closing } on last line
      json_lines[-1] = re.sub(r"}.*", r"}", json_lines[-1])
      json_string='\n'.join(json_lines)
      # eliminate , after last item in a list
      json_string = re.sub(r"},(\s*\n\s*\])", r"}\1",json_string)
      json_data = json.loads(json_string)
      #pprint.pprint(json_data) 
      #self.json_data = json_data 
      return json_data

  def run_linux_args(
      self,
      router_context,
      node_type,
      class_type,
      error_lines,
      json_data
    ):
      """
      Get json output for ethtool command:

      *router_context* - Target router
      *node_type*      - Which node
      *service*        - Systemd service to query
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      self._any_node_command = f"lshw -json -class " + class_type

      status = self.run_linux_json(
        router_context,
        node_type,
        error_lines,
        json_data
       )
      return status

class NetNsIfConfig(NetNsCommand):
    """
    namespace = "(lte-ns-[0-9]+) "
    device = "^[0-9]+: (wwp.*?[0-9]+):"
 
    On the local or remote system:
    - execute ip netns list
    - for each matching namespace, execute ip netns exec namespace ip address
    -    for each matching device:
    -        execute ifconfig  device
    - Package it all up into a nice json list of ifconfig data for each
      namespace / device
    """
    def __init__(self, debug=False, progobj=None):
        super().__init__(debug=debug, progobj=progobj)

    def clear_json(self):
        self.json_data = [ ]

    def is_full_json(self):
        return True

    def _get_namespace_command(self):
        """
        This creates the command:
        ip netns exec <namespace> ifconfig <device>
        """
        return '"ifconfig " + dev'  

    def _get_display_suffix(self):
        return "ifconfig <device>"

    def _device_output_to_json(self, dev_entry):
        text_blob  = dev_entry["output"]
        text_lines = text_blob.splitlines()
        json_list  = self.convert_entry_to_json(text_lines)
        # There should be only list entry                                                                                                                                   
        json_data = json_list.pop()
        self._update_entry_info(json_data)
        return json_data

    def convert_entry_to_json(self, text_lines):
        """
        Overrides parent method to parse the output from a single
        device interface...

        wwp0s21u1i8: flags=4305<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>  mtu 9000
        inet 10.96.52.186  netmask 255.255.255.252  destination 10.96.52.186
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 1000  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 13  bytes 624 (624.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        """
        json_data = {}
        match_rules = [ 
          { 
              "regex" : r"RX packets ([0-9]+)\s+bytes ([0-9]+)", 
              "fields" : [ "RX_packets", "RX_bytes" ]
          },
          { 
              "regex" : r"RX errors ([0-9]+)\s+dropped ([0-9]+)\s+overruns ([0-9]+)\s+frame ([0-9]+)", 
              "fields" : [  "RX_errors", "RX_dropped", "RX_overruns", "RX_frame" ]
          }, 
          {
              "regex" : r"TX packets ([0-9]+)\s+bytes ([0-9]+)", 
              "fields" : [ "TX_packets", "TX_bytes"  ]
          },
          { 
              "regex" : r"TX errors ([0-9]+)\s+dropped ([0-9]+)\s+overruns ([0-9]+)\s+carrier ([0-9]+)\s+collisions ([0-9])+", 
              "fields" : [ "TX_errors", "TX_dropped", "TX_overruns", "TX_carrier", "TX_collisions" ]
          }
        ]

        for line in text_lines:
           for rule in match_rules:
               matches = re.search(rule["regex"], line);
               if matches is not None:
                  group_index = 1
                  for field in rule["fields"]:
                      json_data[field] = int(matches.group(group_index))
                      group_index += 1
                  break              
        self._update_entry_info(json_data)
        return [ json_data ]

    def run_linux_args(
        self,
        router_context,
        node_type,
        namespace_regex,
        device_regex,
        error_lines,
        json_data
     ):

        self._namespace_regex = namespace_regex
        self._device_regex = device_regex

        status = self.run_linux_json(
            router_context,
            node_type,
            error_lines,
            json_data
        )

        # assert False, "********** NetNsIfConfig.run_linux_args **********\n " + pprint.pformat(json_data)

        return status


class IPSecStatus(Base):
  """
  """
  def __init__(self, debug=False, progobj=None):
      """
      Python's Subprocess command seems to thwart 2>&1. to give
      individual Linux commands control over pipe content, 
      the stderr_to_output flag can be set. This just appends
      the stderr pipe content to the output list, but this
      is sufficient for scrapers looking for lines to match.
      """
      super().__init__(debug=debug, progobj=progobj)
      self.stderr_to_output = True

  def _get_shell_command(self, router_context, node_type):
      return f"ipsec status"

  def clear_json(self):
      self.json_data = []

  def convert_to_json(
         self,
         text_lines
      ):
      """
      For now, jsut scan for connection data...
      """
      match_rules = [
          {
             "regex"  : r'.*?(whack: Pluto is not running \(no "/run/pluto/pluto.ctl"\).*?)',
             "fields" : [ "list:errors" ]
          },
          {
             "regex"  : r".*?Total IPsec connections: loaded ([0-9]+), active ([0-9]+)",
             "fields" : [ "int:loaded", "int:active" ]
          }
      ] 
      self.clear_json()
      json_data = {
          "loaded" : 0,
          "active" : 0,
          "errors" : []
      }
      mc = 0
      for line in text_lines:
          for match in match_rules:
              matches = re.search(match["regex"], line)
              if matches is not None:
                  try:
                      group_index = 1
                      for field in match["fields"]:
                          fdata = field.split(":")
                          ftype = fdata[0]
                          fname = fdata[1]
                          value = matches.group(group_index)
                          if ftype == "int":
                              json_data[fname] = int(value)
                          elif ftype == "list":
                              if not fname in json_data:
                                  json_data[fname] = []
                              json_data[fname].append(value)
                          group_index += 1
                  except (KeyError, IndexError):
                      continue
      self._update_entry_info(json_data)
      return [ json_data ]
      
  def run_linux_args(
      self,
      router_context,
      node_type,
      error_lines,
      json_data
    ):
      """
      Get json output for ethtool command:

      *router_context* - Target router
      *node_type*      - Which node
      *intf*           - Linux interface / device name
      *error_lines*    - Errors messages which do not cause failure 
                         to be returned (some salt errors)
      *json_data*      - Command output as json
      """
      status = self.run_linux_json(
        router_context,
        node_type,
        error_lines,
        json_data
       )
      return status
