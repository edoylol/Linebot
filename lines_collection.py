import random
import time
import math

class Lines:  # class to store respond lines
    """=================== Main Function Lines Storage ======================="""

    def rand_int(self):
        lines = ["I think I will pick %s",
                 "How about %s ?",
                 "%s I guess ?",
                 "Let's try %s",
                 "%s ?",
                 "I think %s ?"]
        return random.choice(lines)

    def echo(self):
        lines = ["%s",
                 "%s :v",
                 "wutt... \n\nbut whatever,,, \"%s\" ahahah",
                 "no xD ! #pfft \n\n\nJK JK okay... \n\"%s\" xD",
                 "... \n\n\n\n\n\"%s\",, I guess (?)",
                 "hee... %s",
                 "\"%s\",, is that good ?",
                 "I don't understand, but \"%s\""]
        return random.choice(lines)

    def choose_one(self,cond):
        if cond == "success" :
            lines = ["I think I will choose %s",
                     "How about %s ?",
                     "%s I guess (?)",
                     "Maybe %s (?)",
                     "%s (?)",
                     "I think %s (?)",
                     "%s then..",
                     "I prefer %s I think.."]

        if cond == "fail" :
            lines = ["Try to add '#' before the item, like #this or #that",
                     "I'm sorry, but please add '#' before the item",
                     "Gomen,, I didn't catch that...",
                     "Gomen,, what do you want me to choose ? ",
                     "Gomen,, I can only choose from item with '#' .. ",
                     ]
        return random.choice(lines)

    def time(self,hh,mm,AmPm):
        lines = ["It's %s:%s %s" % (hh,mm,AmPm), #It's 12:24 Am
                 "About %s:%s %s" % (hh,mm,AmPm), #About 12:24 Am
                 "%s:%s :>" % (hh,mm), # 12:24 :>
                 "It's %s:%s right now.." % (hh,mm), #It's 12:24 right now..
                 "Almost %s:%s,," % (hh,mm) ]#Almost 12:24,,
        return random.choice(lines)

    def date(self,day, DD, MM, YYYY):
        ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])
        lines = ["It's %s, %s %s, %s" % (day, MM, DD, YYYY),  # It's Tuesday, June 16, 2017
                 "It's %s of %s" % (ordinal(int(DD)), MM),  # It's 16th of June
                 "%s %s, %s" % (MM, DD, YYYY),  # June 16, 2017
                 "Today is %s,%s %s" % (day, ordinal(int(DD)), MM),  # Today is Tuesday, 16th June
                 "Today's date is %s" % DD,  # Today's date is 16
                 "I think it's %s %s" % (MM, DD)]  # I think it's June 16
        return random.choice(lines)


    def notyetcreated(self):
        lines = ["Gomen,, this function is not ready..",
                 "Gomen,, please try again later :)",
                 "Gomen,, I can't do that yet :\">",
                 "Gomen,, this function is under maintenance :< ",
                 "Gomen,, please try ask me others",
                 "Gomen,, I'm still learning this..",
                 "Gomen,, He hasn't taught me about this yet",
                 "Gomen,, I don't understand this yet.., but I wish I could help :)"]
        return random.choice(lines)

    def report_bug(self,cond):
        if cond == "success":
            lines = ["Thank you for your report :>",
                     "Arigatoo... wish me luck to fix this problem :\")",
                     "Arigatoo, I'll let master know about this",
                     "Arigatoo, I'll tell master later ~",
                     "Sankyu for your feedback :)",
                     "Gomenne, hope I can fix this soon...\nthanks for the report btw :)",
                     "Gomenne,.. thanks for the feedback though ^^",
                     ]
        elif cond == "fail":
            lines = ["Gomen,, try to send it again..",
                     "Gomen,, master is busy fixing other stuff :'> ",
                     "Gomenne,, seems report function is not working properly ...",
                     "Gomenne,, please try to tell master by personal chat .. ",
                     "Gomen,, can you repeat the report please ? .. :'> ",
                     "Gomen,, I'm still learning how to report stuff... :'> ",
                     ]
        elif cond == "report":
            lines = ['Master, here is the report... : \n\n"%s" \n\nSubmitted by : %s',
                     'Master, I think there are some problems... : \n\n"%s" \n\nSubmitted by : %s',
                     'Master, I\'ve got you a report :3 \n\n"%s" \n\nSubmitted by : %s',
                     'Master, please take a look at this... : \n\n"%s" \n\nSubmitted by : %s',
                     'Master, how should I solve this ? \n\n"%s" \n\nSubmitted by : %s',
                     'Master, please fix this :3 \n\n"%s" \n\nSubmitted by : %s',
                     'Master, try to fix this owkay ?? :3 \n\n"%s" \n\nSubmitted by : %s',
                     'Master, seems something is not working properly.. : \n\n"%s" \n\nSubmitted by : %s']

        return random.choice(lines)


    def join(self,cond):

        if cond == "join" :
            lines = [" Nyaann~ Thanks for adding me ^^ \n hope we can be friend!",
                     " Thanks for inviting Megumi :3 ",
                     " Yoroshiku onegaishimasu~ ^^ ",
                     " Megumi desu ! \n yoroshiku nee ~ ^^",
                     " Megumi desu, you can call me kato or meg aswell.. \n hope we can be friends~ :> ",
                     " Megumi desu, just call me kato or meg  ^^,, \nyoroshiku nee ~ ",
                     " Konichiwa... Megumi desu ! ehehehe",
                     " Supp xD .. Megumi desu :3 ,, \nyoroshiku nee~  #teehee"]

        elif cond == "report" :
            lines = ["Master, Megumi joined a group ~ :> " ,
                     "Master, I'm leaving for a while ,kay? ^^ ",
                     "Master, I got invitation to join a group..",
                     "Master, I'm going to a group ,kay? :3 ",
                     "Master, Wish me luck ,, Megumi joined a group #teehee ^^ ",
                     ]

        return random.choice(lines)

    def leave(self,cond):
        if cond == "leave" :
            lines = ['“To say goodbye is to die a little.” \n― Raymond Chandler',
                     '“I don\'t know when we\'ll see each other again or what the world will be like when we do.\nI will think of you every time I need to be reminded that there is beauty and goodness in the world.” \n― Arthur Golden',
                     'One day in some far off place, I will recognize your face, I won\'t say goodbye my friend, For you and I will meet again',
                     '“Something or someone is always waving goodbye.”\n― Marty Rubin ',
                     'Even if we walk on different paths, one must always live on as you are able! You must never treat your own life as something insignificant! You must never forget the friends you love for as long as you live! Let bloom the flowers of light within your hearts.',
                     'Smile. Not for anyone else, but for yourself. Show yourself your own smile. You\'ll feel better then.',
                     'No matter what painful things happens, even when it looks like you\'ll lose... when no one else in the world believes in you... when you don\'t even believe in yourself... I will believe in you!',
                     'I\'ll always be by your side. You\'ll never be alone. You have as many hopes as there are stars that light up the sky.'
                     ]

        elif cond == "regards" :
            lines = ["See you later my friend.., bye~ \n\n              ~ Megumi ~",
                     'Wish you guys very best in everything.., bye~ \n\n              ~ Megumi ~',
                     'I hope this is not the end of us :> , bye~ \n\n              ~ Megumi ~',
                     'Try adding me sometimes okay ? :> I will wait for it.. bye for now !\n\n              ~ Megumi ~',
                     'Hope can see you again in the future ^^ .. , bye ~\n\n              ~ Megumi ~'
                     ]

        elif cond == "report" :
            lines = ['Master, I\'m done with a group :> \n\n%s : %s',
                     'Master, I have left a group... xD \n\n%s : %s',
                     'Master, Megumi has returned from a group :3 \n\n%s : %s',
                     'Master, I think I\'ve been kick out from a group :"> \n\n%s : %s',
                     'Master, Can you invite me into the group again ? \n\n%s : %s',
                     ]

        else :
            lines = ["I can't leave... it's not a group or room .-. ",
                     'I think you mistaken this for group (?) xD',
                     'C\'mon, this is private chat xD',
                     'This is not group lol.. xD',
                     'I can only leave group and room, even though I don\'t want to TBH'
                     ]
        return random.choice(lines)


    def false(self):
        lines = ["Gomen,, what was that ?",
                 "Are you calling me ?",
                 "Hmm ? ",
                 "I wonder what is that",
                 "Maybe you should try to call 'megumi help' (?)",
                 "hmmm... I wonder what is that",
                 " .-. ? ",
                 " what ?? ._. "]
        return random.choice(lines)

    def tag_notifier(self):
        lines = ['Master, I think %s is calling you.. \n\n"%s"',
                 '%s is calling you master.. \n\n"%s"',
                 'Master, I think your name is being called by %s..\n\n"%s"',
                 'Master,.. tag message from %s \n\n"%s"',
                 'Check this out .. %s tagged you \n\n"%s"',
                 ]
        return random.choice(lines)

    def set_tag_notifier(self,cond):
        if cond == "on" :
            lines = ["OK, I will tell you if someone tag you master ~",
                     "Tag notifier is on active mode :> ",
                     "Sure, I will notify you",
                     "Roger..",
                     "Done.., itterasai :3 ~"]

        elif cond == "off" :
            lines = ["Okaeri.. :3",
                     "OK, welcome back ~",
                     "Roger.. :3 ",
                     "Done,, Tag notifier is off now..",
                     "Sure,, glad to see you again.."]

        elif cond == "same" :
            lines = ["Hmm.. seems nothing changed...",
                     "Hmm.. try to do it one more time.. ^^ \nsometimes it takes more than once",
                     "I don't see any difference though...",
                     "Please try again until it's changed ^^,,\nsometimes it takes more than once "]

        else :
            lines = ["Gomen, I don't catch that.. :/",
                     "Hmm.. try to do it one more time.. ^^",
                     "Gomen, seems notifier setting is failed...",
                     "I think you gave wrong instruction (?) xD"]
        return random.choice(lines)

    def added(self,cond):
        if cond == "added" :
            lines = [" Nyaann~ Thanks for adding me %s ^^ \n hope we can be friend !",
                     " Thanks for adding Megumi :3 \nHope we can be friend, %s ^^",
                     " Konichiwa %s,.. Megumi desu~ \nYoroshiku onegaishimasu \(^.^)/ ",
                     " Megumi desu ! \n yoroshiku nee %s ~ ^^",
                     " Megumi desu, you can call me kato or meg aswell.. \n hope we can be friends %s ~ :> ",
                     " Megumi desu, just call me kato or meg  ^^,, \nyoroshiku nee %s ~ ",
                     " Konichiwa %s... Megumi desu ! ehehehe",
                     " Megumi desu :3 ,, \nyoroshiku nee %s-chan ~  #teehee"
                     ]

        elif cond == "report" :
            lines = ["Master, Megumi got a new friend named %s ~ ^^",
                     "Master, %s added Megumi as a friend ~ YAY ^^",
                     "Master, do you know %s ? he/she added me.. ",
                     "Master, %s just added me ^^ ",
                     "Look master, Megumi got a new friend : %s",
                     "Nee mastah,, %s added me o(>ω<)o ",
                     ]
        return random.choice(lines)

    def removed(self,cond):
        if cond == "removed" :
            lines = ['“To say goodbye is to die a little.” \n― Raymond Chandler',
                     '“I don\'t know when we\'ll see each other again or what the world will be like when we do.\nI will think of you every time I need to be reminded that there is beauty and goodness in the world.” \n― Arthur Golden',
                     'One day in some far off place, I will recognize your face, I won\'t say goodbye my friend, For you and I will meet again',
                     '“Something or someone is always waving goodbye.”\n― Marty Rubin ',
                     'Even if we walk on different paths, one must always live on as you are able! You must never treat your own life as something insignificant! You must never forget the friends you love for as long as you live! Let bloom the flowers of light within your hearts.',
                     'Smile. Not for anyone else, but for yourself. Show yourself your own smile. You\'ll feel better then.',
                     'No matter what painful things happens, even when it looks like you\'ll lose... when no one else in the world believes in you... when you don\'t even believe in yourself... I will believe in you!',
                     'I\'ll always be by your side. You\'ll never be alone. You have as many hopes as there are stars that light up the sky.'
                     ]

        elif cond == "regards" :
            lines = ["See you later %s.., bye~ \n\n              ~ Megumi ~",
                     'Wish you very best in everything.., bye %s ... \n\n              ~ Megumi ~',
                     'I hope this is not the end of us :> , bye %s ... \n\n              ~ Megumi ~',
                     'Nee %s, play with me again OK ? :> I will wait for you.. \n\n              ~ Megumi ~',
                     'Thanks for playing with me until now %s... , bye ~\n\n              ~ Megumi ~'
                     ]

        elif cond == "report" :
            lines = ["Master, seems %s blocked me ...",
                     "Megumi just lost a friend... %s - chan left me...",
                     "Gomenne master,, seems %s don't want to play with me anymore...",
                     "Nee mastah,, can you ask %s to add me again ? ",
                     "Master, gomenne.. %s blocked me I guess...Megumi wasn't a very good girl"
                     ]

        return random.choice(lines)


    def template(self):
        lines = ["",
                 "",
                 "",
                 "",
                 "",
                 "",
                 "",
                 ""]
        return random.choice(lines)

    def template_cond(self,cond):
        if cond == "a" :
            lines = ["",
                     "",
                     "",
                     "",
                     "",
                     "",
                     "",
                     ""]

        else :
            lines = ["",
                     "",
                     "",
                     "",
                     "",
                     "",
                     "",
                     ""]
        return random.choice(lines)

    """=================== some extra Lines Storage ======================="""

    def megumi(self):
        return ['megumi', 'kato', 'meg', 'megumi,', 'kato,', 'meg,']

    def jessin(self):
        return ['jessin','jes','@jessin d','jess','jssin',]

    def day(self):
        return {'Mon' : 'Monday' ,
                "Tue" : "Tuesday" ,
                "Wed" : "Wednesday",
                "Thu" : "Thursday",
                "Fri" : "Friday",
                "Sat" : "Saturday",
                "Sun" : "Sunday"}

    def month(self):
        return {'jan' : 'January',
                'feb' : 'February',
                'mar' : 'March',
                'apr' : 'April',
                'may' : 'May',
                'jun' : 'June',
                'jul' : 'July',
                'aug' : 'August',
                'sep' : 'September',
                'oct' : 'October',
                'nov' : 'November',
                'dec' : 'December'}

