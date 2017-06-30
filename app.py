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
import requests,urllib, urllib.request
import Database

from argparse import ArgumentParser
from flask import Flask, request, abort
from bs4 import BeautifulSoup
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError,
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

from lines_collection import Lines, Labels, Picture


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
Labels = Labels()
Picture = Picture()
userlist = Database.userlist

userlist_update_count = 0
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
    global userlist,userlist_update_count

    if isinstance(event.source, SourceUser):
        userlist_init_count = len(userlist.keys()) # list count before update

        try :
            user_id = event.source.user_id
            user = line_bot_api.get_profile(event.source.user_id).display_name
            userlist.update({user_id:user})

            if len(userlist.keys()) != userlist_init_count : # theres an update
                userlist_update_count = userlist_update_count + 1

                if userlist_update_count >= 1 : # stay 2 until heroku upgraded / find a way
                    report = Lines.dev_mode_userlist("notify update userlist") % (userlist_update_count)
                    command = "megumi dev mode print userlist"
                    buttons_template = ButtonsTemplate(title="Update userlist", text=report, actions=[
                        PostbackTemplateAction(label=Labels.print_userlist(), data=command)
                    ])
                    template_message = TemplateSendMessage(alt_text=report, template=buttons_template)
                    line_bot_api.push_message(jessin_userid, template_message)

        except :
            pass

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
            elif any(word in text for word in ["movie ","movies",
                                               "film","films"])         :
                if any(word in text for word in ["showing","list",
                                                 "playing","schedule"])     : Function.show_cinema_movie_schedule()
                else                                                        : Function.false()
            elif any(word in text for word in ["wiki","is","are","'","mean","?"])  : Function.wiki_search()
            else                                                        : Function.false()

        elif all(word in text for word in ["send ","invite"])       : Function.send_invite(event)

        elif "test" in text                                         : Function.TEST(event)
        elif "command5 " in text                                    : Function.notyetcreated()


        elif all(word in text for word in ["report", "bug"])        : Function.report_bug(event)
        elif any(word in text for word in ["please leave, megumi"]) : Function.leave(event)
        elif all(word in text for word in ["dev","mode"])           :
            if Function.dev_authority_check(event)                      :
                if all(word in text for word in ["print","userlist"])       : Function.dev_print_userlist()
                elif any(word in text for word in ["turn ","able"])         :
                    if any(word in text for word in ["tag notifier",
                                                     "notif", "mention"])       : Function.dev_mode_set_tag_notifier("set")
                    else                                                        : Function.false()
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

