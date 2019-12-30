"""
"""

try:
    from stage_check import Banner
except ImportError:
    import Banner

def create_instance():
    return BannerJson()

try:
    from stage_check import _version
except ImportError:
    import _version

class BannerJson(Banner.Base):
  """
  For Logstash, output metric list wrapper
  """
  def __init__(self):
      super().__init__()
      self.__tool_version = _version.__version__

  @property
  def tool_version(self):
     return self.__tool_version

  def header_summary(
          self, 
          router_context
       ):
        return False

  def header(
          self, 
          router_context, 
          router_count, 
          router_max,
          fp=None
      ):
      if router_count == 1:
          header  = '{\n'
          header += f'    "version" : "{self.tool_version}",\n'
          header += f'    "results" : ['
          if fp is None:
              print(header, end='')
          else:
              fp.write(header)
      return True

  def trailer_summary(
          self, 
          router_context
       ):
      return False

  def trailer (
          self, 
          router_context, 
          router_count, 
          router_max, 
          fp=None
      ):
      if router_count == router_max:
          trailer  = "    ]\n"
          trailer += "}"
          if fp is None:
              print(trailer)
          else:
              fp.write(trailer)
      return True



