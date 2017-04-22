#! python3

'''
ERROR HANDLING WITHOUT MONADS
'''

def division(x, y):
    if y == 0:
        return None
    return x / y

def index(ls, i):
    if i < 0 or i >= len(ls):
        return True, None
    return False, ls[i]

def divide_elements(ls, i1, i2):
    failure, v1 = index(ls, i1)
    if failure:
        return None
    
    failure, v2 = index(ls, i2)
    if failure:
        return None
    
    return division(v1, v2)

def divide_elements(ls, i1, i2):
    try:
        return ls[i1]/ls[i2]
    except (IndexError, ZeroDivisionError):
        return None
        
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

    @classmethod
    def some(cls, x):
        return cls(False, x)
    
    @classmethod
    def none(cls):
        return cls(True, None)


'''
ERROR HANDLING WITH MONADS
'''

def division(x, y):
    if y == 0:
        return Option.none()
    return Option.some(x / y)

def index(ls, i):
    if i < 0 or i >= len(ls):
        return Option.none()
    return Option.some(ls[i])

def divide_elements(ls, i1, i2):
    res1 = index(ls, i1)
    res2 = index(ls, i2)
    
    partial = lambda x: lambda y: division(x,y)
    
    return res2.bind(res1.bind(partial))

print(divide_elements([1,2,3,0],1,2))


'''
OTHER EXAMPLE
'''

def index(ls, i):
    if i < 0 or i >= len(ls):
        return True, None
    return False, ls[i]

def follow(ls, i):
    failed, val = index(ls, i)
    while not failed:
        i = val
        failed, val = index(ls, i)
    return i

def index(ls, i):
    if i < 0 or i >= len(ls):
        return Option.none()
    return Option.some(ls[i])

def follow(ls, i):
    val = Option.some(i)
    while val.is_some():
        i = val
        val = i.bind(index)
    return i.unwrap()
