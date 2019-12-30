"""
"""

try:
    from stage_check import Banner
except ImportError:
    import Banner

try:
    from stage_check import Output
except ImportError:
    import Output

def create_instance():
    return BannerText()

class BannerText(Banner.Base):
  """
  Module to create Text Banners.  Abstracted out because these have 
  no place when creating json output (in this case the only test banner
  might be a comma).
  """
  def __init__(self):
      super().__init__()

  def count_results(self, tests_by_status, status):
      """
      This is duplcate code for a method by the same name in TestExecutor
      which eeds to be addressed at some point
      """
      try:
          count = len(tests_by_status[status]) 
      except (KeyError, TypeError):
          count = 0
          pass
      return count

  def header_summary(
          self, 
          router_context,
          tests_by_status
      ):
      """
      Output short 1 line summary for successful tests when using the
      the -o option (since multiple routers are tested in this case
      the emphasis is only on the routers which fail tests
      """
      router_string = f'Router: {router_context.get_router()}'
      status_string=''
      for key in tests_by_status:
          if status_string != '':
              status_string += ','
          value = self.count_results(tests_by_status, key)
          xlated_key = key
          if key in Output.Status_strings:
              xlated_key = Output.Status_strings[key]
          status_string = status_string + f'{xlated_key}:{value}'
      summary_string = router_context.display_extra_info_summary()
      if summary_string is not None:
          summary_string = ' ' + summary_string
      print(f'{router_string} ({status_string}){summary_string}')
      return True


  def format_node_string(
          self, 
          node_type, 
          node, 
          asset, 
          version, 
          line_list
      ):
      if node is not None:
          line = f'{node_type} {node}'
          if asset is not None: 
              line += f' ({asset})'
          if version is not None: 
             line += f' {version}'
          line_list.append(line)


  def header(
          self, 
          router_context, 
          router_count, 
          router_max, 
          fp=None
      ):
      """
      Output information about the router being tested
      Invokes RouterContext override display_extra_info_header()
      """
      router_lines = [ f'Router:    {router_context.get_router()} [{router_count}/{router_max}]' ]
      footerlen = 0
      self.format_node_string('Primary:  ', router_context.primary_name(),
                              router_context.get_primary_asset(),
                              router_context.get_primary_version(),
                              router_lines)
      self.format_node_string('Secondary:', router_context.secondary_name(),
                              router_context.get_secondary_asset(),
                              router_context.get_secondary_version(),
                              router_lines)
      self.format_node_string('Solitary:   ', router_context.solitary_name(),
                              router_context.get_solitary_asset(),
                              router_context.get_solitary_version(),
                              router_lines)
      extra_info_lines = []
      router_context.display_extra_info_header(extra_info_lines)
      router_lines.extend(extra_info_lines)
      if fp is None:
          for line in router_lines:
              if footerlen < len(line):
                  footerlen = len(line)
              print(f'{line}') 
          print('-' * footerlen) 
      else:
          for line in router_lines:
              if footerlen < len(line):
                  footerlen = len(line)
              line.strip('\n')
              fp.write(f'{line}\n')
          fp.write('-' * footerlen) 
          fp.write('\n') 
      return True  

  def trailer_summary (
          self, 
          router_context
      ):
      return False

  def trailer(
          self, 
          router_context, 
          router_count, 
          router_max, 
          fp=None
      ):
      print('')
      return True

