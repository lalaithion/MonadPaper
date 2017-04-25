# python has a built in function, 'map' that does this.
def fmap(ls, function):
    new = []
    for item in ls:
        new.append(function(item))
    return new

# this is sometimes called 'flatten'
def join(ls):
    new = []
    for sublist in ls:
        for item in sublist:
            new.append(item)
    return new

def bind(ls, function):
    return join(fmap(ls, function))
    
def less_than_abs(x):
    if x == 0:
        return []
    ls = [0]
    for i in range(1,x):
        ls.append(i)
        ls.append(-i)
    return ls

from math import sqrt

def sqrts(x):
    if x < 0:
        return []
    elif x == 0:
        return [0]
    else:
        return [sqrt(x), -sqrt(x)]

print(bind(less_than_abs(3), sqrts))
