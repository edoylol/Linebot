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
import errno
import random
import time
import math
import tempfile
import urllib.request
import Database

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

from lines_collection import Lines


app = Flask(__name__)

# Megumi chat bot (note : remove the whitespace )

# channel_secret = '9d1e7500a205ddaec1c6f2ae0d190e6e'
# channel_access_token = 'f/jBF6+aFLuvzEmI0NbPNWjfrsK3Kjwxzzl1XUeLun+3uRs6AbDEQGphezyssudufYiyiHBoLQWWjEBqTtV00P0jLOJuV
#                         lrEQly/Xjo7ZQXY0YMEoKm869aWpCnu9Jhog4zt4nb4DYB4zVMWApdjCQdB04t89/1O/w1cDnyilFU='

channel_secret = "9b665635f2f8e005e0e9eed13ef18124"
channel_access_token = "ksxtpzGYTb1Nmbgx8Nj8hhkUR5ZueNWdBSziqVlJ2fPNblYeXV7/52HWvey/MhXjgtbml0LFuwQHpJHCP6jN7W0gaKZVUOlA88AS5x58IhqzLZ4Qt91cV8DhXztok9yyBQKAOSxh/uli4cP4lj+2YQdB04t89/1O/w1cDnyilFU="
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

Lines = Lines()
userlist = Database.userlist
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

def update_user_list(event):
    global userlist

    if isinstance(event.source, SourceUser):
        try :
            user_id = event.source.user_id
            user = line_bot_api.get_profile(event.source.user_id).display_name
            userlist.update({user_id:user})
            print(userlist)
            print("update success")
        except :
            print("update fail")

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    global token, original_text, text, jessin_userid, user, tag_notifier_on

    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"

    original_text = event.message.text
    text = original_text.lower()
    token = event.reply_token
    get_receiver_addr(event)
    update_user_list(event)


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
        Function.tag_notifier(event)

#@handler.add(MessageEvent, message=StickerMessage)
# what does people do when being sent a sticker ???

"""  
def handle_sticker_message(event):
    global token
    token = event.reply_token
    get_receiver_addr(event)

    try :
        package_id = str(event.message.package_id)
        sticker_id = str(event.message.sticker_id)
        reply = ("package =",package_id,"\nsticker id =",sticker_id)
        line_bot_api.reply_message(token,TextSendMessage(reply))

    except LineBotApiError as e:
        print(event.message)
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
"""

#@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
# what does people do when being sent a image, video, or audio ??? #

"""
def handle_content_message(event):
    global token
    token = event.reply_token
    get_receiver_addr(event)
"""



@handler.add(JoinEvent)
def handle_join(event):
    global token,jessin_userid
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"

    token = event.reply_token
    get_receiver_addr(event)

    Function.join()

@handler.add(FollowEvent)
def handle_follow(event):
    global token, jessin_userid
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"
    print(event)
    update_user_list(event)
    token = event.reply_token


    Function.added(event)

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    global jessin_userid
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"
    update_user_list(event)

    Function.removed(event)


""""===================================== Usable Function List ==================================================="""

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
            reply = Lines.choose_one("success") % str(result)
        except :
            reply = Lines.choose_one("fail")

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

    """====================== Sub Function List ============================="""

    def report_bug(event):
        try :
            user_id = event.source.user_id
            user = userlist[user_id]
        except :
            user = "Anonymous"
        try:
            report = Lines.report_bug("report") % (original_text,user)
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))
            reply = Lines.report_bug("success")

        except:
            reply = Lines.report_bug("fail")
        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def join():

        reply = Lines.join("join")
        line_bot_api.reply_message(token, TextSendMessage(text=reply))
        report = Lines.join("report")
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def leave(event):

        if isinstance(event.source, SourceGroup):
            group_id = event.source.group_id

            reply = Lines.leave("leave")
            line_bot_api.push_message(group_id, TextSendMessage(text=reply))

            reply = Lines.leave("regards")
            line_bot_api.reply_message(token, TextSendMessage(text=reply))

            report = Lines.leave("report") % ('Group', group_id)
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

            line_bot_api.leave_group(group_id)

        elif isinstance(event.source, SourceRoom):
            room_id = event.source.room_id

            reply = Lines.leave("leave")
            line_bot_api.push_message(room_id, TextSendMessage(text=reply))

            reply = Lines.leave("regards")
            line_bot_api.reply_message(token, TextSendMessage(text=reply))

            report = Lines.leave("report") % ('Chatroom', room_id)
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
        if any(word in text for word in Lines.jessin()):
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

    def added(event):
        try :
            user_id = event.source.user_id
            user = userlist[user_id]
        except :
            user = "someone"

        reply = Lines.added("added") % (user)
        line_bot_api.reply_message(token, TextSendMessage(text=reply))
        report = Lines.added("report") % (user)
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def removed(event):
        try :
            user_id = event.source.user_id
            user = userlist[user_id]
        except :
            user = "someone"

        print("SOURCE",event.source)
        report = Lines.removed("report") % (user)
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def template():
        reply = Lines.added("cond")
        line_bot_api.reply_message(token, TextSendMessage(text=reply))
        report = Lines.added("report")
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

class OtherUtil:
    def remove_symbols(word):
        symbols = "!@#$%^&*()_+=-`~[]{]\|;:'/?.>,<\""
        for i in range(0, len(symbols)):
            word = word.replace(symbols[i], "")  # strong syntax to remove symbols
        if len(word) > 0:
            return word


"""========================================== end of function list ================================================"""

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()


    app.run(debug=options.debug, port=options.port)

