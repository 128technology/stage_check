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
    return TestLteIfConfig(test_id, config, args)

class TestLteIfConfig(TestLteLinux.Base):
  """
  This is a copy of the TestLteInfo module... This is for LTE info only because it
  has to learn the netns name by ly looking up config
  """
  def __init__(self, test_id, config, args):
      super().__init__(test_id, config, args)

  def linux_command(self):
      return Linux.NetNsIfConfig(
          debug=self.debug,
          progobj=self
      )


