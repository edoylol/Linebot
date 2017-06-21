# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import os
import sys
import random
import time
import math

from argparse import ArgumentParser
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError,
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    LeaveEvent, JoinEvent, UnfollowEvent, FollowEvent,
    SourceGroup, SourceRoom, SourceUser
)

app = Flask(__name__)

# Megumi chat bot (note : remove the whitespace )

# channel_secret = '9d1e7500a205ddaec1c6f2ae0d190e6e'
# channel_access_token = 'f/jBF6+aFLuvzEmI0NbPNWjfrsK3Kjwxzzl1XUeLun+3uRs6AbDEQGphezyssudufYiyiHBoLQWWjEBqTtV00P0jLOJuV
#                         lrEQly/Xjo7ZQXY0YMEoKm869aWpCnu9Jhog4zt4nb4DYB4zVMWApdjCQdB04t89/1O/w1cDnyilFU='


channel_secret = "9b665635f2f8e005e0e9eed13ef18124"
channel_access_token = "ksxtpzGYTb1Nmbgx8Nj8hhkUR5ZueNWdBSziqVlJ2fPNblYeXV7/52HWvey/MhXjgtbml0LFuwQHpJHCP6jN7W0gaKZVUOlA88AS5x58IhqzLZ4Qt91cV8DhXztok9yyBQKAOSxh/uli4cP4lj+2YQdB04t89/1O/w1cDnyilFU="
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

tag_notifier_on = True



@app.route("/callback", methods=['POST'])
def callback():  # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
def get_receiver_addr(event):
    global address
    if isinstance(event.source, SourceGroup):
        try:
            address = event.source.group_id
        except:
            address = event.source.user_id
    elif isinstance(event.source, SourceRoom):
        try:
            address = event.source.room_id
        except:
            address = event.source.user_id
    else :
        address = event.source.user_id
    return address


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    global token, original_text, text, jessin_userid, tag_notifier_on

    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"
    original_text = event.message.text
    text = original_text.lower()
    token = event.reply_token
    get_receiver_addr(event)


    if any(word in text for word in Lines.megumi()):

        if "say " in text : Function.echo()
        elif all(word in text for word in ["pick ","num"])          : Function.rand_int()
        elif any(word in text for word in ["choose ","which one"])  : Function.choose_one_simple()

        elif any(word in text for word in ["what ","show "])        :
            if any(word in text for word in ["date","time","day"])      : Function.time_date()
            else                                                        : Function.false()

        elif any(word in text for word in ["turn ","able"])         :
            if any(word in text for word in ["tag notifier",
                                             "notif", "mention"])       : Function.set_tag_notifier("set")
            else                                                        : Function.false()

        elif "command4 " in text                                    : Function.notyetcreated()
        elif "command5 " in text                                    : Function.notyetcreated()

        elif any(word in text for word in ["please leave, megumi"]) : Function.leave(event)
        elif all(word in text for word in ["report","bug"])         : Function.report_bug(event)
        else                                                        : Function.false()

    # special tag / mention function
    if tag_notifier_on :
        if any(word in text for word in Lines.jessin()):
            Function.tag_notifier(event)

@handler.add(JoinEvent)
def handle_join(event):
    global token,jessin_userid
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"
    token = event.reply_token
    get_receiver_addr(event)

    Function.join()


"""===================================  List of Usable Function & Class ============================================"""


