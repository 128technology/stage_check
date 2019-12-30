###############################################################################
#   _____      ____                                      
#  | ____|_  _|  _ \ __ _ _ __ ___  ___ _ __ _ __  _   _ 
#  |  _| \ \/ / |_) / _` | '__/ __|/ _ \ '__| '_ \| | | |
#  | |___ >  <|  __/ (_| | |  \__ \  __/ | _| |_) | |_| |
#  |_____/_/\_\_|   \__,_|_|  |___/\___|_|(_) .__/ \__, |
#                                           |_|    |___/ 
#
# A general purpose expression parser using sly (LEX / YACC) to build up
# a customizable parse tree for later processing. This module has been
# abstracted from stage_check processsing in the event if proves useful
# for other scenarios.
#
###############################################################################
import pprint
import sly

###############################################################################
#
# Parser Token Base classes. The code which includes this module must 
# create a subclass which has a process method for each node (failure to
# do so will not prevent the parse tree from being constructed, but it
# will raise an exception when the parse tree is processed).
#
# e.g:
# class UMINUS(ExParser.Expr):
#   def __init__(self, expr1):
#      super().__init__(expr1)
#
#   def proc(self):
#      return -(self.expr1.proc())
#
#
###############################################################################
class Expr:
    debug = False

    def __init__(self, expr1):
        self.expr1 = expr1
         
    @property
    def debug(self):
        return SingleExpr.debug

    @debug.setter
    def debug(self, value):
        if not isinstance(value, bool):
            raise TypeError
        Expr.debug = value

    def proc(self):
        raise TypeError

class Expr2(Expr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1)
        self.expr2 = expr2



###############################################################################
#
# The Lexer / Tokenizer
#
###############################################################################

class LexerError(Exception):
    """
    Raised when Lexer token extraction error occurs 
    w/o debug enabled...
    """
    pass

class Lexer(sly.Lexer):
    # Set of token names.   This is always required
    tokens = { INT, FLOAT, KEY, STRING, BOOL,
               TYPE2STR, DEFINED, NOT,
               PLUS, MINUS, MULT, DIVIDE, REGEX, MODULO,
               EQ, LT, LE, GT, GE, NE, 
               OR, AND}

    literals = { '(', ')', '\'' }

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
    TYPE2STR = r'@'
    DEFINED  = r'\?'
    NOT      = r'!'

    @_(r'\d+')
    def INT(self, t):
        t.value = int(t.value)
        return t

    # Identifiers and keywords
    FLOAT     = r'[0-9]+\.[0-9]+'
    INT       = r'[0-9]+'
    KEY       = r'[a-zA-Z0-9]+([\.\/_-]+[a-zA-Z0-9]+)*'
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

