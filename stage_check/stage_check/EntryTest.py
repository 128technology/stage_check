"""
"""
import re
import pprint

import sly

try:
    from stage_check import Output
except ImportError:
    import Output

class LexerError(Exception):
    """
    Raised when Lexer token extraction error occurs 
    w/o debug enabled...
    """
    pass

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

class TestLexer(sly.Lexer):
    # Set of token names.   This is always required
    tokens = { INT, FLOAT, KEY, STRING, BOOL, KEY_TEST,
               TYPE2STR,
               PLUS, MINUS, MULT, DIVIDE, REGEX,
               EQ, LT, LE, GT, GE, NE, 
               OR, AND,
               LPAREN, RPAREN }

    literals = { '(', ')', '\'', '@', '+', '-', '*', '/' }

    # String containing ignored characters
    ignore = ' \t'

    # Regular expression rules for tokens
    PLUS     = r'\+'
    MINUS    = r'-'
    MULT     = r'\*'
    DIVIDE   = r'/'
    REGEX    = r'=~'
    EQ       = r'=='
    LE       = r'<='
    LT       = r'<'
    GE       = r'>='
    GT       = r'>'
    NE       = r'!='
    OR       = r'\|\|'
    AND      = r'&&'
    LPAREN   = r'\('
    RPAREN   = r'\)'
    TYPE2STR = r'@'

    @_(r'\d+')
    def INT(self, t):
        t.value = int(t.value)
        return t

    # Identifiers and keywords
    FLOAT     = r'[0-9]+\.[0-9]+'
    INT       = r'[0-9]+'
    KEY       = r'[a-zA-Z0-9]+([\.\/_-]+[a-zA-Z0-9]+)*'
    KEY_TEST  = r'\?[a-zA-Z0-9]+([\.\/_-]+[a-zA-Z0-9]+)*'
    STRING    = r'\'[^\']*\''

    KEY['True']  = BOOL
    KEY['False'] = BOOL

    ignore_comment = r'\#.*'

    # Line number tracking
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        if self.debug:
            print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        else:
            raise LexerError            
        self.index += 1

    @property
    def debug(self):
        return self.__debug 

    @debug.setter
    def debug(self, value):
        self.__debug = value