class Function:
    """====================== Main Function List ==========================="""

    def rand_int():

        def random_number(min=1, max=5):
            # just in case
            if min > max :
                temp = min
                min = max
                max = temp

            a = random.randrange(min, max+1)
            b = random.randrange(min, max+1)
            c = random.randrange(min, max+1)
            d = random.randrange(min, max+1)
            e = random.randrange(min, max+1)

            return random.choice([a,b,c,d,e])

        split_text = text.split(" ")
        found_num = []
        for word in split_text:
            try:
                found_num.append(int(word))
            except:
                continue
        try :
            result = random_number(found_num[0],found_num[1])
            reply = Lines.rand_int() % str(result)
        except :
            reply = "Seems something wrong, try again maybe ?"

        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def echo():
        try :
            start_index = text.find("say ")+4
            reply = Lines.echo() % str(original_text[start_index:])
        except :
            reply = "What should I say?"

        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def choose_one():
        split_text = text.replace(",", " , ").split(" ")
        found_options = []
        cursor = 0
        for word in split_text:
            # print(word)
            if word == "or":
                # get the previous and after 'or' :
                try:
                    if split_text[cursor - 1] != "" and len(split_text[cursor - 1]) >= 2:
                        found_options.append(split_text[cursor - 1])
                    if split_text[cursor + 1] != "" and len(split_text[cursor + 1]) >= 2:
                        found_options.append(split_text[cursor + 1])
                except:
                    pass

                # check for natural language just in case people use comma, TBH not really important ...

                coloniterate = cursor - 2
                for i in range(0, 4):  # check back 3 times
                    try:
                        if split_text[coloniterate - i] == ",":
                            for j in range(1, 4):
                                try:
                                    if coloniterate - i - j >= 0:
                                        if split_text[coloniterate - i - j] != "" and len(
                                                split_text[coloniterate - i - j]) >= 2:
                                            found_options.append(split_text[coloniterate - i - j])
                                            break
                                except:
                                    pass
                    except:
                        pass

                # natural language check end here for each loop ~

            cursor = cursor + 1

        avoid_list = ['megumi', 'kato', 'meg', 'choose', 'or', 'and', ',', ' ']
        found_options = list(set(found_options) - set(avoid_list))
        try :
            result = random.choice(found_options)
            reply = Lines.choose_one() % str(result)
        except :
            reply = " Oops, something wrong... I don't see anything to pick.."
        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def choose_one_simple():
        split_text = text.split(" ")
        found_options = []
        for word in split_text:
            if '#' in word:
                try:
                    word = OtherUtil.remove_symbols(word)
                    found_options.append(word)
                except:
                    pass
        try :
            result = random.choice(found_options)
            reply = Lines.choose_one() % str(result)
        except :
            reply = "Try to add '#' before the item, like #this or #that"

        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def time_date():
        def find_GMT():
            split_text = text.split(" ")
            GMT_found_index = 0
            for word in split_text:
                GMT_found_index += 1
                if word.upper() == "GMT":
                    try:
                        for i in range(0, 5):
                            try:
                                GMT = int(split_text[GMT_found_index + i])
                            except:
                                pass
                        GMT = int(GMT)
                    except:
                        GMT = 0
            try:
                GMT = int(GMT)  # if still can't find requested GMT
            except:
                GMT = 7  # default GMT+7
            return GMT
        def valid_GMT(GMT):
            if (GMT > 12) or (GMT < (-12)):
                return False
            else :
                return True
        if valid_GMT(find_GMT()):
            try:
                GMT = find_GMT()
                split_time = time.ctime(time.time()+GMT*3600).split(" ")
                splitted_hour = split_time[3].split(":")
                day = Lines.day()[split_time[0]]
                MM = Lines.month()[split_time[1].lower()]
                DD = split_time[2]
                YYYY = split_time[4]
                hh = splitted_hour[0]
                mm = splitted_hour[1]
                ss = splitted_hour[2]

                if any(word in text for word in ["date","day"]):
                    reply = Lines.date(day, DD, MM, YYYY)
                elif "time" in text:
                    AmPm = "Am"
                    if int(hh) > 12:
                        hh = int(hh)
                        hh -= 12
                        hh = str(hh)
                        AmPm = "Pm"
                    reply = Lines.time(hh, mm, AmPm)
            except:
                reply = "Seems I can't get the date or time, I wonder why..."

        else : # happen when GMT is not valid
            reply = "I think the timezone is a little bit off... should be between -12 to 12 isn't ??"

        line_bot_api.reply_message(token, TextSendMessage(text=reply))



    def report_bug(event):

        try:
            try :
                sender = line_bot_api.get_profile(event.source.user_id).display_name
            except :
                sender = "Anonymous"
            report = Lines.report_note() % (original_text,sender)
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))
            reply = Lines.report_bug("success")

        except:
            reply = Lines.report_bug("fail")
        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def join():

        reply = Lines.join()
        line_bot_api.reply_message(token, TextSendMessage(text=reply))
        report = Lines.join_note()
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def leave(event):

        if isinstance(event.source, SourceGroup):
            group_id = event.source.group_id

            reply = Lines.leave("leave")
            line_bot_api.push_message(group_id, TextSendMessage(text=reply))

            reply = Lines.leave("regards")
            line_bot_api.reply_message(token, TextSendMessage(text=reply))

            report = Lines.leave_note() % ('Group', group_id)
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

            line_bot_api.leave_group(group_id)

        elif isinstance(event.source, SourceRoom):
            room_id = event.source.room_id

            reply = Lines.leave("leave")
            line_bot_api.push_message(room_id, TextSendMessage(text=reply))

            reply = Lines.leave("regards")
            line_bot_api.reply_message(token, TextSendMessage(text=reply))

            report = Lines.leave_note() % ('Chatroom', room_id)
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

            line_bot_api.leave_room(room_id)

        else:
            reply = Lines.leave("fail")
            line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def set_tag_notifier(cond="pass"):
        global tag_notifier_on , tag_notifier_conf
        if cond == "set":
            if any(word in text for word in ["on ", "enable "]):
                if tag_notifier_on is not True :
                    tag_notifier_on = True
                    reply = Lines.set_tag_notifier("on")
                else:  # already True
                    reply = Lines.set_tag_notifier("same")

            elif any(word in text for word in ["off ", "disable "]):
                if tag_notifier_on is True :
                    tag_notifier_on = False
                    reply = Lines.set_tag_notifier("off")
                else:  # already False
                    reply = Lines.set_tag_notifier("same")

            else:
                reply = Lines.set_tag_notifier("fail")
                pass

            line_bot_api.reply_message(token, TextSendMessage(text=reply))

        elif cond == "pass":
            pass
            print("func passed")

        print("current status : ", tag_notifier_on)

    def tag_notifier(event):
        try :
            sender = line_bot_api.get_profile(event.source.user_id).display_name
        except :
            sender = "someone"
        report = Lines.tag_notifier() % (sender,original_text)
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def notyetcreated():
        reply = Lines.notyetcreated()
        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def false():
        reply = Lines.false()
        line_bot_api.reply_message(token, TextSendMessage(text=reply))


