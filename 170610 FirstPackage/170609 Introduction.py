""" First trial on 9 June 2017"""

def LB():
    print("")

""" String introduction """
def StringIntro():
    user = "1234567890"  # assign string to variable
    print(user[0])  # print out first letter
    print(user[1])  # print out second letter
    print(user[-1])  # print out last letter
    print(user[3:8])  # print out fourth - tenth letter
    print(user[:3])  # print out from beginning to the fourth
    print(user[3:])  # print out from the fourth to end

    length = len('aslkdfjasldfkjaslfkja')  # get the lenght of string
    print("the lenght of string is : ", length)

""" List (Array) introduction """
def ListIntro():
    number = [0,1, 2, 3, 4]
    print("printing certain element : ",number[3])             # print out certain element

    number[4] = 22               # set value to certain element
    number = number + [33,44,55] # add sets of values
    print("printing edited list : ",number)

    number.append(88)       # another way to add value
    number[:2] = []         # way to remove value
    print("printing edited list : ", number)

""" Flow Control """
def rightage(age) :
    if age < 30 :
        print("not old enough")
    elif age > 30 :
        print("too old")
    else :
        print("just right")

def rightname(name = 'Ra'):
    if name is 'Ra' :
        print("right name")
    else :
        print("wrongname")

def forloop():
    number = [0,1,2,3,4]
    for num in number :     # iterate all element of  array
        print(num)
    LB()
    for num in number[-3:]:  # iterate limited element of array
        print(num)
    LB()
    for x in range(2, 4):
        print(x)
    LB()


def FlowControl() :
    rightage(3)
    rightage(30)
    rightage(300)
    LB()
    rightname("Ra")
    rightname("dude")
    LB()
    forloop()


rightname("Ra")
rightname("a")
rightname()




