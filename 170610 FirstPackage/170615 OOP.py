from Storage import *

class Enemy:

    def __init__(self):
        self.name = randname()
        self.attack = rand(1,3)*rand(1,6)*rand(7,10)*rand(11,15)
        self.defense = rand(1,3)*rand(1,6)*rand(7,10)*rand(11,15)
        self.hp = rand(1,3)*rand(1,6)*rand(7,10)*rand(11,15)*rand(20,25)
        self.setstar()
        print(self.name,"created")

    def setstar(self):
        total_stat = self.attack*self.defense*self.hp/10000000
        print(total_stat)
        star = 0
        while total_stat > 0 :
            star = star + 1
            total_stat = total_stat // 10
        self.star = star
        return self.star

    def checkstat(self):
        print("name :",self.name)
        print("star :",self.star)
        print("atk :", self.attack)
        print("def :", self.defense)
        print("hp :", self.hp)


mushroom = Enemy()