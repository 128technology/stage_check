"""
"""
import re
import json
import pprint

def text_to_status(text):
    """
    Returns None if no match is found
    """
    status_dict = {
          'OK'   : Status.OK,
          'PASS' : Status.OK,
          'FAIL' : Status.FAIL,
          'WARN' : Status.WARN,
          'NONE' : Status.NONE,
    }
    if text is not None:
        upper_text = text.upper()
        if upper_text in status_dict:
            return status_dict[upper_text]
    return None

def status_to_text(status):
    if status is not None:
        status_text = {}
        status_text[Status.FAIL] = "FAIL"
        status_text[Status.OK]   = "PASS"
        status_text[Status.WARN] = "WARN"
        status_text[Status.NONE] = "NONE"
        return Status_strings[status]
    return None

def init_result_stats(stats):
    status_list = [
        "NONE",
        "OK",
        "FAIL",
        "WARN"
    ]
    stats["total_count"]     = 0
    stats["tested_count"]    = 0
    stats["exclude_count"]   = 0
    stats["match_count"]     = 0
    stats["non_match_count"] = 0
    for entry in status_list:
        stats[entry] = 0

def update_stats(stats, result):
    try:
        stats["tested_count"] += 1
    except KeyError:
        stats["tested_count"] = 1
    if result is None or \
       result == Status.NONE:
        try:
            stats["non_match_count"] += 1
        except KeyError:
            stats["non_match_count"] = 1
    else:
        try:
            stats["match_count"] += 1
        except KeyError:
            stats["match_count"] = 1
        stats_key = status_to_text(result)
        if stats_key is None:
            stats_key = "NONE"
        try:
            stats[stats_key] += 1
        except KeyError:
            stats[stats_key] = 1

 
def populate_format(entry, sformat):
    """
    replace entry keys in format with corresponding values

    Given:
    (1) entry   = { "actions" : "words", "words" : "actions" } 
    (2) sformat = "{actions} speak louder than {words}"     
    
    result  = "words speak louder than actions"    
    """
    result  = sformat 
    pattern = '\{([^\{\}]+)\}'
    matches = re.findall(pattern, sformat)
    for key in matches:
        key_list = key.split('.')
        value = entry
        keys_exist = True
        for k in key_list:
            if k in value:
                value = value[k]
            else:
                keys_exist = False
                value = None
                break
        if keys_exist == True:
            target = "{" + f"{key}" + "}"
            result = result.replace(target, f"{value}")
    return result

class MissingOverload(Exception):
      """
      Raised when the base class is method is not overloaded...
      """
      pass

class Status:
    OK, \
    FAIL, \
    WARN, \
    NONE = range(4)


Status_strings = {
    Status.FAIL  : "FAIL",
    Status.OK    : "PASS",
    Status.WARN  : "WARN",
    Status.NONE  : "NONE"
}

class Base:

  def __init__(self):
      """
      """
      self.__status     = Status.FAIL
      self.__full_name = 'Output.Base'
      self.file_name  = None
      self.test_info  = {}

      self._debug = False

  @property
  def debug(self):
     return self._debug

  @debug.setter
  def debug(self, value):
     if isinstance(value, bool):
         self._debug = value

  @property
  def full_name(self):
     return self.__full_name

  @property
  def status(self):
      return self.__status

  @status.setter
  def status(self, status):
      self.__status = status

  def set_status(self, status):
      self.status = status
      return status

  def is_status_ok(self):
      return self.status == Status.OK

  def test_start(self, test_info, status=None):
      """
      Initialize test information
      """
      self.test_info = test_info
      if status is not None:
          self.status = status


  def progress_start(self, fp):
      """
      Used to indicate progress during textual output (the original output
      mode of stage check).  For non-textual output there is no point in
      overloading...
      """

  def progress_display(self, message, fp):
      """
      Used to indicate progress during textual output (the original output
      mode of stage check).  For non-textual output there is no point in
      overloading...
      """

  def progress_end(self):
      """
      Used to indicate progress during textual output (the original output
      mode of stage check).  For non-textual output there is no point in
      overloading...
      """

  def test_end(self):
      """
      On test ending, results might be output, or json snippets might
      be edited to become parseable.
      """
      raise MissingOverload

  def unsupported_node_type(self, local_info):
      raise MissingOverload

  def run_as_wrong_user(self, user, status=Status.WARN):
      raise MissingOverload

  def graphql_error(self, status_code, error_list=None):
      raise MissingOverload

  def test_end_by_status(self, status_list = []):
      """
      Perform whatever action occurs at test_end() except
      only if self.status matches an entry in the passed list
      
      @status_list -- List of statuses to natch
      """

  # default
  def proc_run_linux_error(self, 
                           shell_status, 
                           error_line):
      self.status  = Status.FAIL
      self.amend_run_linux_error(
          shell_status, 
          error_line
          )
      return self.status


