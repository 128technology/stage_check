"""
"""
import re
import pprint
import json

try:
    from stage_check import ExParser
except ImportError:
    import ExParser

try:
    from stage_check import Output
except ImportError:
    import Output


class MissingOverload(Exception):
  """
  Raised when MatchFunction is not overloaded by a
  derived class
  """

class MatchFunction(object):
  """
  Derived classes will have this method called when
  
  """    
  def process_match(entry, test_index, test, defaults):
      raise MissingOverload

CURRENT_TEST_STRING=''

######################################################################
#
# These classes ares used to define the parse tree nodes -- and after
# parsing are used to process each node to get the result
#
######################################################################

class VariableExpr(ExParser.Expr):
    """
    The variables member is available to all
    instances in the parse tree.
    """
    variables = {}

    def set_variables(variables):
        VariableExpr.variables = variables

    def __init__(self, expr1):
        super().__init__(expr1)

    @property
    def variables(self):
        return VariableExpr.variables


class DualExpr(ExParser.Expr2):
    """
    Gives subclasses methods to infer types from strings
    """
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def infer_type(self, non_string, string):
        if isinstance(non_string, int):
            return int(string)
        elif isinstance(non_string, float):
            return float(string)
        elif isinstance(non_string, bool):
            return bool(string)
        assert False, f"infer_type({non_string}:{non_string.__class__.__name}, {string})"
        return None

    def infer_types(self, left, right):
        try:
            if not isinstance(left, str) and \
               isinstance(right, str):
                right = self.infer_type(left, right)

            if not isinstance(right, str) and \
              isinstance(left, str):
               left = self.infer_type(right, left)
        except NameError:
            pass
        return left, right

    
