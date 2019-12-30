"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import Linux
except ImportError:
    import Linux

try:
    from stage_check import OutputLteLinux
except ImportError:
    import OutputLteLinux


def create_instance():
    return OutputLteLinuxText()


class Base(OutputLteLinux.Base, Output.Text):
  """
  """
  def __init__(self, fullName="OutputLteLinux.Base"):
      super().__init__(fullName=fullName)
      
  def amend_exception(
      self, 
      dev_linux,
      dev_128, 
      exception
      ):
      """
      """
      if dev_128 is not None:
          if "name" in dev_128: 
               exception_string = f"devint {dev_128['name']}: {exception.__class__.__name__} {exception}"
          else:
               exception_string = f"UnNamed 128devInt: {exception.__class__.__name__} {exception}"
      else:
          if "namespace" in dev_linux and \
             "linux_device" in dev_linux:
              exception_string = f"devint {dev_linux['namespace']}/{dev_linux['linux_device']}: {exception.__class__.__name__} {exception}"
          else:
              exception_string = f"UnNamed LinuxDev: {exception.__class__.__name__} {exception}"
      self.message_list.append(exception_string)
      return True

  def amend_missing_json(
      self, 
      json_data 
      ):
      msg=""
      msg_map = [ 
          { "key" : "node_name",    "prefix" : "node=" }, 
          { "key" : "namespace",    "prefix" : "ns=" }, 
          { "key" : "linux_device", "prefix" : "ldev=" }
      ]
      for entry in msg_map:
          try:
              key = entry['key']
              if key in json_data:
                  if len(msg) > 0:
                      msg += " "
                  msg += f"{entry['prefix']}{json_data['key']}" 
          except KeyError:
              continue
      if len(msg) > 0: 
          msg += ": "
      msg += "Jsonified Linux Output Missing Data"
      self.message_list.append(msg)
      return True

  def amend_no_128_config(
      self, 
      info_linux,
      ):
      assert info_linux['node_name'] is not None, pprint.pformat(info_linux)
      message = f"{info_linux['node_name']} devint {info_linux['namespace']}/{info_linux['linux_device']}: No 128T matching config!!!"
      self.message_list.append(message)
      return True


  def amend_no_linux_device(
      self, 
      info_128, 
      ):
      message = f"{info_128['node_name']} devint {info_128['name']}: No Linux info for {info_128['targetInterface']}"
      self.message_list.append(message)
      return True


  def amend_test_result(
          self,
          all_linux, 
          matching_linux,
          t128_entries,
          stats
      ):
      """
      Note that t128_entries are keyed using a compound key consisting of
      <node_name>|<device>. See TestLteInfo.make_device_key(...) for more info
      """
      list_key = Linux.LteInfos.MESSAGE_LIST_KEY
      for entry in matching_linux:
          if list_key in entry:
              for message in entry[list_key]:
                  self.message_list.append(message)

      if self.status == Output.Status.WARN:
           self.message = f"No LTE interfaces found..."
      elif self.status == Output.Status.FAIL:
           self.message = f"{len(self.message_list)} issues with {len(matching_linux)}/{len(all_linux)} "
           self.message += f"(cfg:{len(t128_entries)}/{stats['t128_full_count']}) interfaces"
      else:
           self.message = f"All {len(all_linux)} (cfg:{len(t128_entries)}/{stats['t128_full_count']}) interfaces(s) OK"
      return True


