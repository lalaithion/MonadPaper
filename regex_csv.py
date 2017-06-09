#! python3

import re

from collections import namedtuple
from enum import Enum, auto

num = r'(\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?'
plus = r'\s*\+\s*'
minus = r'\s*-\s*'
times = r'\s*\*\s*'
div = r'\s*/\s*'

class Op(Enum):
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIV = auto()

Expr = namedtuple('Expr', ['Op','e1','e2'])

def parse_expr(text):
    first = re.match(num, text)
    print(text, first)
    if first:
        rest = text[first.end():]
        return float(first.group(0)), rest
    else:
        if text[0] == '(':
            amount = 0
            endi = None
            
            for index in range(len(text)):
                if text[index] == ')':
                    amount -= 1
                elif text[index] == '(':
                    amount += 1

                if amount == 0:
                    endi = index
                    break
            
            if endi is None:
                raise Exception
            
            return parse(text[1:endi]), text[endi+1:]
        else:
            raise Exception
    

def parse(text):
    first, rest = parse_expr(text)
    
    print(first, rest)
    
    opre = [plus, minus, times, div]
    opsy = [Op.PLUS, Op.MINUS, Op.TIMES, Op.DIV]
    ops = zip(opre, opsy)
    
    operation = None
    
    for regex, symbol in ops:
        match = re.match(regex, rest)
        if match:
            rest = rest[match.end():]
            operation = symbol
            break
    
    if operation is None:
        raise Exception
        
    print(operation)
    print(rest)
    
    last, leftover = parse_expr(rest)
    
    return Expr(operation, first, last)

text = '(1+2) * (9 - ())'

print(parse(text))
