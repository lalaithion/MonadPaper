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
            
    def bind(self, function):
        if self.is_error():
            return self
        
        val = self.unwrap()
        return function(val)
        
    def fmap(self, function):
        if self.is_error():
            return self
            
        val = self.unwrap()
        return Result.ok(function(val))
    
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
        self._function = function
        
    def __call__(self, text):
        x = self._function(text)
        return x

    def __repr__(self):
        return '<Parsing Combinator>'
            
    def bind(self, function):
        
        print(function)
        
        def bind_func(result):
            return function(result[0]).bind(lambda x: Result.ok((x, result[1])))

        return Parser(lambda text: self(text).bind(bind_func))
    
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
    def char(cls, val):

        def match_char(text):
            print(val, text)
            try:
                current = text[0]
            except IndexError:
                return Result.error('End of String encountered, but ' +
                    '{} is still expected'.format(repr(val)))
            
            if current == val:
                return Result.ok((text[0], text[1:]))
            else:
                return Result.error('Failed to match character {} at {}'
                    .format(repr(val), repr(text)))

        return Parser(match_char)

    @classmethod
    def empty(cls):

        def match_empty(text):
            return Result.ok(('', text))

        return Parser(match_empty)

    @classmethod
    def oneof(cls, charls):

        def match_charls(text):
            print(charls, text)
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

'''
Writing Code
'''
'''
def result_int(s):
    try:
        i = Result.ok(int(s))
    except Exception:
        i = Result.error("Failed to parse into an integer")
    return i

text = 'aaaabcabc_______'
print(text)
parser = (Parser.char('a').many() + Parser.char('b') + Parser.char('c'))
print(parser)
result = Parser.parse_prefix(parser, text)
print(result)
'''


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
#
#print(Parser.parse_total(number, '-12'))
#print(Parser.parse_total(number, '12e10'))
#print(Parser.parse_total(number, '2.12345e+100'))
#print(Parser.parse_total(number, 'hello world'))
#print(Parser.parse_total(number, '99 bottles of beer on the wall'))
#print(Parser.parse_total(number, ''))
#
#def result_float(x):
#    try:
#        return Result.ok(float(x))
#    except Exception:
#        return Result.error('Failed to cast to a float')
#
#whitespace = Parser.oneof(' \n').many1()
#many_numbers = (
#        (whitespace.optional() >= number)
#    ).many_list()
#
#text = '2.12345e+100 2.1e10 1223 13.5 100e100'
#print(Parser.parse_total(many_numbers, text))
## Ok(([2.12345e+100, 21000000000.0, 1223.0, 13.5, 1e+102], ''))
#
#expression = Parser.noneof(',\n').many1()
#comma = Parser.char(',')
#newline = Parser.char('\n')
#line = (expression <= comma.optional()).many_list()
#csv = ((line <= newline)).many_list()
#
#text = '''1,2,3,8,5
#hello world, my, good, friends, 5
#0,1,2,3,4
#'''
#print(Parser.parse_total(csv, text))
#
#from collections import namedtuple
#from enum import Enum, auto
#
#class Op(Enum):
#    PLUS = auto()
#    MINUS = auto()
#    TIMES = auto()
#    DIV = auto()
#
#Expr = namedtuple('Expr', ['Op','e1','e2'])
#
#openp = Parser.char('(') + whitespace.optional()
#closep = whitespace.optional() + Parser.char(')')
#plus = whitespace.optional() + Parser.char('+') + whitespace.optional()
#minus = whitespace.optional() + Parser.char('-') + whitespace.optional()
#times = whitespace.optional() + Parser.char('*') + whitespace.optional()
#div = whitespace.optional() + Parser.char('/') + whitespace.optional()
#
#Plus = lambda x: Expr(Op.PLUS, x[0], x[1])
#Minus = lambda x: Expr(Op.MINUS, x[0], x[1])
#Times = lambda x: Expr(Op.TIMES, x[0], x[1])
#Div = lambda x: Expr(Op.DIV, x[0], x[1])
#
#def expr(text):
#    recursive_plus = ((openp >= Parser(expr)) & (plus >= Parser(expr))) <= closep
#    recursive_minus = ((openp >= Parser(expr)) & (minus >= Parser(expr))) <= closep
#    recursive_times = ((openp >= Parser(expr)) & (times >= Parser(expr))) <= closep
#    recursive_div = ((openp >= Parser(expr)) & (div >= Parser(expr))) <= closep
#
#    full = (
#                (recursive_plus > Plus)
#                | (recursive_minus > Minus)
#                | (recursive_times > Times)
#                | (recursive_div > Div)
#                | number
#           )
#
#    return full(text)
#
#text = '((1+2) * (9 - 11))'
#
#print(Parser(expr).parse_total(text))
## Ok(
##     Expr(
##         Op=<Op.TIMES: 3>,
##         e1=Expr(
##             Op=<Op.PLUS: 1>,
##             e1=1.0,
##             e2=2.0
##         ),
##         e2=Expr(
##             Op=<Op.MINUS: 2>,
##             e1=9.0,
##             e2=11.0
##         )
##     )
## )
## Here is a function that matches any character
#
#def any_char(text):
#    if len(text) == 0:
#        return Result.error("The text is too short"
#                            " to contain any character")
#    else:
#        return Result.ok((text[0], text[1:]))
#
#any_char_parser = Parser(any_char).fmap(ord)
#
#print(any_char_parser('hello'))
#print(any_char_parser('hello'))
## Result.Ok(('h','ello'))
#
#


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
#

#print(Parser(expr).parse_total(text))

loop = Parser.char('hi').optional().optional()

#print(loop("hi"))

def bad_recursion(text):
    
    bad = Parser(bad_recursion)
    final = bad + Parser.char('a')
    
    return final(text)

bad_parser = Parser(bad_recursion)

print(bad_parser('a'))