class Text(Base):

  class AnsiModes:
      """
      Terminal control sequences for color and style
      """
      reset='\033[0m'
      bold='\033[01m'
      disable='\033[02m'
      underline='\033[04m'
      reverse='\033[07m'
      strikethrough='\033[09m'
      invisible='\033[08m'

  class AnsiColors:
      black='\033[30m'
      red='\033[31m'
      green='\033[32m'
      orange='\033[33m'
      blue='\033[34m'
      purple='\033[35m'
      cyan='\033[36m'
      lightgrey='\033[37m'
      darkgrey='\033[90m'
      lightred='\033[91m'
      lightgreen='\033[92m'
      yellow='\033[93m'
      lightblue='\033[94m'
      pink='\033[95m'
      lightcyan='\033[96m'
      _black='\033[40m'
      _red='\033[41m'
      _green='\033[42m'
      _orange='\033[43m'
      _blue='\033[44m'
      _purple='\033[45m'
      _cyan='\033[46m'
      _lightgrey='\033[47m'
 
  def empty_message(self):
     return (self.message is None or \
             self.message == '')

  FIRST_INDENT = 33
  FORMAT_WIDTH = 100

  def __init__(self):
      super().__init__()
      self.message         = None
      self.message_list    = []
      self.progress_msglen = None

  def format(self, status, description, message, fp=None):
      """
      Formatted output

      Test Name         Pass/Fail      Commentary/multiline
      """
      prestr  = ''
      poststr = ''
      midstr  = ''
      if  status == Status.FAIL:
          prestr  = Text.AnsiColors.red
          prestr  = prestr + Text.AnsiModes.bold
          poststr = Text.AnsiModes.reset
          smsg    = "FAIL"
      elif status == Status.WARN:
          prestr  = Text.AnsiColors.blue
          prestr  = prestr + Text.AnsiModes.bold
          poststr = Text.AnsiModes.reset
          smsg    = "WARN"
      elif status == Status.OK:
          prestr  = Text.AnsiColors.green
          prestr  = prestr + Text.AnsiModes.bold
          midstr  = Text.AnsiModes.reset
          smsg    = "PASS"
      else:
          smsg    = "    "

      if description == '':
          desc_string = '   :'
          desc_string = f'{desc_string:<{self.FIRST_INDENT}.{self.FIRST_INDENT}} '
      else:
          desc_string = description[0:self.FIRST_INDENT-1]
          desc_string = f'{desc_string:<{self.FIRST_INDENT}.{self.FIRST_INDENT}}:'

      default_width = self.FORMAT_WIDTH
      if message is None:
          message=' '

      message_list = message.split('\n')
      for line in message_list:
          line_index = 0
          line_length = len(line)
          indent_string = ' '
          while  line_index < line_length:
              indent_length = len(indent_string)
              max_line_index  = line_index + self.FORMAT_WIDTH - indent_length
              output_line = indent_string + line[line_index:max_line_index]
              try:
                  last_space_index = output_line.rindex(' ')
                  if last_space_index > self.FORMAT_WIDTH - 25:
                      max_line_index = max_line_index - (len(output_line) - last_space_index)
                      output_line = output_line[0:last_space_index]
              except ValueError:
                  pass   
              if fp is None:
                  print(f'{desc_string} {prestr}{smsg}{midstr} {output_line}{poststr}')
              else:
                  fp.write(f'{desc_string} {smsg} {output_line}\n')
              line_index = max_line_index
              indent_string='     '


  def format_in_place(self, prevlen=0, desc=None, msg=None, fp=None):
      if fp is not None:
          return
      if prevlen is None:
          return
      pad=0
      message=' '
      if msg is not None:
          message = msg
      msglen=len(message)
      if prevlen > msglen:
          pad = prevlen - msglen
      if desc is None:
          description=f"{' ':<{self.FIRST_INDENT}.{self.FIRST_INDENT}} "
      else:
          debug_string=''
          if self.debug:
              debug_string = f"<{prevlen}:{msglen}:{pad}>"
          desc = desc + debug_string
          description=f"{desc:<{self.FIRST_INDENT}.{self.FIRST_INDENT}}:"
      if self.debug:
          line = f"{description}$       {message}{' ':<{pad}.{pad}}"
          line = line + '$\n'
      else:
          line = f"{description}       {message}{' ':<{pad}.{pad}}"
      print(f"\r{line}", end='')
      if desc is None:
          print("\r", end='')
      return msglen


  def clear_results_dict(self):
      self.results = {}

  """
  TODO -- There shoud be no need for a separate dictionary because 
          the results are stored in the output and each test
          instance instantiates a new output object
  """
  def results_to_dict(self, status, msg, msg_list):
      """
      Save Test output to a json-like dictionary for post test-run
      processing...
      """
      self.results = {}
      self.results['status']       = status
      self.results['message']      = msg
      self.results['message-list'] = msg_list

  def output_results_dict(self, status_list = []):
      try:
          if self.results['status'] in status_list:
              self.output_results(self.results['status'], self.results['message'],
                                  self.results['message-list'])
      except KeyError:
          pass

  def output_results(self, status, msg, msg_list=[], fp=None):
      desc = f"{self.test_info['TestIndex']:<3}{self.test_info['TestDescription']}"
      self.format(status, desc, msg, fp)
      if msg_list is not None:
          for message in msg_list:
              self.format(Status.NONE, '', message, fp)
      if fp is not None:
          self.results_to_dict(status, msg, msg_list)

  def unsupported_node_type(self, local_info):
      self.message = f"Test not supported by node {local_info.get_node_name()} type " \
                     f"{Text.AnsiColors.red}{local_info.get_node_type()}"
      self.status = Status.WARN
      return self.status

  def run_as_wrong_user(self, user, status=Status.WARN):
      self.status = status
      self.message = f'Run script from Linux as user {user}'
      return self.status

  def graphql_error(self, status_code, error_list=None):
      self.status = Status.FAIL
      if status_code is None:
          self.message = f"GraphQL server returned No status code"
      elif status_code > 299:
          self.message = f"GraphQL server returned ERROR {status_code}"
      else:
          self.message = f"GraphQL API returned errors"
      if error_list is not None and \
          len(error_list) > 0:
          self.message_list = error_list.copy()
      return self.status

  def test_end(self, fp, status=None):
      if status is not None:
          self.status = status
      if self.progress_msglen is not None:
          self.progress_end()
      self.output_results(self.status, self.message, self.message_list, fp)
      return self.status

  def progress_start(self, fp):
      """
      Used to indicate progress during textual output (the original output
      mode of stage check).  For non-textual output there is no point in
      overloading...
      """
      self.progress_msglen = self.format_in_place(0, self.test_info["TestDescription"], fp=fp)

  def progress_display(self, message, fp=None):
      """
      Used to indicate progress during textual output (the original output
      mode of stage check).  For non-textual output there is no point in
      overloading...
      """
      if self.progress_msglen is None:
          self.progress_start(fp)
      desc = f"{self.test_info['TestIndex']:<3}{self.test_info['TestDescription']}"
      self.progress_msglen = self.format_in_place(
          self.progress_msglen, 
          desc, 
          message, 
          fp=fp
      )

  def test_end_by_status(self, status_list = []):
        if self.status in status_list:
            self.output_results(self.status, self.message,
                                self.message_list)

  def progress_end(self):
      """
      Used to indicate progress during textual output (the original output
      mode of stage check).  For non-textual output there is no point in
      overloading...
      """
      self.format_in_place(prevlen=self.progress_msglen)

  def entry_result_to_text(self, entry):
      sformat = None
      string = None
      if "test_exception" in entry and \
          entry["test_exception"] is not None:
          sformat = entry["test_exception"]
      elif "test_format" in entry:
          sformat = entry["test_format"]
      if sformat is not None:
          string = populate_format(entry, sformat)
      if string is not None:
          self.message_list.append(string) 
      return True

  def test_result_to_text(self, entry_tests, stats):
      pass_format = "No Format Provided!"
      fail_format = pass_format
      try:
         pass_format = entry_tests["result"]["PASS"]
         fail_format = entry_tests["result"]["FAIL"]
      except KeyError:
         print(f"*************** KEY ERROR *********************")
         pass

      if self.status != Status.OK:
          message = populate_format(stats, fail_format)
      else:
          message = populate_format(stats, pass_format)
      self.message = message
      return True  
  """
  Common Output Ammend methods... 
  """  
  def amend_run_linux_error(
          self,
          return_status,
          error_string
      ):
      """
      @return_status
      @error_string
      """
      self.message = error_string



