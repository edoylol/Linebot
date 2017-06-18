import random

def delay():
    a = random.randrange(1,8)
    b = random.randrange(1,8)
    c = random.randrange(1,8)
    d = random.randrange(1,8)
    e = random.randrange(1,8)
    rand = random.choice([a,b,c,d,e])
    return rand


