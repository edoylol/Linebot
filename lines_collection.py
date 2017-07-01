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

    def invite(self,cond):
        if cond == "header" : #  % sender
            lines = ["Konichiwa, %s invite you to : ",
                     "Nee,, %s invite you to : ",
                     "Konichiwa,, you got invitation from %s : ",
                     "Nee,,you got invitation from %s : ",
                     "Sumimasen,, you got invitation from %s : "
                    ]
        elif cond == "success" :
            lines = ["Done,, %s invitations sent ^^ ",
                     "Invitations sent, Megumi has delivered %s invitation",
                     "Megumi has delivered your invitation to %s participant",
                     "Done,, Megumi has sent your invitation to %s person",
                     "Megumi report : %s invitations sent successfully"
                     ]

        elif cond == "failed" :
            lines = ["Gomenne, seems I can't send the invitation..",
                     "Seems something wrong about the invitation, wanna check it once more time ?",
                     "Megumi can't send your invitation right now.. sorry..",
                     "Hmm.. I wonder why I can't send your invitation though...",
                     "Gomen, please try to send the invitation again.."
                     ]
        return random.choice(lines)

    def invite_report(self,cond):
        if cond == "respond recorded" :
            lines = ["Thanks for your response %s, Megumi will pass it right now ~",
                     "OK %s..Megumi will let (him/her) know...",
                     "I see.. thanks for your response %s ..",
                     "Thanks %s,, Megumi will tell (him/her) ASAP ^^",
                     "Kay %s, I will let (him/her) know.."
                    ]
        elif cond == "desc missing" :
            lines = ["I think the description is missing...",
                     "Megumi will still send the invitation, even though there is no description..",
                     "Try to add description next time ,kay ? ^^ ",
                     "If you want to add description next time, just surround description with (*)",
                     "It's ok not having description, but it would be better to have it."
                     ]
        elif cond == "participant list missing":
            lines = ["I think the participant list is missing...",
                     "Megumi will still send to dev list, since there is no participant list..",
                     "Try to add participant list next time ,kay ? ^^ \n(sent to dev list) ",
                     "If you want to add participant list next time, just use 'to participant_list'",
                     "If there is no participant list, it will be sent to dev list."
                     ]
        elif cond == "yes" : #  % responder
            lines = ["About the invitation, %s said that (he/she) will come..",
                     "About the invitation, %s said 'OK'",
                     "About the invitation, %s confirmed 'OK'",
                     "About the invitation, %s said 'sure~'",
                     "About the invitation, I think %s said 'OK'"
                     ]
        elif cond == "no" :
            lines = ["About the invitation, %s said sorry that (he/she) can't go..",
                     "About the invitation, %s rejected the offer",
                     "About the invitation, %s declined the offer",
                     "About the invitation, %s said 'maybe later'",
                     "About the invitation, I think %s said that (he/she) can't fulfill the request"
                    ]

        elif cond == "pending" :
            lines = ["About the invitation, %s is still thinking whether going or not",
                     "About the invitation, %s will contact you later..",
                     "About the invitation, %s is unsure about that invitation outcome",
                     "About the invitation, %s can't guarantee (his/her) approval",
                     "About the invitation, %s said that (he/she) will think about it"
                    ]
        return random.choice(lines)

    def show_cinema_movie_schedule(self,cond):
        if cond == "header" : # accept 1 % tag list

            lines = ["Here's the information Megumi found while using '%s' as tag..\n",
                     "I tried using '%s' as tag, and found those...\n",
                     "Here's the information you requested ^^\n(using '%s' as tag)\n",
                     "Here you go~ \nMegumi used '%s' as search tag btw..\n",
                     "Here's the schedule I found with '%s' as tag..\n"
                     ]
        elif cond == "cinema name" : # accept 1 % cinema name

            lines = [" ♦♦  %s  ♦♦ \n",
                     "(・ω・) %s (・ω・)\n",
                     " ❤❤   %s   ❤❤ \n",
                     " ~~~   %s   ~~~ \n",
                     " >>>   %s   <<< \n"
                     ]
        elif cond == "No cinema found" : # accept 1 % tag list

            lines = ["No cinema is found :<  \nI tried to search using '%s' as tag",
                     "Somehow Megumi can't find cinema with '%s' name..",
                     "There's no cinema under '%s' name..",
                     "I think you should try again using tag other than '%s'..",
                     "I can't figure out which cinema with '%s' ",
                     "Megumi can't find the cinema you requested (%s)..",
                     "I don't see any cinema by searching using '%s' :< "
                     ]
        elif cond == "Too many cinemas" : # accept 1 % tag list

            lines = ["I found too many cinemas with '%s' as tag",
                     "There're too many cinemas \n with '%s' as tag",
                     "Try using more specific tags than '%s', there're too many cinemas..",
                     "I can't figure out which cinema with '%s'\nThere're too many of them...",
                     "Be specific please,, there're tons of cinemas with '%s'"
                     ]
        elif cond == "No keyword found" :

            lines = ["Megumi can't find without keyword.. .-.",
                     "Please specify which cinema :> ",
                     "Did you include keyword already ? I don't see those..",
                     "Which cinema do you want ?",
                     "There're a lot of cinemas, which one ?"
                     ]
        elif cond == "failed to open the the page" :

            lines = ["Megumi seems can't open the page..",
                     "Something wrong happened when I tried to open the page..",
                     "Gomen, Megumi can't give you the schedule right now..",
                     "Gomen, Megumi failed to open the the page..",
                     "Seems Megumi can't access the information right now.."
                     ]
        elif cond == "failed to show movie data" :

            lines = ["Gomen, Megumi failed to gather movies data",
                     "Seems I can't show the schedule..",
                     "Gomenne, somehow I can't show the schedule..",
                     "Gomenne, there's some problem when I want to show the schedule..",
                     "I've gathered the schedule, but I can't send it to you right now ..",
                     ]
        elif cond == "footer" :

            lines = [" ♦ ＼(＾∀＾)  end   (＾∀＾)ノ ♦ ",
                     " Hope you enjoy the show later ~",
                     " (=^ ◡ ^=) end 	(=^ ◡ ^=)",
                     " (＾• ω •＾) enjoy the show ~ ",
                     "      ヾ(・ω・)メ(・ω・)ノ    ",
                     ]
        elif cond == "asking to show cinema list" :

            lines = ["Wanna see the cinema list ?",
                     "Nee,, wanna see the cinema list ?",
                     "Let's take a look at the cinema list :> ",
                     "How about seeing the cinema list ? ",
                     "I have the cinema list, wanna see ?",
                     ]
        elif cond == "show cinema list" :

            lines = ["Here you go..  \n",
                     "These are the cinemas I could find ~\n",
                     "Pick the cinemas from the list below kay ? :> \n",
                     "Try to add some of this name into search next time ^^\n",
                     "These are the cinema list you requested..\n",
                     ]
        elif cond == "specify the company" :

            lines = ["Does it have CGV or XXI ? I don't remember...\n(Try to add either 'cgv' or 'xxi')",
                     "Is it CGV ? or maybe XXI ? I'm not sure...\n(Try to add either 'cgv' or 'xxi')",
                     "Which cinema list is it? CGV or XXI ? \n(Try to add either 'cgv' or 'xxi')",
                     "Which cinema list should I search from?\n(Try to add either 'cgv' or 'xxi')",
                     "Gomen,, please specify which cinema do you want me to search for..\n(Try to add either 'cgv' or 'xxi')",
                     ]
        return random.choice(lines)

    def wiki_search(self,cond):
        if cond == "page not found" : # takes 2 % (language, keyword)
            lines = ["I think %s wikipedia does not have an article about '%s' ... ",
                     "Gomen, I tried to search %s wikipedia, but I can't find '%s' ",
                     "%s wikipedia doesn't has '%s' titled page I think...",
                     "I don't see any pages on %s wikipedia titled '%s'...",
                     "Seems %s wikipedia doesn't have information about '%s'..."]
        elif cond == "try different keyword / language":
            lines = ["How bout trying different keyword / language ? \n\nJust in case you need it..",
                     "How bout trying other keyword / language ? \n\nHere's the wiki list, just in case..",
                     "Wanna try other keyword? or maybe language? \n\nI will put it here, just in case..",
                     "How about trying other language ? \n\nHere's the list of wikipedia you can pick..",
                     "Maybe try other keyword / language ? \n\nJust in case you need it btw,.. ",
                     "\nJust in case you need wiki list... ",
                     ]
        elif cond == "no keyword found" :
            lines = ["What do you want me to search for ? ",
                     "Gomen, what was that ? ",
                     "Gomen, say it again please ? what was that ? ",
                     "Gomen, what do you want me to search for ?",
                     "Gomen, what did you ask just now ?",
                     "Sorry, I missed the thing you asked just now.. ",
                     "Please say it again what I should be looking for...",
                     "Pardon, what do you want me to look for ? "]
        elif cond == "has disambiguation" :
            lines = ["FYI, this keyword has other uses...\n",
                     "Just saying, this keyword has other uses..\n",
                     "This keyword has other uses\n",
                     "This keyword has other disambiguation choices\n",
                     "This page is auto-redirected, there are other disambiguation..\n",
                     "FYI, there are other disambiguation available...\n",
                     "Just saying, this keyword has other meaning as well..\n",
                     "FYI, this keyword has other meaning as well.. \n"]
        elif cond == "not specific page - header" :
            lines = ["Seems '%s' is not a specific keyword,..",
                     "I think there are a lot different uses of '%s'..",
                     "I can't determine which '%s' you are looking for...",
                     "I'm not sure which is the appropriate answer for '%s' ",
                     "There are a lot of '%s' ,,"
                     ]
        elif cond == "not specific page - content" :
            lines = ["Here's the list of '%s' people usually search for : \n",
                     "These are some common uses of '%s'...\n",
                     "How about pick one from the list of '%s' below ? \n",
                     "I found some common uses of '%s', how about pick one ? \n",
                     "I wonder if '%s' you looking for is listed below... \n"
                     ]
        elif cond == "ask detail info" :
            lines = ["Wanna see more detailed info ?",
                     "Nee,, wanna see the detailed page ?",
                     "Do you want to see the full page ?  ",
                     "Take a look at the original page ? ",
                     "I also have the full page, wanna see ?",
                     ]

        return random.choice(lines)

    def download_youtube(self,cond):
        if cond == "page not found" :
            lines = ["Are you sure you include the youtube link correctly ?",
                     "I can't find the link you want to download...",
                     "Seems the page is unavailable...",
                     "I can't find the youtube page you requested..",
                     "The youtube page is unavailable, I think..."]
        elif cond == "no video found" :
            lines = ["There's no video with that format...",
                     "I don't see any video available to download...",
                     "Seems this video doesn't meet the requested format..",
                     "Seems this video is not available in that format..",
                     "I can't find any video to download...try other format(?) "]
        elif cond == "gathering video data failed" :
            lines = ["The page is so slow, I can't gather any data...",
                     "Gomen, seems the video download data corrupted..",
                     "Gomen, the video data is so unresponsive...",
                     "Seems something missing from the video download data, making it's unavailable",
                     "I can't gather the data you requested, seems something wrong..."]
        elif cond == "pick one to download" :
            lines = ["Here's the list of available video(s) ",
                     "Pick one form the list below ,kay ? ^^",
                     "Here you go :> ",
                     "Choose one to download...",
                     "Which one do you want ? .."]
        elif cond == "send option header" :
            lines = ["I found some videos with %s",
                     "Here are some videos with %s",
                     "Those videos passed %s as filter",
                     "I tried to filter with %s and these are the result..",
                     "I tried to use %s as filter, and found those..."]
        elif cond == "header" :
            lines = ["This is the list of available formats...\n",
                     "Try to include one of the format next time...\n",
                     "These are the available formats... \n",
                     "Why did you make such a wide filtering ? Try to narrow it down..\n",
                     "I wonder which one do you want...\n"]
        elif cond == "footer" :
            lines = ["\n ♦ ＼(＾∀＾)  end   (＾∀＾)ノ ♦ ",
                     "\n Hope you find the one you want ~",
                     "\n (=^ ◡ ^=) end 	(=^ ◡ ^=)",
                     "\n \(＾• ω •＾) found it ?  ",
                     "\n      ヾ(・ω・)メ(・ω・)ノ    ",
                     ]
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
            lines = [" Nyaann~ Thanks for adding me ^^ \nhope we can be friend!",
                     " Thanks for inviting Megumi :3 ",
                     " Yoroshiku onegaishimasu~ ^^ ",
                     " Megumi desu ! \nyoroshiku nee ~ ^^",
                     " Megumi desu, you can call me kato or meg aswell.. \nhope we can be friends~ :> ",
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



    def added(self,cond):
        if cond == "added" :
            lines = [" Nyaann~ Thanks for adding me %s ^^ \nhope we can be friend !",
                     " Thanks for adding Megumi :3 \nHope we can be friend, %s ^^",
                     " Konichiwa %s,.. Megumi desu~ \nYoroshiku onegaishimasu \(^.^)/ ",
                     " Megumi desu ! \nyoroshiku nee %s ~ ^^",
                     " Megumi desu, you can call me kato or meg aswell.. \nhope we can be friends %s ~ :> ",
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

    def dev_mode_set_tag_notifier(self,cond):
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

    def dev_mode_userlist(self,cond):
        if cond == "print userlist success" :
            lines = ["Print success, %d new entries recorded.\nDon't forget to print until 0 updates ^^ ~ ",
                     "Roger master,, %d new entries has been recorded.",
                     "Done..., don't forget to copy these %d new entries",
                     "Ryokai ^^.,,, just don't forget to copy these %d new entries later, kay ? ",
                     "Sure master.., there are %d new entries recorded FYI..."
                     ]

        elif cond == "print userlist failed" :
            lines = ["Gomenne master, seems Megumi can't access the userlist... ",
                     "Gomen master, there's some errors Megumi can't handle when printing the userlist",
                     "Gomenne master, I don't know why but Megumi can't do that...",
                     "Gomen master, the userlist seems can't be printed out in the logs.. I wonder why...",
                     "Hmm... seems Megumi can't do that now.. how about try again ?"
                     ]

        elif cond == "userlist not updated yet":
            lines = ["Gomenne master, I think the userlist hasn't changed yet... ",
                     "Gomen master, Megumi just printed the same userlist before...",
                     "Gomenne master, I don't think you have to print it again...",
                     "Gomen master, the userlist seems same as before...",
                     "Hmm... are you sure want to print the same list ? \nHow about try again later ?"
                     ]

        elif cond == "notify update userlist" :
            lines = ["Master, I think there're %d updates on userlist,,",
                     "Master, userlist has %d updates, how about updating now ?",
                     "The userlist has %d updates, wanna update now ?",
                     "%d entries on userlist, should I update now?",
                     "Let's update the userlist master.. %d new entries"
                     ]

        return random.choice(lines)

    def dev_mode_authority_check(self,cond):
        if cond == "failed" :
            lines = ["Megumi can't enter Dev Mode now, try again later..",
                     "Megumi can't verify your id, so I can't grant you access..",
                     "Seems Megumi can't grant you access now..",
                     "Try calling dev mode once again.. seems some error occurred...",
                     "Megumi can't verify your id, please try again later..",
                     ]

        elif cond == "reject" :
            lines = ["Gomenne,,Megumi can't grant you access for that..",
                     "Do not try to access dev mode.. you are not allowed to !",
                     "Gomen,, you are not allowed to do that..",
                     "Gomen, your request has been rejected.",
                     "Megumi does not allow you to enter dev mode !",
                     "Gomenne,,Megumi can't do that for you..",
                     "Gomenne,,Megumi is told not to give you access..",
                     "Gomen,,Megumi does not recognize you as developer..."
                     ]

        elif cond == "notify report" :
            lines = ["Master, %s is trying to enter dev mode...",
                     "Be careful master, %s is trying to enter dev mode... ",
                     "Be careful master, %s has tried to enter dev mode just now.",
                     "Master, just now %s tried to enter dev mode.",
                     "Nee mastah, %s tried to enter dev mode. ",
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

class Labels: # more like my response template
    def confirmation(self,cond):
        if cond == "yes" :
            lines = ["Sure,,",
                     "Yes please..",
                     "Ok..",
                     "Yeah,..",
                     "Why not...",
                     "Sure Kato..",
                     ]

        elif cond == "no" :
            lines = ["Nope..",
                     "Not now..",
                     "Don't do it..",
                     "Better not",
                     "No..",
                     "Later..",
                     ]
        return random.choice(lines)

    def print_userlist(self):
        lines = ["Sure,,print it out",
                 "Go ahead..",
                 "Go ahead Megumi..",
                 "Yes please Megumi..",
                 "Ok Megumi..",
                 "Yeah, do it Megumi..",
                 "Do it Megumi..",
                 "Sure Kato..",
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

class Picture :
    def header(self,cond):
        if cond == "background" :
            pic = ["https://il2.picdn.net/shutterstock/videos/1974016/thumb/1.jpg",
                   "https://static.videezy.com/system/resources/thumbnails/000/005/037/small/Abstract_Blur_4K_Motion_Background_Loop.jpg",
                   "https://static.videezy.com/system/resources/thumbnails/000/004/941/small/jellyfish-4k-living-background.jpg",
                   "https://static.videezy.com/system/resources/thumbnails/000/005/030/small/silk-4k-wedding-background.jpg",
                   "https://static.videezy.com/system/resources/thumbnails/000/005/045/small/Blurry_Vision_4K_Motion_Background_Loop.jpg",
                   "https://il2.picdn.net/shutterstock/videos/15516307/thumb/1.jpg",
                   "https://static.videezy.com/system/resources/thumbnails/000/005/038/small/Alive_4K_Motion_Background_Loop.jpg",
                   "https://static.videezy.com/system/resources/thumbnails/000/005/042/small/Beautiful_Slide_4K_Motion_Background_Loop.jpg",
                   "https://static.videezy.com/system/resources/thumbnails/000/005/615/small/abstract-blue-bokeh-b-roll-4k-stock-video.jpg",
                   "https://static.videezy.com/system/resources/thumbnails/000/006/812/small/colorful-bokeh.jpg"
                   ]
        return random.choice(pic)