###############################################################################
#
#  YACC-based python parser for stage_check expressions.
#
#  This has been altered to produce a parse tree rather than
#  evaluating expressions as they are parsed.  Separating
#  parsing from evaluation allows for the 'or' and 'and' operators
#  to skip evaluating the sceond expression when the first expression
#  evaluates to a value that makes the second expression irrelevent.
#  
#
###############################################################################
class Parser(sly.Parser):
    """
    When embedding the evaluation into the parsing, it is not 
    possible to skip logical operand values which are meaningless
    because even though evaluation may not be required, they still
    must be visited for parsing.

    For example, we'd like to be able to say 
    @variable && variable == 1
    where variable == 1 never gets evaluated if @variable is False
    (@variable returns True if the variable is defined or False
    otherwise)

    To do this correctly, it is necessary to parse the expression
    into an expression tree, which evaluates the parse tree, and
    is able to skip anything after False && ...  or a True || ... 
    expressions

    To use the Parser class, a treeModule must first be loaded. 
    """
    # Get the token list from the lexer (required)
    tokens = Lexer.tokens

    precedence = (
       ('left', OR),
       ('left', AND),
       ('nonassoc',  EQ, NE, LT, GT, LE, GE, REGEX),
       ('left', PLUS, MINUS),
       ('left', MULT, DIVIDE, MODULO),
       ('right', NOT),
       ('right', TYPE2STR),
       ('right', DEFINED),
       ('right', UMINUS)
    )

    tokenClasses = {
       'UMINUS'   : Expr,
       'DEFINED'  : Expr,
       'TYPE2STR' : Expr,
       'EQ'       : Expr2,
       'NE'       : Expr2,
       'LT'       : Expr2,
       'GT'       : Expr2,
       'LE'       : Expr2,
       'GE'       : Expr2,
       'MINUS'    : Expr2,
       'PLUS'     : Expr2,
       'MULT'     : Expr2,
       'DIVIDE'   : Expr2,
       'MODULO'   : Expr2,
       'AND'      : Expr2, 
       'OR'       : Expr2,
       'PARENS'   : Expr,
       'KEY'      : Expr,
       'STRING'   : Expr,
       'FLOAT'    : Expr,
       'INT'      : Expr,
       'BOOL'     : Expr, 
       'REGEX'    : Expr2,
       'NOT'      : Expr
    }

    # The AND class should only evaluate the second 
    # expression if required to get a result
    @_('expr AND expr')
    def expr(self, p):
        cls = self.get_token_class('AND')
        return cls(p.expr0, p.expr1)

    # The OR class should only evaluate the second 
    # expression if required to get a result
    @_('expr OR expr')
    def expr(self, p):
        cls = self.get_token_class('OR')
        return cls(p.expr0, p.expr1)

    @_('expr EQ expr')
    def expr(self, p):
        cls = self.get_token_class('EQ')
        return cls(p.expr0, p.expr1)

    @_('expr NE expr')
    def expr(self, p):
        cls = self.get_token_class('NE')
        return cls(p.expr0, p.expr1)

    @_('expr GT expr')
    def expr(self, p):
        cls = self.get_token_class('GT')
        return cls(p.expr0, p.expr1)

    @_('expr LT expr')
    def expr(self, p):
        cls = self.get_token_class('LT')
        return cls(p.expr0, p.expr1)

    @_('expr GE expr')
    def expr(self, p):
        cls = self.get_token_class('GE')
        return cls(p.expr0, p.expr1)

    @_('expr LE expr')
    def expr(self, p):
        cls = self.get_token_class('LE')
        return cls(p.expr0, p.expr1)

    @_('expr REGEX expr')
    def expr(self, p):
        cls = self.get_token_class('REGEX')
        return cls(p.expr0, p.expr1)

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        cls = self.get_token_class('UMINUS')
        return cls(p.expr)

    @_('TYPE2STR expr')
    def expr(self, p):
        cls = self.get_token_class('TYPE2STR')
        return cls(p.expr)

    @_('DEFINED expr')
    def expr(self, p):
        cls = self.get_token_class('DEFINED')
        return cls(p.expr)

    @_('NOT expr')
    def expr(self, p):
        cls = self.get_token_class('NOT')
        return cls(p.expr)

    @_('expr MINUS expr')
    def expr(self, p):
        cls = self.get_token_class('MINUS')
        return cls(p.expr0, p.expr1)

    @_('expr PLUS expr')
    def expr(self, p):
        cls = self.get_token_class('PLUS')
        return cls(p.expr0, p.expr1)

    @_('expr MULT expr')
    def expr(self, p):
        cls = self.get_token_class('MULT')
        return cls(p.expr0, p.expr1)

    @_('expr DIVIDE expr')
    def expr(self, p):
        cls = self.get_token_class('DIVIDE')
        return cls(p.expr0, p.expr1)

    @_('expr MODULO expr')
    def expr(self, p):
        cls = self.get_token_class('MODULO')
        return cls(p.expr0, p.expr1)

    # The PARENS class should evaluate to itself
    @_('"(" expr ")"')
    def expr(self, p):
        cls = self.get_token_class('PARENS')
        return cls(p.expr)

    # The NUMBER class should cast the result to an int
    @_('INT')
    def expr(self, p):
        cls = self.get_token_class('INT')
        return cls(p.INT)

    # The KEY class should evaluate to storage[key]
    @_('KEY')
    def expr(self, p):
        cls = self.get_token_class('KEY')
        return cls(p.KEY)

    # The FLOAT class expression should be cast to a float
    @_('FLOAT')
    def expr(self, p):
        cls = self.get_token_class('FLOAT')
        return cls(p.FLOAT)

    # The BOOL class expression should be cast to a bool
    @_('BOOL')
    def expr(self, p):
        cls = self.get_token_class('BOOL')
        return cls(p.BOOL)

    # The STRING class expression should be stripped of 
    # enclosing ''s
    @_('STRING')
    def expr(self, p):
        cls = self.get_token_class('STRING')
        return cls(p.STRING)

    def set_class_map(
        self,
        class_map
    ):
        """
        It is not easy to inherit from the sly.Parser class, so the parse tree classes
        to be used are passed as a map
        """
        for key in Parser.tokenClasses:
            if not key in class_map:
                raise ValueError(f"Key {key} missing from map...")
            # TODO check for class types (i.e. do they inherit from what 
            # they should inherit from...
            found_base = False
            dbg = []
            bases = type.mro(class_map[key])
            for base in bases:
                basename = base.__module__ + '.' + base.__name__
                compname = __name__ + '.' + Parser.tokenClasses[key].__name__
                dbg.append(f"{basename} == {compname}")
                if compname == basename:
                     found_base = True
                     break
            if not found_base:
                string = '\n'.join(dbg)
                assert False, f"{string}"
        self.classMap = class_map

    def get_token_class(self, key):
        try:
            return self.classMap[key]
        except (AttributeError, NameError, KeyError) as e:
            return Parser.tokenClasses[key]

    def tokens_with_no_class(self):
        result = []
        for key in Parser.tokenClasses:
            try:
                if not key in self.classMap:
                    result.append(key)
            except (NameError, AttributeError) as e:
                result.append(key)
        return result   
   
