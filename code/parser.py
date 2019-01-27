#! python3

'''
RESULT
'''
class Result:
    def __init__(self, failed, value, message):
        self._failed = failed
        self._message = message
        self._value = value

    def __repr__(self):
        if self._failed:
            return 'Option.error({})'.format(repr(self._message))
        else:
            return 'Option.ok({})'.format(repr(self._value))

    def __str__(self):
        if self._failed:
            return 'Error({})'.format(self._message)
        else:
            return 'Ok({})'.format(self._value)

    def is_ok(self):
        if self._failed:
            return False
        return True

    def is_error(self):
        return not self.is_ok()
    
    def unwrap(self):
        if self.is_ok():
            return self._value
        else:
            raise Exception('This Result is an Error')
    
    def error_msg(self):
        if self.is_error():
            return self._message
        else:
            raise Exception('This Result is Ok')
            
    # function operates on the value in the monad
    def fmap(self, function):
        if self.is_error():
            # self is a Result Monad
            return self
        
        val = self.unwrap()
        # function(val) is a value, so we have to wrap it
        return Result.ok(function(val))
    # bind returns a Result Monad

    # function returns a Result Monad
    def bind(self, function):
        if self.is_error():
            # self is a Result Monad
            return self
        
        val = self.unwrap()
        # function(val) is a Result Monad
        return function(val)
    # bind returns a Result Monad
    
    def recover(self, function):
        if self.is_error():
            return function()
        
        return self
    
    def __rshift__(self, function):
        return self.bind(function)

    @classmethod
    def ok(cls, val):
        return cls(False, val, None)
    
    @classmethod
    def error(cls, msg):
        return cls(True, None, msg)

'''
PARSER
'''

class Parser:
    def __init__(self, function):
        # function takes a string to be parsed and returns a Result Monad
        # holding a tuple, holding (already_parsed_value, remainder_of_string)
        # or an Error
        self._function = function
        
    def __call__(self, text):
        x = self._function(text)
        return x

    def __repr__(self):
        return '<Parsing Combinator>'
            
    # function takes a value, and returns a Result monad holding either the
    # result of that function, or an error message.
    def bind(self, function):
        
        # returned holds a tuple holding
        # (currently matched value, remainder of source text)
        def inner_function(returned):
            match = returned[0]
            remainder = returned[1]
            return (function(match)
                .bind(lambda x: Result.ok((x, remainder))))

        return Parser(lambda text: self(text).bind(inner_function))
    
    def fmap(self, function):
        return self.bind(lambda x: Result.ok(function(x)))
    
    def combine(self, other, function):
        
        def combine_func(match, rest):
            res = other(rest)
            if res.is_ok():
                other_match, rest = res.unwrap()
                new_match = function(match, other_match)
                return Result.ok((new_match, rest))
            else:
                return res
            
        return Parser(lambda text: self(text).bind(lambda res: combine_func(*res)))
    
    def concat(self, other):
        return self.combine(other, lambda x, y: x + y)
    
    def choice(self,other):
        
        def choice_func(text):
            return self(text).recover(lambda: other(text))
        
        return Parser(choice_func)
    
    def many(self, function=lambda x,y: x + y):
        
        def repeat_func(text):
            res = self(text)
            
            if res.is_error():
                return Result.ok(('',text))
            
            match = res.unwrap()[0]
            rest = res.unwrap()[1]
            
            res = self(rest)
            
            while res.is_ok():
                curr, rest = res.unwrap()
                if curr == '':
                    break
                match = function(match, curr)
                res = self(rest)
            
            return Result.ok((match, rest))
            
        return Parser(repeat_func)
    
    def many_list(self):
        
        def repeat_func(text):
            res = self(text)
            
            if res.is_error():
                return Result.ok(('',text))
            
            match = [res.unwrap()[0]]
            rest = res.unwrap()[1]
            
            res = self(rest)
            
            while res.is_ok():
                curr, rest = res.unwrap()
                if curr == '':
                    break
                match = match + [curr]
                res = self(rest)
            
            return Result.ok((match, rest))
            
        return Parser(repeat_func)
        
    def many1(self, function=lambda x,y: x + y):
        return self.combine(self.many(function), function)
    
    def many1_list(self):
        return self.combine(self.many_list(function), function)
    
    def optional(self):
        return self | Parser.empty()
    
    def first(self, other):
        return self.combine(other, lambda x,y: x)
    
    def last(self, other):
        return self.combine(other, lambda x,y: y)
    
    def tuple(self, other):
        return self.combine(other, lambda x,y: (x,y))

    def __rshift__(self, function):
        return self.bind(function)
    
    def __gt__(self, function):
        return self.fmap(function)
    
    def __ge__(self, other):
        return self.last(other)
    
    def __le__(self, other):
        return self.first(other)
        
    def __add__(self, other):
        return self.concat(other)
        
    def __or__(self, other):
        return self.choice(other)

    def __and__(self, other):
        return self.tuple(other)

    @classmethod
    def char(cls, char):

        # char is a single character
        # text is a string
        def match_char(text):
            try:
                current = text[0]
            except IndexError:
                return Result.error('End of String encountered, but ' +
                    '{} is still expected'.format(repr(char)))
            
            if current == char:
                return Result.ok(
                    (text[0],   # the character matched
                     text[1:])  # the remainder of the text
                )
            else:
                return Result.error('Failed to match character {} at {}'
                    .format(repr(char), repr(text)))

        return Parser(match_char)

    @classmethod
    def empty(cls):

        def match_empty(text):
            return Result.ok(('', text))

        return Parser(match_empty)

    @classmethod
    def oneof(cls, charls):

        def match_charls(text):
            #print(charls, text)
            try:
                current = text[0]
            except IndexError:
                return Result.error('End of String encountered, but one of ' +
                '{} is still expected'.format(list(charls)))

            if current in charls:
                return Result.ok((text[0], text[1:]))
            else:
                return Result.error('Failed to match one of {} at {}'
                    .format(list(charls), repr(text)))

        return Parser(match_charls)

    @classmethod
    def noneof(cls, charls):

        def none_charls(text):
            try:
                current = text[0]
            except IndexError:
                return Result.error('End of String encountered, but none of ' +
                '{} is still expected'.format(repr(text)))

            if current not in charls:
                return Result.ok((text[0], text[1:]))
            else:
                return Result.error('Found one of {} at {} '
                    +'when there should be none of'.format(list(charls), repr(text)))

        return Parser(none_charls)

    def parse_prefix(self, string):
        return self(string)

    def parse_total(self, string):
        
        def check_full(tup):
            if tup[1] == '':
                return Result.ok(tup[0])
            else:
                return Result.error('The match did not consist of the entire ' +
                    'string: {} was left over'.format(repr(tup[1])))
            
        return self(string) >> check_full

