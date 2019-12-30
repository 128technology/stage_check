#!/usr/bin/python3.6
#########################################################################################
#  _            _      _            _                  _               _                 
# | |_ ___  ___| |_   | |_ _____  _| |_     ___  _   _| |_ _ __  _   _| |_   _ __  _   _ 
# | __/ _ \/ __| __|  | __/ _ \ \/ / __|   / _ \| | | | __| '_ \| | | | __| | '_ \| | | |
# | ||  __/\__ \ |_   | ||  __/>  <| |_   | (_) | |_| | |_| |_) | |_| | |_ _| |_) | |_| |
#  \__\___||___/\__|___\__\___/_/\_\\__|___\___/ \__,_|\__| .__/ \__,_|\__(_) .__/ \__, |
#                 |_____|             |_____|             |_|               |_|    |___/ 
#
# pytest code for human-readable text output (class OutputText)
#
#########################################################################################

import pytest
import pprint

try:
    from stage_check import Output
except ImportError:
    import Output

class TextOutputTester(Output.Text):
  def __init__(self):
      super().__init__()
      
  def add_message(self, message):
      self.message = message

  def set_info(self, test_info):
      self.test_info = test_info

test_info = {
     "TestIndex" : 0,
     "TestDescription" : "Test Line Overwrite"
}

class TestOutputInPlace:
   def check_initialization(self):
      """
      Test classes are not allowed initialization...
      """
      try:
          self.output
      except AttributeError:
          self.output = TextOutputTester()
      try:
          self.prev_line
      except AttributeError:
          self.prev_line = None

   @pytest.mark.parametrize(
      'progress_message',
      [
        "[0]3456789[1]3456789",
        "ABCDEFGHIJKLMNOPQRSTUVXYZ",
        "AAAAAABBBBBBCCCCCCCDDDDDDDEEEEEE",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
      ]
   ) 
   def test_in_place_debug(self, capsys, progress_message):
      """
      Ensure that the in-place algorthm will always overwrite the 
      previous string (by testing the length of the current string 
      (including spaces) against the previous one.
    
      The first paramtrization always passes because there is
      nothing prevous to compare against...
      """
      self.check_initialization()
      self.output.debug = True
      self.output.test_start(test_info)
      self.output.progress_start(fp=None)
      self.output.progress_display(progress_message, fp=None)
      captured = capsys.readouterr()
      all_output = captured.out.splitlines()
      last_line = all_output[-1]
      if self.prev_line is not None:
          assert len(last_line) >= len(self.prev_line)
      self.prev_line = last_line
      self.output.add_message("Test Message")
      #self.output.test_end(fp=None)

   @pytest.mark.parametrize(
      'test_data',
      [
          { 
              "message" : "_internal_->_conductor_2: 10/10 replies from 10.231.124.254; average latency 1.34ms", 
              "output"  : [ 
                  "0  Test Line Overwrite           : \x1b[31m\x1b[01mFAIL  _internal_->_conductor_2: 10/10 replies from 10.231.124.254; average latency\x1b[0m",
                  "   :                               \x1b[31m\x1b[01m          1.34ms\x1b[0m"
               ]
          }
      ]
   ) 
   def test_wrapping(self, capsys, test_data):
      """
      Ensure that the in-place algorthm will always overwrite the 
      previous string (by testing the length of the current string 
      (including spaces) against the previous one.
    
      The first paramtrization always passes because there is
      nothing prevous to compare against...
 
      This test disabled output debugging, which is truer, but
      more difficult to debug in event of failure
      """
      self.check_initialization()
      self.output.debug = False
      self.output.test_start(test_info)
      #self.output.progress_start(fp=None)
      #self.output.progress_display(progress_message, fp=None) 
      self.output.add_message(test_data['message'])
      self.output.test_end(fp=None)
      captured = capsys.readouterr()
      all_output = captured.out.splitlines()
      last_line = all_output[-1]
      #assert False, pprint.pformat(all_output)
      assert all_output == test_data['output']