class OR(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def proc(self):
        left = self.expr1.proc()
        if left:
            result = True
            right =  True
        else:
            right = self.expr2.proc() 
        result = left or right
        if self.debug:
            print(f"{left} or {right}: {result}")
        return result

class AND(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def proc(self):
        left = self.expr1.proc()
        if not left:
            result = False
            right =  False
        else:
            right = self.expr2.proc()
        result = left and right
        if self.debug:
            print(f"{left} and {right}: {result}")
        return result

class EQ(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def proc(self):
        left = self.expr1.proc()
        right = self.expr2.proc() 
        result = left == right
        if self.debug:
            print(f"{left} == {right}: {result}")
        return result

class NE(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def proc(self):
        left = self.expr1.proc()
        right = self.expr2.proc() 
        result = left != right
        if self.debug:
            print(f"{left} != {right}: {result}")
        return result

class LT(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def proc(self):
        proc1 = self.expr1.proc()
        proc2 = self.expr2.proc()
        assert proc1 is not None, CURRENT_TEST_STRING
        assert proc2 is not None, CURRENT_TEST_STRING
        left, right = self.infer_types(self.expr1.proc(), self.expr2.proc())
        result = left < right
        if self.debug:
            print(f"GE: {left} < {right}: {result}")
        return result

class GT(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def proc(self):
        left, right = self.infer_types(self.expr1.proc(), self.expr2.proc())
        result = left > right
        if self.debug:
            print(f"GE: {left} > {right}: {result}")
        return result

class LE(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def proc(self):
        left, right = self.infer_types(self.expr1.proc(), self.expr2.proc())
        result = left <= right
        if self.debug:
            print(f"GE: {left} <= {right}: {result}")
        return result

class GE(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def proc(self):
        left, right = self.infer_types(self.expr1.proc(), self.expr2.proc())
        result = left >= right
        if self.debug:
            print(f"GE: {left} >= {right}: {result}")
        return result

class PLUS(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def expr_add(self, p):
        left = self.expr1.proc()
        right = self.expr2.proc() 
        if self.debug:
            print(f"{left} + {right}: {left + right}")
        return left + right


class MINUS(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def proc(self):
        left = self.expr1.proc()
        right = self.expr2.proc() 
        result = left - right
        if self.debug:
            print(f"{left} - {right}: {result}")
        return result

class MULT(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def proc(self, p):
        left = self.expr1.proc()
        right = self.expr2.proc() 
        result = left * right 
        if self.debug:
            print(f"{left} * {right}: {result}")
        return result

class DIVIDE(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def expr_add(self, p):
        left = self.expr1.proc()
        right = self.expr2.proc() 
        result = left / right
        if self.debug:
            print(f"{left} / {right}: {result}")
        return result

class MODULO(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def expr_add(self, p):
        left = self.expr1.proc()
        right = self.expr2.proc() 
        result = left % right
        if self.debug:
            print(f"{left} % {right}: {result}")
        return result

class REGEX(DualExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)
        
    def proc(self):
        left = self.expr1.proc()
        right = self.expr2.proc() 
        if not isinstance(left, str) or \
           not isinstance(right, str):
            raise ValueError
        matches = re.search(left, right)
        result = matches is not None
        if self.debug:
            print(f"{left} =~ {right}: {result}")
        return result

class UMINUS(ExParser.Expr):
    def __init__(self, expr1):
        super().__init__(expr1)

    def proc(self):
        right = self.expr1.proc()
        result = -right
        if self.debug:
            print(f"-{right}:  -{right}")
        return result

class PARENS(ExParser.Expr): 
    def __init__(self, expr1):
        super().__init__(expr1)

    def proc(self):
        result = self.expr1.proc()
        if self.debug:
            print(f"(expr): {result}")
        return result

class TYPE2STR(ExParser.Expr):
    def __init__(self, expr1):
        super().__init__(expr1)

    def proc(self):
        result = None
        type_name = 'Undefined'
        try:
            result = self.expr1.proc()
            type_name = result.__class__.__name__
            if type_name == 'NoneType':
                type_name = 'None'
        except (NameError, KeyError, AttributeError) as e:
            pass
        if self.debug:
            print(f"@{result}: {type_name}")
        return type_name

class INT(ExParser.Expr):
    def __init__(self, expr1):
        super().__init__(expr1)

    def proc(self):
        result = int(self.expr1)
        return result

class FLOAT(ExParser.Expr):
    def __init__(self, expr1):
        super().__init__(expr1)

    def proc(self):
        result = float(self.expr1)
        return result

class KEY(VariableExpr):
    def __init__(self, expr1):
        super().__init__(expr1)

    def proc(self):
        """
        Let any exceptions bubble up because DEFINED will need them
        in order to asses whether or not variables[ID] is defined
        """
        keys = self.expr1.split('.')
        value = self.variables
        for k in keys:
            value = value[k]
        if self.debug:
            print(f"entry[{self.expr1}] = {value}")
        return value
     
class DEFINED(ExParser.Expr):
    def __init__(self, expr1):
        super().__init__(expr1)

    def proc(self):
        """
        Because DEFINED is truly an operation now, the expresion is 
        no longer assumed to be a variable name to be dereferenced;
        it is evaulated and depending on the exceptions or lack thereof
        returns a result 
        """
        try:
            result = self.expr1.proc()
        except (NameError, AttributeError, KeyError) as e:
            return False
        return True

class NOT(ExParser.Expr):
    def __init__(self, expr1):
        super().__init__(expr1)

    def proc(self):
        return not self.expr1.proc()

class STRING(ExParser.Expr):
    def __init__(self, expr1):
        super().__init__(expr1)

    def proc(self):
        return self.expr1[1:-1]


class BOOL(ExParser.Expr):
    def __init__(self, expr1):
        super().__init__(expr1)
  
    def proc(self):
        return self.expr1 == 'True'


class Parser(object):

  tokenClasses = {
       'UMINUS'   : UMINUS,
       'DEFINED'  : DEFINED,
       'TYPE2STR' : TYPE2STR,
       'EQ'       : EQ,
       'NE'       : NE,
       'LT'       : LT,
       'GT'       : GT,
       'LE'       : LE,
       'GE'       : GE,
       'MINUS'    : MINUS,
       'PLUS'     : PLUS,
       'MULT'     : MULT,
       'DIVIDE'   : DIVIDE,
       'MODULO'   : MODULO,
       'AND'      : AND, 
       'OR'       : OR,
       'PARENS'   : PARENS,
       'INT'      : INT,
       'KEY'      : KEY,
       'STRING'   : STRING,
       'FLOAT'    : FLOAT,
       'BOOL'     : BOOL, 
       'REGEX'    : REGEX,
       'NOT'      : NOT
  }

  def __init__(self, debug=False):
      self.__lexer  = ExParser.Lexer()
      self.__parser = ExParser.Parser()
      self.__lexer.debug = debug
      self.__parser.debug = debug
      self.__debug = debug
      self.__parser.set_class_map(Parser.tokenClasses)
      ExParser.Expr.debug = debug

  @property
  def lexer(self):
      return self.__lexer

  @property
  def parser(self):
      return self.__parser

  @property
  def debug(self):
      return self.__debug

  def true_value(self, value):
      """
      """
      try:
          return bool(value)
      except NameError:
          return False

  def exclude_entry(self, entry, exclude_tests):
      """
      Evaluate entry against list of exclude tests.  Returns True
      if it matches, False if it does not.

      *entry*          Dictionary derived from flattened graphql json reply, 
                       Linux command etc.
      *exclude_tests*  Dictionary of tests to run against this entry
      """
      VariableExpr.variables = entry
      matched = False
      rule_number=0
      for item in exclude_tests:
          try:
              tokens = self.lexer.tokenize(item)
              tree = self.parser.parse(tokens)
              result = tree.proc()
          except Exception as e:
              entry["exclude_rule"]   = item
              entry["exclude_exception"] = f"rule {rule_number}: {e.__class__.__name__} exception '{e}'"
              break
          matched = self.true_value(result)
          if matched:
              if self.debug:
                 print(f"exclude_entry[{rule_number}]: Matched {item}\n")
              matched = True
              break
          else:
              if self.debug:
                 print(f"exclude_entry[{rule_number}]: No Match {item}\n")
          rule_number = rule_number + 1
      return matched

  def eval_entry_by_test(self, entry, test_index, test_entry, defaults):
      """
      *entry*        Entry from json reply list, Linux command etc.
                     Linux command etc.
                     Linux command etc.
      *test_index*   Dictionary of tests to run against this entry
      *test_entry*   Test (dictionary) to run against this entry
      *defaults*     Default values if not present in test_entry

      Returns None if:
          (1) entry did not match the test
          (2) entry matched but no status could be found
      """ 
      fname = "eval_entry_by_test"
      return_status = None
      if self.debug:
          print(f"{fname}[#{test_index}]: check entry against {test_entry['test']}")
      try:
          CURRENT_TEST_STRING = test_entry["test"]
          VariableExpr.variables = entry
          tokens = self.lexer.tokenize(test_entry["test"])
          tree = self.parser.parse(tokens)
          result = tree.proc()
          if self.debug:
              print(f"{fname}[#{test_index}]: parse({test_entry['test']}) -> RESULT:{result}")
      except Exception as e:
          return_status = Output.Status.FAIL
          entry["test_status"]    = return_status
          entry["test_matched"]   = test_entry
          entry["test_index"]     = test_index
          entry["test_exception"] = f"Rule #{test_index}: {e.__class__.__name__} exception '{e}'"
          if self.debug:
              print(f"{fname}[#{test_index}]: EXCEPTION {e.__class__.__name__} {e}")
          return return_status
      matched = self.true_value(result)
      if self.debug:
          print(f"{fname}[#{test_index}]: true_value({result}) -> {matched}")
      if matched:
          if "status" in test_entry:
              status = test_entry["status"]
          elif "status" in defaults:
              status = defaults["status"]
          else:
              return None
          format_string = None
          if "format" in test_entry:
              format_string = test_entry["format"]
          elif "format" in defaults:
              format_string = defaults["format"]
          return_status = Output.text_to_status(status)
          if self.debug:
              print(f"{fname}[#{test_index}]: {status} matched -> "
                    f"{Output.text_to_status(status)}({status})")
          entry["test_status"]    = return_status
          entry["test_matched"]   = test_entry
          entry["test_index"]     = test_index
          entry["test_format"]    = format_string
          entry["test_exception"] = None
      return return_status


  def eval_entry_by_tests(self, entry, entry_tests):
      """
      *entry*        Entry from json reply list, Linux command etc.
                     Linux command etc.
      *entry_tests*  Dictionary of tests to run against this entry
      """
      no_match = { "status" : None }
      defaults = {}
      tests    = entry_tests["tests"]
      if "no_match" in entry_tests:
          no_match = entry_tests["no_match"]
      if "defaults" in entry_tests:
          defaults = entry_tests["defaults"]

      if self.debug:
          print("-------  eval_entry_by_tests: the entry  --------")
          pprint.pprint(entry)
          print("-------  eval_entry_by_tests: the tests  --------")
          pprint.pprint(entry_tests)
          print("-------------------------------------------------")

      return_status = None
      test_index = 0 

      for test in tests:
          current_status = self.eval_entry_by_test(entry, test_index, test, defaults)
          if current_status is not None:
              return_status = current_status
              break
          test_index += 1

      if return_status is None:
          return_status = Output.text_to_status(no_match["status"])
          entry["test_status"]      = return_status    
          entry["test_matched"]     = None
          entry["test_exception"]   = None
          if "format" in no_match:
              entry["test_format"]  = no_match["format"] 
          if self.debug:
              print(f"test_entry[#N/A]: return_status None -> "
                    f"{Output.status_to_text(return_status)} ({return_status})")
      return return_status


  def eval_tests_by_entry(self, entry, entry_tests, func_object):
      """
      *entry*        Entry from json reply list, Linux command etc.
                     Linux command etc.
      *entry_tests*  Dictionary of tests to run against this entry
      *func*         Function to execute
      """
      defaults = {}
      tests      = entry_tests["tests"]
      if "defaults" in entry_tests:
          defaults = entry_tests["defaults"]

      self.parser.json_entry = entry
      if self.debug:
          print("-------  eval_entry_by_tests: the entry  --------")
          pprint.pprint(self.parser.json_entry)
          print("-------  eval_entry_by_tests: the tests  --------")
          pprint.pprint(entry_tests)
          print("-------------------------------------------------")

      test_index = 0 
      for test in tests:
          return_status = None
          current_status = self.eval_entry_by_test(entry, test_index, test, defaults)
          if current_status is not None:
              func_object.process_match(entry, test_index, test, defaults)
          test_index += 1


