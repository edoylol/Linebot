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
from lines_collection import Lines

Lines = Lines()

class Function:
    """====================== Main Function List ==========================="""

    def rand_int(self):

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

    def echo(self):
        try :
            start_index = text.find("say ")+4
            reply = Lines.echo() % str(original_text[start_index:])
        except :
            reply = "What should I say?"

        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def choose_one(self):
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

    def choose_one_simple(self):
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

    def time_date(self):
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



    def report_bug(self,event):

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

    def join(self):

        reply = Lines.join()
        line_bot_api.reply_message(token, TextSendMessage(text=reply))
        report = Lines.join_note()
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def leave(self,event):

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

    def set_tag_notifier(self,cond="pass"):
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

    def tag_notifier(self,event):
        if any(word in text for word in Lines.jessin()):
            try :
                sender = line_bot_api.get_profile(event.source.user_id).display_name
            except :
                sender = "someone"
            report = Lines.tag_notifier() % (sender,original_text)
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def notyetcreated(self):
        reply = Lines.notyetcreated()
        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def false(self):
        reply = Lines.false()
        line_bot_api.reply_message(token, TextSendMessage(text=reply))



class OtherUtil:
    def remove_symbols(self,word):
        symbols = "!@#$%^&*()_+=-`~[]{]\|;:'/?.>,<\""
        for i in range(0, len(symbols)):
            word = word.replace(symbols[i], "")  # strong syntax to remove symbols
        if len(word) > 0:
            return word