def result_float(s):
    try:
        i = Result.ok(float(s))
    except Exception:
        i = Result.error("Failed to parse into an float")
    return i

def result_fst(x):
    try:
        return Result.ok(x[0])
    except Exception:
        return Result.error("Failed to get first element")

def result_snd(x):
    try:
        return Result.ok(x[0])
    except Exception:
        return Result.error("Failed to get first element")

digits = Parser.oneof('0123456789').many1()
decimal = (Parser.char('.') + digits).optional()
sign = (Parser.char('+') | Parser.char('-')).optional()
exponent = ((Parser.char('e') | Parser.char('E')) + sign + digits).optional()
number = (sign + digits + decimal + exponent) >> result_float

from enum import Enum, auto

# This is just a basic Enumeration in Python
class Op(Enum):
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIV = auto()

class Expr:
    def __init__(self, expr1, op, expr2):
        self.expr1 = expr1
        self.expr2 = expr2
        
        if op == '+':
            self.op = Op.PLUS
        elif op == '-':
            self.op = Op.MINUS
        elif op == '*':
            self.op = Op.TIMES
        elif op == '/':
            self.op = Op.DIV
        else:
            self.op = op
    
    def __repr__(self):
        return ("Expr({}, {}, {})"
            .format(self.expr1, self.op, self.expr2))

whitespace = Parser.oneof(' \n').many1()

# this function surrounds a parser with optional whitespace
# it takes a parser as an argument, and returns a new parser
def pad(parser):
    return (whitespace.optional() >= parser) <= whitespace.optional()

# we create a bunch of symbols for our parser which
# all can be surrounded by whitespace
openp = pad(Parser.char('('))
closep = pad(Parser.char(')'))

# this function surrounds a parser with a pair of parens
# it takes a parser as an argument, and returns a new parser
def surround(parser):
    return (openp >= parser) <= closep

plus = Parser.char('+')
minus = Parser.char('-')
times = Parser.char('*')
div = Parser.char('/')
operator = pad( plus | minus | times | div )

def expr(text):
    recursive = Parser(expr)
    
    expression = surround(
        (recursive | number)
        & operator
        & (recursive | number)
    )
    
    # things parsed by expression will have the slightly ugly form
    # of Ok(((a,b),c)). To transform that into an Ok(Expr)
    # we will define the following function:
    weird_func = lambda weird_tuple: Expr(
                        weird_tuple[0][0],
                        weird_tuple[0][1],
                        weird_tuple[1]
                    )
    
    full = expression > weird_func
    
    return full(text)

text = '((1+2) * (9 - 11))'

print(Parser(expr).parse_total(text))
