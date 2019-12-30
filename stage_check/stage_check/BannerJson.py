"""
"""

try:
    from stage_check import Banner
except ImportError:
    import Banner

def create_instance():
    return BannerJson()

class BannerJson(Banner.Base):
  """
  For Logstash, output metric list wrapper
  """
  def __init__(self):
      super().__init__()

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
          print('[\n')
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
          print(']')
      return True



