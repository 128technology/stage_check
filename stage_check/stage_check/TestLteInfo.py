"""
"""
import pprint
import ipaddress

try:
    from stage_check import Linux
except ImportError:
    import Linux

try:
    from stage_check import TestLteLinux
except ImportError:
    import TestLteLinux

def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance

    @test_id - test index number
    @config  - test parameters from, config
    @args    - command line args
    """
    return TestLteInfo(test_id, config, args)

class TestLteInfo(TestLteLinux.Base):
  """
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)

  def linux_command(self):
      return Linux.LteStatus(
          debug=self.debug,
          progobj=self
      )

