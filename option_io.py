#! python3

'''
THE OPTION MONAD
'''

class OptionException(Exception):
    pass

class Option:
    def __init__(self, failed, value):
        self._failed = failed
        self._value = value

    def __repr__(self):
        if self._failed:
            return 'Option.none()'
        else:
            return 'Option.some({})'.format(self._value)

    def __str__(self):
        if self._failed:
            return 'None'
        else:
            return 'Some({})'.format(self._value)

    def is_some(self):
        if self._failed:
            return False
        return True

    def is_none(self):
        return not self.is_some()
    
    def unwrap(self):
        if self._failed:
            raise OptionException('This Option has no value')
        else:
            return self._value
            
    def bind(self, function):
        if self.is_none():
            return type(self).none()
        
        val = self.unwrap()
        return function(val)
    
    def __or__(self, function):
        return self.bind(function)

    @classmethod
    def some(cls, x):
        return cls(False, x)
    
    @classmethod
    def none(cls):
        return cls(True, None)


def option_open(filename, mode='r'):
    try:
        fd = Option.some(open(filename, mode=mode))
    except Exception:
        fd = Option.none()
    return fd

def option_read(fd, size=-1):
    try:
        data = Option.some(fd.read(size))
    except Exception:
        data = Option.none()
    return data

import re

def option_match(pattern, string):
    match = re.match(pattern, string)
    if match:
        return Option.some(match)
    else:
        return Option.none()

def option_get_group(match, group):
    try:
        g = match.group(group)
    except Exception:
        g = None

    if g == None:
        return Option.none()
    else:
        return Option.some(g)

def option_int(s):
    try:
        i = Option.some(int(s))
    except Exception:
        i = Option.none()
    return i


result = (Option.some('text.txt') | option_open | option_read | (lambda x: option_match(r'\s*(\S*)', x)) | (lambda x: option_get_group(x, 1)) | option_int)
print(result)