class TestParser(sly.Parser):
    """
    Consider adding support for unary operators:
    - negativity operator
    ! logical negation
    ? dictionary key existence

    Additional binary:
    =~ regex match
    """
    precedence = (
        ('left', PLUS, MINUS),
        ('left', MULT, DIVIDE),
        ('right', UMINUS),            # Unary minus operator
    )

    tokens = TestLexer.tokens

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, debug):
        if isinstance(debug, bool):
            self.__debug = debug

    @property
    def json_entry(self):
        return self.__json_entry

    @json_entry.setter
    def json_entry(self, json_entry):
        if isinstance(json_entry, dict):
            self.__json_entry = json_entry

    def infer_type(self, non_string, string):
        if isinstance(non_string, int):
            return int(string)
        elif isinstance(non_string, float):
            return float(string)
        elif isinstance(non_string, bool):
            return bool(string)
        return None

    def infer_types(self, left, right):
        #print(f"INFER(I) L={left}({type(left)} R={right}({type(right)}")
        if not isinstance(left, str) and \
           isinstance(right, str):
           right = self.infer_type(left, right)

        if not isinstance(right, str) and \
           isinstance(left, str):
           left = self.infer_type(right, left)
             
        #print(f"INFER(O) L={left}({type(left)} R={right}({type(right)}")
        return left, right
    
    @_('expr_or OR expr_and')
    def expr_or(self, p):
        if self.debug:
            print(f"{p[0]} || {p[2]}: {p[0] or p[2]}")
        return p[0] or p[2] 

    @_('expr_and')
    def expr_or(self, p):
        return p.expr_and

    @_('expr_and AND expr_comp')
    def expr_and(self,p):
        if self.debug:
            print(f"{p[0]} && {p[2]}: {p[0] and p[2]}")
        return p[0] and p[2]   

    @_('expr_comp')
    def expr_and(self, p):
        return p.expr_comp

    @_('expr_comp EQ expr_add')
    def expr_comp(self, p):
        if self.debug:
            print(f"{p[0]} == {p[2]}: {p[0] == p[2]}")
        return p[0] == p[2]

    @_('expr_comp NE expr_add')
    def expr_comp(self, p):
        if self.debug:
            print(f"{p[0]} != {p[2]}: {p[0] != p[2]}")
        return p[0] != p[2]

    @_('expr_comp GT expr_add')
    def expr_comp(self, p):
        left, right = self.infer_types(p[0], p[2])
        if self.debug:
            print(f"GT: {left} > {right}: {left > right}")
        return left > right

    @_('expr_comp LT expr_add')
    def expr_comp(self, p):
        left, right = self.infer_types(p[0], p[2])
        if self.debug:
            print(f"LT: {left} < {right}: {left < right}")
        return left < right

    @_('expr_comp LE expr_add')
    def expr_comp(self, p):
        left, right = self.infer_types(p[0], p[2])
        if self.debug:
            print(f"LE: {left} <= {right}: {left <= right}")
        return left <= right

    @_('expr_comp GE expr_add')
    def expr_comp(self, p):
        left, right = self.infer_types(p[0], p[2])
        if self.debug:
            print(f"GE: {left} >= {right}: {left >= right}")
        return left >= right

    @_('expr_add')
    def expr_comp(self, p):
        return p.expr_add

    @_('expr_add PLUS expr_mult')
    def expr_add(self, p):
        if self.debug:
            print(f"{p[0]} + {p[2]}: {p[0] + p[2]}")
        return p[0] + p[2]

    @_('expr_add MINUS expr_mult')
    def expr_add(self, p):
        if self.debug:
            print(f"{p[0]} - {p[2]}: {p[0] - p[2]}")
        return p[0] - p[2]

    @_('expr_mult')
    def expr_add(self, p):
        return p.expr_mult

    @_('expr_mult MULT expr')
    def expr_mult(self, p):
        if self.debug:
            print(f"{p[0]} * {p[2]}: {p[0] * p[2]}")
        return p[0] * p[2]

    @_('expr_mult DIVIDE expr')
    def expr_mult(self, p):
        if self.debug:
            print(f"{p[0]} / {p[2]}: {p[0] / p[2]}")
        return p[0] / p[2]

    @_('expr_mult REGEX expr')
    def expr_mult(self, p):
        if not isinstance(p[0], str) or \
           not isinstance(p[2], str):
            raise ValueError
        matches = re.search(p[2], p[0])
        retval = matches is not None
        if self.debug:
            print(f"{p[0]} =~ {p[2]}: {retval}")
        return retval

    @_('expr')
    def expr_mult(self, p):
        return p.expr

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return -p.expr

    @_('LPAREN expr_or RPAREN') 
    def expr(self, p):
        if self.debug:
            print(f"({p.expr_or})")
        return p.expr_or

    @_('TYPE2STR expr')
    def expr(self, p):
        try:
            type_name = p[1].__class__.__name__
            if type_name == 'NoneType':
                type_name = 'None'
        except NameError:
            type_name = 'Undefined'
        if self.debug:
            print(f"@{p[1]}: {type_name}")
        return type_name

    @_('term')
    def expr(self, p):
        return p.term

    @_('INT')
    def term(self, p):
        return int(p[0])

    @_('FLOAT')
    def term(self, p):
        return float(p[0])

    @_('KEY')
    def term(self, p):
        keys = p[0].split('.')
        value = self.__json_entry
        for k in keys:
            value = value[k]
        if self.debug:
            print(f"entry[{p[0]}] = {value}")
        return value

    @_('KEY_TEST')
    def term(self, p):
        """
        Treating this as a token is a bit of a hack, but it works...
        """
        key   = p[0]
        key   = key[1:]
        keys  = key.split('.')
        value = self.__json_entry
        for k in keys:
           if not k in value:
               if self.debug:
                   print(f"?entry[{key}] = False")
               #assert False, "KEY: " + pprint.pformat(k) + " VALUE: " + pprint.pformat(value)
               return False
           value = value[k]
        if self.debug:
            print(f"?entry[{key}] = True")
        return True

    @_('STRING')
    def term(self, p):
        return p[0][1:-1]

    @_('BOOL')
    def term(self, p):
        return p[0] == 'True'

    @property
    def json_entry(self):
        return self.__json_entry 

    @json_entry.setter
    def json_entry(self, value):
        self.__json_entry = value

    @property
    def debug(self):
        return self.__debug 

    @debug.setter
    def debug(self, value):
        self.__debug = value


class Parser(object):
  def __init__(self, debug=False):
      self.__lexer  = TestLexer()
      self.__parser = TestParser()
      self.__lexer.debug = debug
      self.__parser.debug = debug
      self.__debug = debug

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
      Convert a value to boolean using explicit rules
      bool_result = False
      if isinstance(value, bool):
          if value == True:
              bool_result = True
      elif isinstance(value, int):
          if value != 0:
              bool_result = True
      elif isinstance(value, float):
          if value != 0.0:
              bool_result = True
      elif isinstance(value, str):
          if value != '':
              bool_result = True
      return bool_result
      """
      return bool(value)

  def exclude_entry(self, entry, exclude_tests):
      """
      Evaluate entry against list of exclude tests.  Returns True
      if it matches, False if it does not.

      *entry*          Dictionary derived from flattened graphql json reply, 
                       Linux command etc.
      *exclude_tests*  Dictionary of tests to run against this entry
      """
      self.parser.json_entry = entry
      matched = False
      rule_number=0
      for item in exclude_tests:
          try:
              tokens = self.lexer.tokenize(item)
              result = self.parser.parse(tokens)
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
          tokens = self.lexer.tokenize(test_entry["test"])
          result = self.parser.parse(tokens)
          if self.debug:
              print(f"{fname}[#{test_index}]: parse({test_entry['test']}) -> RESULT:{result}")
      #except Exception as e:
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

      self.parser.json_entry = entry
      if self.debug:
          print("-------  eval_entry_by_tests: the entry  --------")
          pprint.pprint(self.parser.json_entry)
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