class Lines:  # class to store respond lines
    """=================== Main Function Lines Storage ======================="""

    def rand_int():
        lines = ["I think I will pick %s",
                 "How about %s ?",
                 "%s I guess ?",
                 "Let's try %s",
                 "%s ?",
                 "I think %s ?"]
        return random.choice(lines)

    def echo():
        lines = ["%s",
                 "%s :v",
                 "wutt... \n\nbut whatever,,, \"%s\" ahahah",
                 "no xD ! #pfft \n\n\nJK JK okay... \n\"%s\" xD",
                 "... \n\n\n\n\n\"%s\",, I guess (?)",
                 "hee... %s",
                 "\"%s\",, is that good ?",
                 "I don't understand, but \"%s\""]
        return random.choice(lines)

    def choose_one():
        lines = ["I think I will choose %s",
                 "How about %s ?",
                 "%s I guess (?)",
                 "Maybe %s (?)",
                 "%s (?)",
                 "I think %s (?)",
                 "%s then..",
                 "I prefer %s I think.."]
        return random.choice(lines)

    def time(hh,mm,AmPm):
        lines = ["It's %s:%s %s" % (hh,mm,AmPm), #It's 12:24 Am
                 "About %s:%s %s" % (hh,mm,AmPm), #About 12:24 Am
                 "%s:%s :>" % (hh,mm), # 12:24 :>
                 "It's %s:%s right now.." % (hh,mm), #It's 12:24 right now..
                 "Almost %s:%s,," % (hh,mm) ]#Almost 12:24,,
        return random.choice(lines)

    def date(day, DD, MM, YYYY):
        ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])
        lines = ["It's %s, %s %s, %s" % (day, MM, DD, YYYY),  # It's Tuesday, June 16, 2017
                 "It's %s of %s" % (ordinal(int(DD)), MM),  # It's 16th of June
                 "%s %s, %s" % (MM, DD, YYYY),  # June 16, 2017
                 "Today is %s,%s %s" % (day, ordinal(int(DD)), MM),  # Today is Tuesday, 16th June
                 "Today's date is %s" % DD,  # Today's date is 16
                 "I think it's %s %s" % (MM, DD)]  # I think it's June 16
        return random.choice(lines)


    def notyetcreated():
        lines = ["Gomen,, this function is not ready..",
                 "Gomen,, please try again later :)",
                 "Gomen,, I can't do that yet :\">",
                 "Gomen,, this function is under maintenance :< ",
                 "Gomen,, please try ask me others",
                 "Gomen,, I'm still learning this..",
                 "Gomen,, He hasn't taught me about this yet",
                 "Gomen,, I don't understand this yet.., but I wish I could help :)"]
        return random.choice(lines)

    def report_bug(cond):
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
        return random.choice(lines)

    def report_note():
        lines = ['Master, here is the report... : \n\n"%s" \n\nSubmitted by : %s',
                 'Master, I think there are some problems... : \n\n"%s" \n\nSubmitted by : %s',
                 'Master, I\'ve got you a report :3 \n\n"%s" \n\nSubmitted by : %s',
                 'Master, please take a look at this... : \n\n"%s" \n\nSubmitted by : %s',
                 'Master, how should I solve this ? \n\n"%s" \n\nSubmitted by : %s',
                 'Master, please fix this :3 \n\n"%s" \n\nSubmitted by : %s',
                 'Master, try to fix this owkay ?? :3 \n\n"%s" \n\nSubmitted by : %s',
                 'Master, seems something is not working properly.. : \n\n"%s" \n\nSubmitted by : %s']
        return random.choice(lines)

    def join():
        lines = [" Nyaann~ Thanks for adding me ^^ \n hope we can be friends!",
                 " Thanks for inviting Megumi :3 ",
                 " Yoroshiku onegaishimasu~ ^^ ",
                 " Megumi desu ! \n yoroshiku nee ~ ^^",
                 " Megumi desu, you can call me kato or meg aswell.. \n hope we can be friends~ :> ",
                 " Megumi desu, just call me kato or meg  ^^,, \nyoroshiku nee ~ ",
                 " Konichiwa... Megumi desu ! ehehehe",
                 " Supp xD .. Megumi desu :3 ,, \nyoroshiku nee~  #teehee"]
        return random.choice(lines)

    def join_note():
        lines = ["Master, Megumi joined a group ~ :> " ,
                 "Master, I'm leaving for a while ,kay? ^^ ",
                 "Master, I got invitation to join a group..",
                 "Master, I'm going to a group ,kay? :3 ",
                 "Master, Wish me luck ,, Megumi joined a group #teehee ^^ ",
                 ]
        return random.choice(lines)

    def leave(cond = "leave"):
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
            return random.choice(lines)
        elif cond == "regards" :
            lines = ["See you later my friend.., bye~ \n\n              ~ Megumi ~",
                     'Wish you guys very best in everything.., bye~ \n\n              ~ Megumi ~',
                     'I hope this is not the end of us :> , bye~ \n\n              ~ Megumi ~',
                     'Try adding me sometimes okay ? :> I will wait for it.. bye for now !\n\n              ~ Megumi ~',
                     'Hope can see you again in the future ^^ .. , bye ~\n\n              ~ Megumi ~'
                     ]
            return random.choice(lines)
        else :
            lines = ["I can't leave... it's not a group or room .-. ",
                     'I think you mistaken this for group (?) xD',
                     'C\'mon, this is private chat xD',
                     'This is not group lol.. xD',
                     'I can only leave group and room, even though I don\'t want to TBH'
                     ]
            return random.choice(lines)

    def leave_note():
        lines = ['Master, I\'m done with a group :> \n\n%s : %s',
                 'Master, I have left a group... xD \n\n%s : %s',
                 'Master, Megumi has returned from a group :3 \n\n%s : %s',
                 'Master, I think I\'ve been kick out from a group :"> \n\n%s : %s',
                 'Master, Can you invite me into the group again ? \n\n%s : %s',
                 ]
        return random.choice(lines)

    def false():
        lines = ["Gomen,, what was that ?",
                 "Are you calling me ?",
                 "Hmm ? ",
                 "I wonder what is that",
                 "Maybe you should try to call 'megumi help' (?)",
                 "hmmm... I wonder what is that",
                 " .-. ? ",
                 " what ?? ._. "]
        return random.choice(lines)

    def tag_notifier():
        lines = ['Master, I think %s is calling you.. \n\n"%s"',
                 '%s is calling you master.. \n\n"%s"',
                 'Master, I think your name is being called by %s..\n\n"%s"',
                 'Master,.. tag message from %s \n\n"%s"',
                 'Check this out .. %s tagged you \n\n"%s"',
                 ]
        return random.choice(lines)

    def set_tag_notifier(cond):
        if cond == "on" :
            lines = ["OK, I will tell you if someone tag you master ~",
                     "Tag notifier is on active mode :> ",
                     "Sure, I will notify you",
                     "Roger..",
                     "Done.., itterasai :3 ~"]
            return random.choice(lines)
        elif cond == "off" :
            lines = ["Okaeri.. :3",
                     "OK, welcome back ~",
                     "Roger.. :3 ",
                     "Done,, Tag notifier is off now..",
                     "Sure,, glad to see you again.."]
            return random.choice(lines)
        elif cond == "same" :
            lines = ["Hmm.. seems nothing changed...",
                     "Hmm.. try to do it one more time.. ^^ \nsometimes it takes more than once",
                     "I don't see any difference though...",
                     "Please try again until it's changed ^^,,\nsometimes it takes more than once "]
            return random.choice(lines)
        else :
            lines = ["Gomen, I don't catch that.. :/",
                     "Hmm.. try to do it one more time.. ^^",
                     "Gomen, seems notifier setting is failed...",
                     "I think you gave wrong instruction (?) xD"]
            return random.choice(lines)

    def template():
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

    def megumi():
        return ['megumi', 'kato', 'meg', 'megumi,', 'kato,', 'meg,']

    def jessin():
        return ['jessin','jes','@jessin d','jess','jssin',]

    def day():
        return {'Mon' : 'Monday' ,
                "Tue" : "Tuesday" ,
                "Wed" : "Wednesday",
                "Thu" : "Thursday",
                "Fri" : "Friday",
                "Sat" : "Saturday",
                "Sun" : "Sunday"}

    def month():
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


class OtherUtil:
    def remove_symbols(word):
        symbols = "!@#$%^&*()_+=-`~[]{]\|;:'/?.>,<\""
        for i in range(0, len(symbols)):
            word = word.replace(symbols[i], "")  # strong syntax to remove symbols
        if len(word) > 0:
            return word


"""=============================================================================================================="""

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)