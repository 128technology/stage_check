"""
"""

class MissingOverload(Exception):
      """
      Raised when the base class is method is not overloaded...
      """
      pass

class Base(object):
  def __init__(self):
      self.place_holder = True

  """
  Module to create Text Banners.  Abstracted out because these have 
  no place when creating json output (in this case the only test banner
  might be a comma).
  """
  def header_summary(
          self, 
          router_context,
          tests_by_status
       ):
       """
       Output summary of Router information
       """
       raise MissingOverload

  def header(
          self, 
          router_context, 
          router_count, 
          router_max,
          fp=None
      ):
      """
      Invoked before a router's test is started to output
      Interesting information about that Router
      """
      raise MissingOverload

  def trailer_summary(
          self, 
          router_context
       ):
       """
       Output summary of Router information
       """
       raise MissingOverload

  def trailer(
          self, 
          router_context, 
          router_count, 
          router_max, 
          fp=None
      ):
      """
      Invoked before a router's test is started to output
      Interesting information about that Router
      """
      raise MissingOverload