@handler.add(PostbackEvent)
def handle_postback(event):
    global token, original_text, text, jessin_userid, user, tag_notifier_on

    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"
    original_text = event.postback.data
    text = original_text.lower()
    token = event.reply_token
    get_receiver_addr(event)
    update_user_list(event)

    if original_text == 'ping': #dummy
        line_bot_api.reply_message(token, TextSendMessage(text='pong'))

    elif all(word in text for word in ["confirmation invitation"])                  :
        if all(word in text for word in ['confirmation invitation : yes'])              : Function.invite_respond(event,"yes")
        elif all(word in text for word in ['confirmation invitation : no'])             : Function.invite_respond(event,"no")
        elif all(word in text for word in ['confirmation invitation : pending'])        : Function.invite_respond(event,"pending")

    elif all(word in text for word in ["request","cinema list please"])             :
        if all(word in text for word in ["xxi"])                                        : Function.show_cinema_list("xxi")
        elif all(word in text for word in ["cgv"])                                      : Function.show_cinema_list("cgv")

    elif all(word in text for word in ["megumi dev mode print userlist"])           :
        if Function.dev_authority_check(event)                                          :
            if all(word in text for word in ["print", "userlist"])                          : Function.dev_print_userlist()
            else                                                                            : Function.false()


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

    def send_invite(event):
        global invitation_sender, invitation_sender_id

        """ invitation data """

        try : # find desc needed
            found_index = [i for i, x in enumerate(text) if x == '*']
            desc_start = found_index[0] + 1
            desc_end = found_index[1]
            desc = text[desc_start:desc_end]
            no_desc = False
        except :
            no_desc = True
            desc = " (つ≧▽≦)つ "

        try : # find where to send
            split_text = text.split(" ")
            filtered_text = []
            for word in split_text:
                new_word = OtherUtil.remove_symbols(word)
                if new_word != None:
                    filtered_text.append(new_word)

            invite_list_index = filtered_text.index("to") + 1
            list_name = filtered_text[invite_list_index]
            invite_list = Database.list_dictionary[list_name]
            no_invite_list = False
        except :
            no_invite_list = True
            invite_list = Database.list_dictionary["dev"]

        """ report if some args missing """

        if no_desc or no_invite_list:
            if no_desc :
                report = Lines.invite_report("desc missing")
                line_bot_api.push_message(address, TextSendMessage(text=report))
            if no_invite_list :
                report = Lines.invite_report("participant list missing")
                line_bot_api.push_message(address, TextSendMessage(text=report))

        header_pic = Picture.header("background")
        title = 'Invitation'

        if (isinstance(event.source, SourceGroup)) or (isinstance(event.source, SourceRoom)):
            invitation_sender = "someone"
        else:
            invitation_sender_id = event.source.user_id
            invitation_sender = userlist[invitation_sender_id]

        """ generate the invitation """

        buttons_template = ButtonsTemplate(title=title, text=desc, thumbnail_image_url=header_pic, actions=[
            PostbackTemplateAction(label='Count me in', data='confirmation invitation : yes'),
            PostbackTemplateAction(label='No thanks', data='confirmation invitation : no'),
            PostbackTemplateAction(label='Decide later', data='confirmation invitation : pending')
        ])
        template_message = TemplateSendMessage(alt_text=desc, template=buttons_template)

        """ sending the invitation """

        try :
            report = Lines.invite("header") % invitation_sender
            invitation_sent = 0
            for participan in invite_list :
                line_bot_api.push_message(participan,TextSendMessage(text=report))
                line_bot_api.push_message(participan, template_message)
                invitation_sent += 1
            if invitation_sender != "someone" :
                report = Lines.invite("success") % invitation_sent
                line_bot_api.push_message(invitation_sender_id,TextSendMessage(text=report))

        except :
            if invitation_sender != "someone" :
                report = Lines.invite("failed")
                line_bot_api.push_message(invitation_sender_id,TextSendMessage(text=report) )

    def invite_respond(event,cond):
        global invitation_sender
        try :
            responder_id = event.source.user_id
            responder = userlist[responder_id]
        except :
            responder = "someone"

        # send respond report
        report = Lines.invite_report("respond recorded") % responder
        line_bot_api.push_message(responder_id, TextSendMessage(text=report))

        # send report to sender
        report = Lines.invite_report(cond) % responder
        if (invitation_sender != "someone") and (invitation_sender != None):
            line_bot_api.push_message(invitation_sender_id, TextSendMessage(text=report))
        else:
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def show_cinema_movie_schedule():
        if "xxi" in text :
            def get_cinema_list(search_keyword):
                if search_keyword == [] or search_keyword == [""]:
                    report = Lines.show_cinema_movie_schedule("No keyword found")
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    return []
                else:
                    cinemas = []
                    page_url = "http://www.21cineplex.com/theaters"
                    try:
                        req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                        con = urllib.request.urlopen(req)
                        page_source_code_text = con.read()
                        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                    except:
                        report = Lines.show_cinema_movie_schedule("failed to open the the page")
                        line_bot_api.push_message(address, TextSendMessage(text=report))

                    links = mod_page.findAll('a')
                    for link in links:
                        cinema_link = link.get("href")
                        if all(word in cinema_link for word in
                               (["http://www.21cineplex.com/theater/bioskop"] + search_keyword)):
                            cinemas.append(cinema_link)

                    if len(cinemas) > 1:
                        cinemas = set(cinemas)
                    return cinemas

            def get_movie_data(cinema):

                movielist = []
                desclist = []
                schedulelist = []

                req = urllib.request.Request(cinema, headers={'User-Agent': "Magic Browser"})
                con = urllib.request.urlopen(req)
                page_source_code_text = con.read()
                mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                mod_schedule_table = BeautifulSoup(str(mod_page.find("table", {"class": "table-theater-det"})), "html.parser")

                movies = mod_schedule_table.findAll('a')
                for movie in movies:
                    title = movie.string
                    if title is not None:
                        movielist.append(title)
                        movie_description = movie.get("href")
                        if movie_description in desclist :
                            desclist.append("  ")
                        else :
                            desclist.append(movie_description)

                showtimes = mod_schedule_table.findAll("td", {"align": "right"})
                for showtime in showtimes:
                    schedulelist.append(showtime.string)

                moviedata = zip(movielist, desclist, schedulelist)
                return moviedata

            def get_cinema_name(cinema_link):

                index_start = cinema_link.find("-") + 1
                index_end = cinema_link.find(",")
                cinema_name = cinema_link[index_start:index_end]
                cinema_name = cinema_name.replace("-", " ")

                """ Special case TSM """
                if cinema_name == "tsm xxi" :
                    if cinema_link == "http://www.21cineplex.com/theater/bioskop-tsm-xxi,186,BDGBSM.htm" :
                        cinema_name = "tsm xxi (Bandung)"
                    elif cinema_link == "http://www.21cineplex.com/theater/bioskop-tsm-xxi,335,UPGTSM.htm" :
                        cinema_name = "tsm xxi (Makassar)"

                return cinema_name

            def request_cinema_list():
                confirmation = Lines.show_cinema_movie_schedule("asking to show cinema list")
                buttons_template = ButtonsTemplate(text=confirmation, actions=[
                        PostbackTemplateAction(label="Sure...", data='request xxi cinema list please',text='Sure...')])
                template_message = TemplateSendMessage(alt_text=confirmation, template=buttons_template)
                line_bot_api.push_message(address, template_message)



            keyword = ['are', 'at', 'can', 'film', 'help', 'is', 'kato','list', 'me', 'meg', 'megumi', 'movie',
                       'movies', 'playing', 'please', 'pls', 'schedule', 'show', 'showing','xxi', 'what']

            search_keyword = OtherUtil.filter_words(text)
            search_keyword = OtherUtil.filter_keywords(search_keyword, keyword)

            cinemas = get_cinema_list(search_keyword)


            if len(cinemas) <= 0:
                reply = Lines.show_cinema_movie_schedule("No cinema found") % (", ".join(search_keyword))
                ask_for_request = True
            elif len(cinemas) > 2:
                reply = Lines.show_cinema_movie_schedule("Too many cinemas") % (", ".join(search_keyword))
                ask_for_request = True
            else:
                try:
                    reply = []
                    reply.append(Lines.show_cinema_movie_schedule("header") % (", ".join(search_keyword)))
                    for cinema in cinemas:
                        cinema_name = get_cinema_name(cinema)
                        moviedata = get_movie_data(cinema)
                        reply.append(Lines.show_cinema_movie_schedule("cinema name") % cinema_name)
                        for data in moviedata:
                            reply.append(data[0])  # movie title
                            reply.append(data[1])  # movie description
                            reply.append(data[2])  # movie schedule
                            reply.append("\n")

                    reply.append(Lines.show_cinema_movie_schedule("footer"))
                    reply = "\n".join(reply)
                    ask_for_request = False
                except :
                    reply = Lines.show_cinema_movie_schedule("failed to show movie data")


            line_bot_api.reply_message(token,TextSendMessage(text=reply))
            if ask_for_request :
                request_cinema_list()

        elif "cgv" in text :
            def get_cinema_list(search_keyword):
                if search_keyword == [] or search_keyword == [""]:
                    report = Lines.show_cinema_movie_schedule("No keyword found")
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                else:
                    cinemas_name = []
                    cinemas_link = []
                    page_url = "https://www.cgv.id/en/schedule/cinema/"
                    try:
                        req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                        con = urllib.request.urlopen(req)
                        page_source_code_text = con.read()
                        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                    except:
                        report = Lines.show_cinema_movie_schedule("failed to open the the page")
                        line_bot_api.push_message(address, TextSendMessage(text=report))

                    links = mod_page.findAll('a', {"class": "cinema_fav"})
                    for link in links:
                        cinema_name = link.string
                        cinema_link = "https://www.cgv.id" + link.get("href")
                        if all(word in cinema_name.lower() for word in search_keyword):
                            cinemas_name.append(cinema_name)
                            cinemas_link.append(cinema_link)

                    cinemas = zip(cinemas_name, cinemas_link)
                    return cinemas

            def get_movie_data(cinema):

                movielist = []
                desclist = []
                schedulelist = []

                req = urllib.request.Request(cinema, headers={'User-Agent': "Magic Browser"})
                con = urllib.request.urlopen(req)
                page_source_code_text = con.read()
                mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                mod_schedule_table = BeautifulSoup(str(mod_page.findAll("div", {"class": "schedule-lists"})),"html.parser")
                movies_data = BeautifulSoup(str(mod_schedule_table.findAll("div", {"class": "schedule-title"})),"html.parser")

                movies = movies_data.findAll("a")  # getting the movie name and desc
                for movie in movies:
                    movie_name = movie.string
                    movie_desc = "https://www.cgv.id" + movie.get("href")
                    movielist.append(movie_name)
                    desclist.append(movie_desc)

                schedules = mod_schedule_table.findAll("a", {"id": "load-schedule-time"})  # getting the movie schedule
                last_movie = ""
                for schedule in schedules:
                    movie_title = schedule.get("movietitle")
                    time = schedule.string
                    if movie_title != last_movie:
                        schedulelist.append("#")
                        last_movie = movie_title
                    if time != ", ":
                        schedulelist.append(time)

                # re formatting the schedulelist
                schedulelist = " ".join(schedulelist)
                schedulelist = schedulelist.split("#")
                try:
                    schedulelist.remove("")
                except:
                    pass

                moviedata = zip(movielist, desclist, schedulelist)
                return moviedata


            def request_cinema_list():
                confirmation = Lines.show_cinema_movie_schedule("asking to show cinema list")
                buttons_template = ButtonsTemplate(text=confirmation, actions=[
                    PostbackTemplateAction(label="Sure...", data='request cgv cinema list please', text='Sure...')])
                template_message = TemplateSendMessage(alt_text=confirmation, template=buttons_template)
                line_bot_api.push_message(address, template_message)

            keyword = ['are', 'at', 'can', 'cgv', 'film', 'help', 'is', 'kato', 'list', 'me', 'meg', 'megumi', 'movie',
                       'movies', 'playing', 'please', 'pls', 'schedule', 'show', 'showing', 'what']

            search_keyword = OtherUtil.filter_words(text)
            search_keyword = OtherUtil.filter_keywords(search_keyword, keyword)

            cinemas = get_cinema_list(search_keyword)  # return a list with [ cinema name , cinema url]

            found_cinema_name = []
            found_cinema_link = []
            for cinema in cinemas:
                found_cinema_name.append(cinema[0])
                found_cinema_link.append(cinema[1])

            found_cinema = zip(found_cinema_name, found_cinema_link)

            if len(found_cinema_name) <= 0:
                reply = Lines.show_cinema_movie_schedul6e("No cinema found") % (", ".join(search_keyword))
                ask_for_request = True
            elif len(found_cinema_name) > 2:
                reply = Lines.show_cinema_movie_schedule("Too many cinemas") % (", ".join(search_keyword))
                ask_for_request = True
            else:
                """ if cinema amount is just fine... """
                try:
                    reply = []
                    reply.append(Lines.show_cinema_movie_schedule("header") % (", ".join(search_keyword)))
                    for cinema in found_cinema:
                        cinema_name = cinema[0]  # cinema [0] is the cinema name
                        moviedata = get_movie_data(cinema[1])  # cinema [1] is the cinema link
                        reply.append(Lines.show_cinema_movie_schedule("cinema name") % cinema_name)
                        for data in moviedata:
                            reply.append(data[0])  # movie title
                            reply.append(data[1])  # movie description
                            reply.append(data[2])  # movie schedule
                            reply.append("\n")

                    reply.append(Lines.show_cinema_movie_schedule("footer"))
                    reply = "\n".join(reply)
                    ask_for_request = False

                except:
                    reply = Lines.show_cinema_movie_schedule("failed to show movie data")

            line_bot_api.reply_message(token, TextSendMessage(text=reply))
            if ask_for_request:
                request_cinema_list()

        else:
            report = Lines.show_cinema_movie_schedule("specify the company")
            line_bot_api.push_message(address, TextSendMessage(text=report))

    def show_cinema_list(cond):

        if cond == "xxi" :
            def get_cinema_list():
                cinemas = []
                page_url = "http://www.21cineplex.com/theaters"
                req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                con = urllib.request.urlopen(req)
                page_source_code_text = con.read()
                mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                links = mod_page.findAll('a')
                for link in links:
                    cinema_link = link.get("href")
                    if all(word in cinema_link for word in ["http://www.21cineplex.com/theater/bioskop"]):
                        cinemas.append(cinema_link)

                cinemas = set(cinemas)
                return cinemas

            def get_cinema_name(cinema_link):

                index_start = cinema_link.find("-") + 1
                index_end = cinema_link.find(",")
                cinema_name = cinema_link[index_start:index_end]
                cinema_name = cinema_name.replace("-", " ")

                """ Special case TSM """
                if cinema_name == "tsm xxi" :
                    if cinema_link == "http://www.21cineplex.com/theater/bioskop-tsm-xxi,186,BDGBSM.htm" :
                        cinema_name = "tsm xxi (Bandung)"
                    elif cinema_link == "http://www.21cineplex.com/theater/bioskop-tsm-xxi,335,UPGTSM.htm" :
                        cinema_name = "tsm xxi (Makassar)"

                return cinema_name


            cinema_list = []
            cinemas = get_cinema_list()

            for cinema in cinemas:
                cinema_list.append(get_cinema_name(cinema))
            cinema_list = sorted(cinema_list)
            cinema_list.insert(0,Lines.show_cinema_movie_schedule("show cinema list"))
            report = "\n".join(cinema_list)

            if len(report) > 1800 :
                report1 = report[:1800]+"..."
                report2 = "..."+report[1801:]
                line_bot_api.push_message(address, TextSendMessage(text=report1))
                line_bot_api.push_message(address, TextSendMessage(text=report2))
            else :
                line_bot_api.push_message(address, TextSendMessage(text=report))

        elif cond == "cgv" :
            cinema_list = []
            page_url = "https://www.cgv.id/en/schedule/cinema/"

            req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
            con = urllib.request.urlopen(req)
            page_source_code_text = con.read()
            mod_page = BeautifulSoup(page_source_code_text, "html.parser")
            cinemas = mod_page.findAll('a', {"class": "cinema_fav"})

            for cinema in cinemas:
                cinema = cinema.string
                cinema_list.append(cinema)

            cinema_list = sorted(cinema_list)
            cinema_list.insert(0, Lines.show_cinema_movie_schedule("show cinema list"))
            report = "\n".join(cinema_list)

            if len(report) > 1800:
                report1 = report[:1800] + "..."
                report2 = "..." + report[1801:]
                line_bot_api.push_message(address, TextSendMessage(text=report1))
                line_bot_api.push_message(address, TextSendMessage(text=report2))
            else:
                line_bot_api.push_message(address, TextSendMessage(text=report))

    def wiki_search():
        def getting_page_title(mod_page):
            try:
                first_heading = mod_page.findAll("h1", {"id": "firstHeading"})
                page_title = first_heading[0].string
                return page_title
            except:
                return "page title doesn't exist"

        def is_specific(mod_page):
            content = str(mod_page.find_all('p'))
            keyword = ["commonly refers to", "may also refer to", "may refer to"]

            if any(word in content for word in keyword):
                return False
            else:
                return True

        def has_disambiguation(mod_page):
            content = str(mod_page.find_all('a', {"class": "mw-disambig"}))
            keyword = ["disambiguation"]

            if any(word in content for word in keyword):
                return True
            else:
                return False

        def first_paragraph_coordinate(mod_page):
            content = str(mod_page.find('p'))
            keyword = ["coordinate"]

            if any(word in content for word in keyword):
                return True
            else:
                return False

        def get_paragraph(mod_page, cond='first'):

            def filter_paragraph_contents(content, start_sym='<', end_sym='>'):
                isfilter = (start_sym or end_sym) in content
                while isfilter:
                    start_index = content.find(start_sym)
                    stop_index = content.find(end_sym) + 1
                    content = content.replace(str(content[start_index:stop_index]), "")
                    isfilter = (start_sym or end_sym) in content
                return content

            if cond == 'first':
                content = mod_page.find('p')
            elif cond == 'second':
                content = mod_page.find_all('p')[1]
            content = filter_paragraph_contents(str(content), '<', '>')
            content = filter_paragraph_contents(str(content), '[', ']')
            return content

        def show_suggestion(mod_page):
            suggestion = []
            keyword = ['All pages beginning with ', 'disambiguation', 'Categories', 'Disambiguation',
                       'Place name disambiguation ', 'All article disambiguation ', 'All disambiguation ', 'Talk',
                       'Contributions', 'Article', 'Talk', 'Read', 'Main page', 'Contents', 'Featured content',
                       'Current events', 'Random article', 'Donate to Wikipedia', 'Help', 'About Wikipedia',
                       'Community portal',
                       'Recent changes', 'Contact page', 'What links here', 'Related changes', 'Upload file',
                       'Special pages',
                       'Wikidata item', 'Wikispecies', 'Cebuano', 'Čeština', 'Deutsch', 'Eesti', 'Español',
                       'Français',
                       '한국어', 'Italiano', 'עברית', 'Latviešu', 'Magyar', 'Nederlands', '日本語', 'Norsk bokmål',
                       'پښتو',
                       'Polski', 'Português', 'Русский', 'Simple English', 'Slovenščina', 'Српски / srpski',
                       'Srpskohrvatski / српскохрватски', 'Suomi', 'Svenska', 'Türkçe', 'Українська', 'اردو',
                       'Volapük',
                       'Edit links', 'Creative Commons Attribution-ShareAlike License', 'Terms of Use',
                       'Privacy Policy',
                       'Privacy policy', 'About Wikipedia', 'Disclaimers', 'Contact Wikipedia', 'Developers',
                       'Cookie statement']

            links = mod_page.find_all('a')

            for link in links:
                href = str(link.get("href"))
                if "/wiki/" in (href[:6]):  # to eliminate wiktionary links
                    if link.string is not None:
                        if not (any(word in link.string for word in keyword)):
                            suggestion.append(link.string)
            suggestion = suggestion[:10]
            return suggestion

        def get_search_keyword():

            split_text = OtherUtil.filter_words(text, "for wiki search")
            keyword = []
            for word in split_text:
                if "'" in word:
                    keyword.append(word)

            if keyword == []:
                return
            else:
                keyword = " ".join(keyword)
                keyword = keyword.replace(" ", "_")
                return keyword

        def get_search_language():

            try:
                split_text = OtherUtil.filter_words(text)
                index_now = 0
                for word in split_text:
                    if word == "wiki":
                        index_found = index_now - 1
                        break
                    index_now = index_now + 1
                language = split_text[index_found]

            except:
                language = 'en'  # default search language

            return language

        def request_page():
            text = Lines.wiki_search("ask detail info")
            header_pic = Picture.header("background")
            buttons_template = ButtonsTemplate(text=text, thumbnail_image_url=header_pic, actions=[
                URITemplateAction(label=Labels.confirmation("yes"), uri=str(page_url))
            ])
            template_message = TemplateSendMessage(alt_text=text, template=buttons_template)
            line_bot_api.push_message(address, template_message)

        keyword = get_search_keyword()
        language = get_search_language()
        report = []
        request_detailed_info = False

        if keyword != None:
            try:
                keyword = keyword[1:-1]
                page_url = "https://" + language + ".wikipedia.org/wiki/" + keyword
                req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                con = urllib.request.urlopen(req)
                page_source_code_text = con.read()
                mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                exist = True
            except :
                report.append(Lines.wiki_search("page not found") % (language, keyword))
                exist = False

            if exist:
                title = getting_page_title(mod_page)
                if is_specific(mod_page):
                    report.append(title)
                    if has_disambiguation(mod_page):
                        report.append(Lines.wiki_search("has disambiguation"))

                    if first_paragraph_coordinate(mod_page):
                        report.append(get_paragraph(mod_page, 'second'))
                    else:
                        report.append(get_paragraph(mod_page, 'first'))

                    request_detailed_info = True

                else:
                    report.append(Lines.wiki_search("not specific page - header") % keyword)
                    report.append(Lines.wiki_search("not specific page - content") % keyword)
                    suggestion = show_suggestion(mod_page)
                    suggestion = "\n".join(suggestion)
                    report.append(suggestion)
        else:
            report.append(Lines.wiki_search("no keyword found"))

        report = "\n".join(report)
        line_bot_api.push_message(address, TextSendMessage(text=report))
        if request_detailed_info:
            request_page()

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

        report = Lines.removed("report") % (user)
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def dev_mode_set_tag_notifier(cond="pass"):
        global tag_notifier_on
        if cond == "set":
            if any(word in text for word in ["on ", "enable "]):
                if tag_notifier_on is not True :
                    tag_notifier_on = True
                    reply = Lines.dev_mode_set_tag_notifier("on")
                else:  # already True
                    reply = Lines.dev_mode_set_tag_notifier("same")

            elif any(word in text for word in ["off ", "disable "]):
                if tag_notifier_on is True :
                    tag_notifier_on = False
                    reply = Lines.dev_mode_set_tag_notifier("off")
                else:  # already False
                    reply = Lines.dev_mode_set_tag_notifier("same")

            else:
                reply = Lines.dev_mode_set_tag_notifier("fail")
                pass

            line_bot_api.reply_message(token, TextSendMessage(text=reply))

        elif cond == "pass":
            pass


    def dev_print_userlist():
        global userlist_update_count
        if userlist_update_count != 0 :
            try :
                print("=================================== new user list ===================================\n")
                print(userlist)
                print("\n================================= end of  user list =================================")
                reply = Lines.dev_mode_userlist("print userlist success") % (userlist_update_count)
                userlist_update_count = 0
            except :
                reply = Lines.dev_mode_userlist("print userlist failed")
        elif userlist_update_count == 0 :
            reply = Lines.dev_mode_userlist("userlist not updated yet")
        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    def dev_authority_check(event):
        try:
            user_id = event.source.user_id
            user = userlist[user_id]

            if (user_id == jessin_userid):
                granted = True
            else:
                reply = Lines.dev_mode_authority_check("reject")
                line_bot_api.reply_message(token, TextSendMessage(text=reply))
                report = Lines.dev_mode_authority_check("notify report") % (user)
                line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))
                granted = False

        except : #accessed in group / room / failed
            user = "someone"
            reply = Lines.dev_mode_authority_check("failed")
            line_bot_api.reply_message(token, TextSendMessage(text=reply))
            report = Lines.dev_mode_authority_check("notify report") % (user)
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))
            granted = False

        return granted

    def TEST(event):
        return



    def template():
        reply = Lines.added("cond")
        line_bot_api.reply_message(token, TextSendMessage(text=reply))
        report = Lines.added("report")
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

class OtherUtil:
    def remove_symbols(word,cond="default"):
        if cond == "default" :
            symbols = "!@#$%^&*()+=-`~[]{]\|;:'/?.>,<\""
        elif cond == "for wiki search" :
            symbols = "!@#$%^&*+=-`~[]{]\|;:/?.>,<\""

        for i in range(0, len(symbols)):
            word = word.replace(symbols[i], "")  # strong syntax to remove symbols
        if len(word) > 0:
            return word

    def filter_words(text,cond="default"):
        split_text = text.split(" ")
        filtered_text = []
        for word in split_text:
            new_word = OtherUtil.remove_symbols(word,cond)
            if new_word != None:
                filtered_text.append(new_word)
        return filtered_text

    def filter_keywords(text, keyword):
        while any(word in text for word in keyword):
            for word in text:
                if word in keyword:
                    text.remove(word)
        return text

"""========================================== end of function list ================================================"""

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()


    app.run(debug=options.debug, port=options.port)