class Json(Base):
  def __init__(self):
      super().__init__()

  def transform(self, dict_out):
      """
      format converts the test_info (which should be created at the beginning of 
      any test) into a form which can be parsed by logstash
      """
      dict_out.clear()
      tags   = {}
      fields = {}

      tag_keys = [
          "node_type",         
          "StageCheckVersion", 
          "TestVersion",       
          "TestDescription",   
          "TestIndex",         
          "TestIndexLast",         
          "RouterIndex",         
          "RouterIndexLast",         
          "InvokingRouter",    
          "InvokingNode",      
          "InvokingRole",      
          "Router",            
          "Node",              
          "NodeType",          
          "Asset",
      ]

      field_keys = [
          "GQLStatus",
          "NotRootUser"
      ]
 
      try:
          tstamp_result = self.test_info["DateTime"].timestamp()
          tstamp_int   = int(tstamp_result)
          dict_out["timestamp"] = tstamp_int
          dict_out["name"] = self.test_info["TestModule"]
      except (KeyError, ValueError) as e:
          pass

      for key in tag_keys:
          try:
              tags[key] = self.test_info[key]
          except KeyError:
              pass

      for key in field_keys:
          try:
              fields[key] = self.test_info[key]
          except KeyError:
              pass

      dict_out["tags"]   = tags
      dict_out["fields"] = fields

  def run_as_wrong_user(self, user, status=Status.WARN):
      self.status = status
      self.test_info["NotUserRoot"] = 1
      return self.status

  def unsupported_node_type(self, local_info):
      self.status = Status.WARN
      return self.status

  def graphql_error(self, status_code, error_list=None):
      self.status = Status.FAIL
      self.test_info["GQLStatus"] = status_code
      return self.status

  def test_end(self, fp, status=None):
      """  
      """
      sample = { }
      skip_last_postfix=False
      indent_string = "    "

      try:
         if self.test_info["TestIndex"] + 1 == self.test_info["TestIndexLast"] and \
            self.test_info["RouterIndex"] == self.test_info["RouterIndexLast"]:
             skip_last_postfix = True
      except KeyError:
         pass

      self.transform(sample)
      if status is None:
          status = self.status
      try:
          sample["fields"]["TestStatus"] = self.status
      except KeyError:
          pass
      json_string = json.dumps(sample, indent=4, sort_keys=True)
      lines = json_string.splitlines()
      json_string_count = len(lines)
      line_count = 1
      for line in lines:
          postfix=""
          if line_count == json_string_count and \
             skip_last_postfix == False:
              postfix = ","
          if self.debug:
              print(f"{indent_string}{line}{postfix} {line_count}/{json_string_count} {skip_last_postfix} "
                    f"{self.test_info['TestIndex']}/{self.test_info['TestIndexLast']} "
                    f"{self.test_info['RouterIndex']}/{self.test_info['RouterIndexLast']}")
          else:
              print(f"{indent_string}{line}{postfix}")
          line_count += 1
