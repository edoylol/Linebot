import random,string

""" Variable that you can change """
# duration of visit in minute(S)
duration_min = 60
duration_max = 380

# LETS ASUME 1 HOUR = 100 mins....
place_open_time = 700 # let say 7.00
place_close_time = 2300 # let say 23.00

# Determine how fast is a people created (in minutes)
people_enter_every = 2

# Determine the variance of place capacity , later on will be picked randomly from the list
capacity_variance = [300,350,500,650] # this means there's a chance 100person place, 150person place, and so on..
# capacity_variance = [number]    ->> do this if you want to set the capacity to fixed 'number'


""" variable that should not be changed (at least for now) """
places = []
time_list = []
count_visit = [0]*4
count_over = [0]*4


def randname(size=15, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    """ function to generate random string """
    return ''.join(random.choice(chars) for _ in range(size))

def time_pass(list,passed_time):
    for x in list :
        try :
            list[x] = list[x] - passed_time
            if list[x] < 0 :
                list[x] = None
        except :
            pass
    return list


class place :
    def __init__(self):
        self.capacity = random.choice(capacity_variance)
        self.name = randname()

class people :
    def __init__(self):
        self.time = random.randrange(duration_min,duration_max)

""" creating place instance """
a = place()
b = place()
c = place()
d = place()

a_list = [None] * a.capacity
b_list = [None] * b.capacity
c_list = [None] * c.capacity
d_list = [None] * d.capacity

time = place_open_time
while (time >= place_open_time) and (time < place_close_time) : # AS LONG THE PLACE IS OPEN..
    pep = people()  # create people

    dest = random.choice([a_list,b_list,c_list,d_list]) # randomly pick which place to visit..

    if dest == a_list :
        dest_id = 0
    elif dest == b_list :
        dest_id = 1
    elif dest == c_list :
        dest_id = 2
    elif dest == d_list :
        dest_id = 3

    count_visit[dest_id] = count_visit[dest_id] + 1 # counting how many people visit certain place

    """ process of getting people visiting time into a database """
    time_list.append(pep.time)

    """ process of people entering the place and leaving the place (simple algoritm) """

    index_none = -999
    i = 0
    while index_none == (-999) and i in range(0,len(dest)) :
        if dest[i] == None :
            index_none = i
            dest[index_none] = pep.time
        i = i + 1
    if index_none == -999 :
        count_over[dest_id] = count_over[dest_id] + 1

    passed_time = random.randrange(0,people_enter_every)
    dest = time_pass(dest,passed_time)
    time = time + passed_time


""" count all visitors for the day """
count_total = 0
for x in range(0,len(count_visit)) :
    count_total = count_total + count_visit[x]

""" get people visit time average """
average_time = (sum(time_list) / float(len(time_list)))

""" displaying report """
print("Today, we have total of",count_total,"visitors for all 4 places...")
print("Everyone has taken about {0:.2f} minute(s) in one place before leaving".format(average_time))
print()

print("capacity of A (",a.name,") is :", len(a_list), "person")
print("people visited A :", count_visit[0], "times")
print(count_over[0],"people tried to visit A when full...")
print()

print("capacity of B (",b.name,") is :", len(b_list), "person")
print("people visited B :", count_visit[1], "times")
print(count_over[1],"people tried to visit B when full...")
print()

print("capacity of C (",c.name,") is :", len(c_list), "person")
print("people visited C :", count_visit[2], "times")
print(count_over[2],"people tried to visit C when full...")
print()

print("capacity of D (",d.name,") is :", len(d_list), "person")
print("people visited D :", count_visit[3], "times")
print(count_over[3],"people tried to visit D when full...")
print()



