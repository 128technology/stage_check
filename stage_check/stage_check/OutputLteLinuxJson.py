"""
"""
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import OutputLteLinux
except ImportError:
    import OutputLteLinux


class Base(OutputLteLinux.Base, Output.Json):
  """
  """
  def __init__(self, fullName="OutputLteLinux.Base"):
      super().__init__(fullName=fullName)

