"""
"""

try:
    from stage_check import Output
except ImportError:
    import Output

class Base(Output.Base):
  def __init__(self):
      super().__init__()
      self.__full_name = 'OutputLogs.Base'
      self.status = Output.Status.OK

  def proc_pattern_matched(self, 
                           params,
                           pattern):
      try:
          config = params["patterns"][pattern["pindex"]]
          for key in config:
              if key not in pattern:
                  pattern[key] = config[key]
      except KeyError:
          pass
      try:
          threshold = pattern["threshold"]
          if int(pattern["matches"]) > threshold: 
              self.status  = Output.Status.FAIL
              self.amend_pattern_matched(
                  params,
                  pattern 
              )
      except (KeyError, ValueError) as e:
           self.status  = Output.Status.FAIL
          
      return self.status

  def amend_pattern_matched(
          self, 
          params,
          pattern
      ):
      return True

  """
  amend_test_result
  """

  def proc_test_result(
      self, 
      params,
      stats
      ):
      self.amend_test_result(
          params,
          stats
      )
      return self.status

  def amend_test_result(
      self, 
      params,
      stats
      ):
      return True

