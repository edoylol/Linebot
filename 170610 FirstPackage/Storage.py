import random,time,string


def LB():
    print("")

def rand(min=1,max=5):
    a = random.randrange(min, max+1)
    b = random.randrange(min, max+1)
    c = random.randrange(min, max+1)
    d = random.randrange(min, max+1)
    e = random.randrange(min, max+1)

    rand = random.choice([a,b,c,d,e])
    return rand

def checkrand(min=1,max=5):
    count = [0]*(max-min+2)
    for i in range(1,5000):
        num = rand(min,max)
        count[num-min] = count[num-min] + 1
    for k in range(min,max+1):
        print (k,"appeared",count[k-min],"times")

def randname(size=26, chars = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    """ function to generate random string """
    return ''.join(random.choice(chars) for _ in range(size))

def delayrandom():
    time.sleep(rand())

def setfile(filename="temp",func='a'):
    file = open((str(filename)+'.txt'),str(func))
    return file

def readfile(filename="temp"):
    file = setfile(filename,'r')
    print(file.read())
    file.close()

def remove_symbols(word):
    symbols = "1234567890!@#$%^&*()_+=-`~[]{]\|;:'/?.>,<\""
    for i in range(0,len(symbols)):
        word = word.replace(symbols[i],"")      #strong syntax to remove symbols
    if len(word) > 0 :
        return word

