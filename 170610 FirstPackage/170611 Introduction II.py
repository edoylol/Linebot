""" 11 June 2017 """

import Storage,random

def add_num(*args):
    sum = 0
    for a in args :
        sum = sum + a
    print (sum)

def setstest():
    # array that can't have duplicate value
    numbers = {3, 5 ,2 ,3 ,2,33,22}
    print(numbers)

def dictionarytest(name):
    # dictionary can only contain key-value data
    dragon = {'Ra' : 'The pioneer', 'Luna' : 'Moon dragon' , 'Dialga' : 'Time controler'}
    if name in dragon :
        print(name,dragon[name])
    elif name is 'all' :
        print("list of dragon : ")
        for k,v in dragon.items() :
            print (k)
    else :
        print ("name not found")

def rng(a,b):
    print(random.randrange(a, b))


""" flexible amount of arguments & unpacking arguments """
numbers = [3, 5 ,2 ,3 ,2,33,22]
add_num(3, 5 ,2 ,3 ,2,33,22)
add_num(*numbers)

Storage.LB()

""" Set and Dictionary """
setstest()
Storage.LB()
dictionarytest('all')
Storage.LB()
dictionarytest('Luna')
Storage.LB()

""" import module """
rng(2, 280)

