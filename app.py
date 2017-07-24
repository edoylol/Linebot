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
import math
import random
import time

import requests,urllib, urllib.request
import Database
import unshortenit
import json

from argparse import ArgumentParser
from flask import Flask, request, abort
from bs4 import BeautifulSoup
from datetime import timedelta
from datetime import datetime
from xml.etree import ElementTree

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
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    AudioSendMessage
)

from lines_collection import Lines, Labels, Picture


app = Flask(__name__)

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
def callback():
    """ Get X-Line-Signature header value """

    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


def get_receiver_addr(event):
    """ Get the address (source of event) weather it's group or personal chat """

    # Enable calling from all functions and methods
    global address

    # If the event was sent from a group
    if isinstance(event.source, SourceGroup):
        address = event.source.group_id

    # If the event was sent from a chat room
    elif isinstance(event.source, SourceRoom):
        address = event.source.room_id

    # If the event was sent from a personal chat
    else :
        address = event.source.user_id

    return address


def update_user_list(event):
    """ Function to notify if the userlist is updated TEMPORARILY """
    global userlist, userlist_update_count

    # If the add event come from personal chat
    if isinstance(event.source, SourceUser):
        # Get the list count before update
        userlist_init_count = len(userlist.keys())

        try :
            # Get the user data
            user_id = event.source.user_id
            user = line_bot_api.get_profile(event.source.user_id).display_name
            userlist.update({user_id: user})

            # If there's an update
            if len(userlist.keys()) != userlist_init_count:
                userlist_update_count = userlist_update_count + 1

                if userlist_update_count >= 1:  # stay 1 until heroku upgraded (due to 30 mins inactivity)

                    # Send report to Dev (reminder to update the list)
                    report = Lines.dev_mode_userlist("notify update userlist") % (str(userlist_update_count))
                    command = "megumi dev mode print userlist"
                    buttons_template = ButtonsTemplate(title="Update userlist", text=report, actions=[
                        PostbackTemplateAction(label=Labels.print_userlist(), data=command)
                    ])
                    template_message = TemplateSendMessage(alt_text=report, template=buttons_template)
                    line_bot_api.push_message(jessin_userid, template_message)

        except Exception as exception_detail:
            function_name = "Sending Userlist notification"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    """ Function to handle event that is a text message """

    global token, original_text, text, jessin_userid, user, tag_notifier_on

    # Dev / your user id
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"

    # Get general information from event
    original_text = event.message.text
    text = original_text.lower()
    token = event.reply_token
    get_receiver_addr(event)
    update_user_list(event)

    # List of command available by sending text message
    if any(word in text for word in Lines.megumi()):

        if all(word in text for word in ["pick ", "num"])            : Function.rand_int()
        elif any(word in text for word in ["choose ", "which one"])  : Function.choose_one_simple()

        elif any(word in text for word in ["what ", "show "])        :
            if any(word in text for word in ["date", "time", "day"])    : Function.time_date()
            elif any(word in text for word in ["weather", "forecast"])  : Function.weather_forcast()
            elif any(word in text for word in ["movie ", "movies",
                                               "film", "films"])        :
                if any(word in text for word in ["showing", "list",
                                                 "playing", "schedule"])    : Function.show_cinema_movie_schedule()
                else                                                        : Function.false()

            elif all(word in text for word in ["anime"])                :
                if any(word in text for word in ["download", "link"])       : Function.anime_download_link()
                else                                                        : Function.false()

            elif any(word in text for word in ["is", "are", "info",
                                               "information", "?"])     :
                if any(word in text for word in ["sw", "summonerswar",
                                                 "summoner"])               : Function.summonerswar_wiki()
                elif all(word in text for word in ["itb"])                  :
                    if "'" in text                                              : Function.itb_arc_database()
                    else                                                        : Function.false()
                elif any(word in text for word in ["in"])                       : Function.translate_text()
                elif any(word in text for word in ["mean", "wiki"])         :
                    if "'" in text                                              : Function.wiki_search()
                    else                                                        : Function.false()

                else                                                        : Function.false()
            else                                                        : Function.false()

        elif any(word in text for word in ["how"])                  :
            if any(word in text for word in ["weather", "forecast"])    : Function.weather_forcast()
            elif any(word in text for word in ["say"])                  : Function.translate_text()
            else                                                        : Function.false()

        elif all(word in text for word in ["who"])                  :
            if all(word in text for word in ["itb"])                    :
                if "'" in text                                              : Function.itb_arc_database()
                else                                                        : Function.false()
            else                                                        : Function.false()

        elif any(word in text for word in ["download ", "save "])   :
            if any(word in text for word in ["youtube", "video"])       : Function.download_youtube()
            elif any(word in text for word in ["anime"])                : Function.anime_download_link()
            else                                                        : Function.false()

        elif any(word in text for word in ["translate"])            : Function.translate_text()
        elif any(word in text for word in ["say "])                 : Function.echo()
        elif all(word in text for word in ["send ", "invite"])      : Function.send_invite(event)

        elif all(word in text for word in ["report", "bug"])        : Function.report_bug(event)
        elif any(word in text for word in ["please leave, megumi"]) : Function.leave(event)
        elif all(word in text for word in ["dev", "mode"])          :

            if Function.dev_authority_check(event)                      :
                if all(word in text for word in ["print", "userlist"])      : Function.dev_print_userlist()
                elif any(word in text for word in ["turn ", "able"])        :
                    if any(word in text for word in ["tag notifier",
                                                     "notif", "mention"])       : Function.dev_mode_set_tag_notifier("set")
                    else                                                        : Function.false()

        elif all(word in text for word in ["test new feature"])     : Function.TEST()
        else                                                        : Function.false()

    # Special tag / mention function
    if tag_notifier_on:
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
    """ Function to handle event that is a postback message (send by template message)  """

    global token, original_text, text, jessin_userid, user, tag_notifier_on

    # Dev / your user id
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"

    # Get general information from event
    original_text = event.postback.data
    text = original_text.lower()
    token = event.reply_token
    get_receiver_addr(event)
    update_user_list(event)

    # List of command that is available for postback event
    if original_text == 'ping':
        line_bot_api.reply_message(token, TextSendMessage(text='pong'))

    elif all(word in text for word in ["confirmation invitation"])                  :
        if all(word in text for word in ['confirmation invitation : yes'])              : Function.invite_respond(event,"yes")
        elif all(word in text for word in ['confirmation invitation : no'])             : Function.invite_respond(event,"no")
        elif all(word in text for word in ['confirmation invitation : pending'])        : Function.invite_respond(event,"pending")

    elif all(word in text for word in ["request", "cinema list please"])            :
        if all(word in text for word in ["xxi"])                                        : Function.show_cinema_list("xxi")
        elif all(word in text for word in ["cgv"])                                      : Function.show_cinema_list("cgv")

    elif all(word in text for word in ["summoners_war_wiki"])                       :
        if all(word in text for word in ["overview"])                                   : Function.summonerswar_wiki("overview")
        elif all(word in text for word in ["ratings"])                                  : Function.summonerswar_wiki("show ratings")
        elif all(word in text for word in ["stats"])                                    : Function.summonerswar_wiki("show stats")
        elif all(word in text for word in ["skills"])                                   : Function.summonerswar_wiki("show skills")

    elif all(word in text for word in ["megumi dev mode print userlist"])           :
        if Function.dev_authority_check(event)                                          :
            if all(word in text for word in ["print", "userlist"])                          : Function.dev_print_userlist()
            else                                                                            : Function.false()

@handler.add(JoinEvent)
def handle_join(event):
    """ Function to handle join event (when bot join a chat room / group) """

    global token,jessin_userid

    # Dev / your user id
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"

    token = event.reply_token
    get_receiver_addr(event)

    # Special function dedicated for join event
    Function.join()

@handler.add(FollowEvent)
def handle_follow(event):
    """ Function to handle follow event (when someone add this bot) """
    global token, jessin_userid

    # Dev / your user id
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"
    update_user_list(event)
    token = event.reply_token

    # Special function dedicated for follow event
    Function.added(event)

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    """ Function to handle follow event (when someone block this bot) """
    global jessin_userid

    # Dev / your user id
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"
    update_user_list(event)

    # Special function dedicated for unfollow event
    Function.removed(event)


""""===================================== Usable Function List ==================================================="""


class Function:
    """====================== Main Function List ==========================="""

    @staticmethod
    def rand_int():
        """ Function to return random integer between the minimum and maximum number given in text """
        try:
            def random_number(min_number=1, max_number=5):
                """ Function to generate random integer from min to max.
                min set to 1 and max set to 5 by default. """

                # If min and max are wrongly put, swap them
                if min_number > max_number:
                    temp = min_number
                    min_number = max_number
                    max_number = temp

                # Sampling random for more random result
                a = random.randrange(min_number, max_number+1)
                b = random.randrange(min_number, max_number+1)
                c = random.randrange(min_number, max_number+1)
                d = random.randrange(min_number, max_number+1)
                e = random.randrange(min_number, max_number+1)

                return random.choice([a, b, c, d, e])

            def get_number():
                """ Function to extract number from text """

                found = []
                # Iterate for each word, check weather it's a integer or not
                for word in split_text:
                    try:
                        found.append(int(word))
                    except ValueError:
                        continue

                return found

            split_text = text.split(" ")
            found_num = get_number()
            report = []

            # If the number is exactly 2 (min and max)
            if len(found_num) == 2:
                result = random_number(found_num[0], found_num[1])
                report.append(Lines.rand_int("success") % str(result))

            # If the number is incomplete to serve as min and max, use default settings
            elif len(found_num) < 2:
                result = random_number()
                report.append(Lines.rand_int("default"))
                report.append(Lines.rand_int("success") % str(result))

            # If there are too much number or other error happened
            else:
                report.append(Lines.rand_int("failed"))

            # Send the result to the user
            report = "\n".join(report)
            line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "random integer"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def echo():
        """ Function to echo whatever surrounded by single apostrophe (') """

        try:
            # Find the index of apostrophe
            index_start = text.find("'") + 1
            index_stop = text.rfind("'")

            # If the text (which should be echo-ed) is found
            if index_start != 0 and index_stop != (-1):
                echo_text = text[index_start:index_stop]
                report = Lines.echo("success") % echo_text

            # If the text is not found
            else:
                report = Lines.echo("failed")

            # Send the result
            line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "echo"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def choose_one_simple():

        try :
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

        except Exception as exception_detail:
            function_name = "Choose one"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def time_date():

        try :
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
                    if ('' in split_time) or (None in split_time):
                        for element in split_time :
                            if (element == '') or (element == None):
                                split_time.remove(element)

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

        except Exception as exception_detail:
            function_name = "Time and Date"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def send_invite(event):

        try :
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

        except Exception as exception_detail:
            function_name = "Send Invite"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def invite_respond(event,cond):

        try :
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
            try :
                if (invitation_sender != "someone") and (invitation_sender != None):
                    line_bot_api.push_message(invitation_sender_id, TextSendMessage(text=report))
                else:
                    line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))
            except :
                pass

        except Exception as exception_detail:
            function_name = "Invite respond"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def show_cinema_movie_schedule():

        try :
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

        except Exception as exception_detail:
            function_name = "Show cinema movie schedule"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def show_cinema_list(cond):

        try :
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

        except Exception as exception_detail:
            function_name = "Show cinema list"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def wiki_search():

        try :
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
                    report.append(Lines.wiki_search("try different keyword / language"))
                    report.append("https://meta.wikimedia.org/wiki/List_of_Wikipedias")
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

        except Exception as exception_detail:
            function_name = "Wiki search"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def download_youtube():

        try :
            def get_youtube_link():
                keyword = ["https://www.youtube.com/watch?v=","https://youtu.be/"]
                youtube_link = ""
                text = original_text
                if any(word in text.lower() for word in keyword) :
                    text = text.split(" ")
                    for word in text:
                        if any(x in word.lower() for x in keyword):
                            youtube_link = word

                return youtube_link

            def get_spec():
                vid_format = "MP4"
                vid_quality_min = 720
                vid_quality_max = 720
                default = True

                video_audio_format_list = ['3g2', '3gp', 'aa', 'aac', 'aax', 'act', 'amr', 'amv', 'asf', 'au', 'avi',
                                           'awb', 'dct', 'drc', 'dss', 'dvf', 'f4a', 'f4b', 'f4p', 'f4v', 'flac', 'flv',
                                           'gif', 'gifv', 'm4a', 'm4b', 'm4p', 'm4v', 'mkv', 'mmf', 'mng', 'mov', 'mp2',
                                           'mp3', 'mp4', 'mpc', 'mpe', 'mpeg', 'mpg', 'mpv', 'msv', 'ogg', 'ogv', 'rm',
                                           'rmvb', 'vob', 'wav', 'webm', 'wma', 'wmv', 'yuv']

                if any(word in text for word in video_audio_format_list):
                    split_text = text.split(" ")
                    for word in split_text :
                        if word in video_audio_format_list :
                            vid_format = word
                            default = False

                if any(word in text for word in ['min','max']):
                    split_text = text.split(" ")
                    index = 0
                    for word in split_text :
                        if 'min' in word :
                            try :
                                vid_quality_min = int(split_text[index+1])
                                default = False
                            except :
                                pass

                        if 'max' in word :
                            try :
                                vid_quality_max = int(split_text[index+1])
                                default = False
                            except :
                                pass

                        index = index + 1

                return (vid_format.upper(),vid_quality_min,vid_quality_max,default)

            def get_genyoutube(youtube_link):
                if "https://www.youtube.com/watch?v=" in youtube_link :
                    video_id = youtube_link.replace("https://www.youtube.com/watch?v=", "")
                elif "https://youtu.be/" in youtube_link :
                    video_id = youtube_link.replace("https://youtu.be/", "")

                return "http://video.genyoutube.net/" + video_id

            def get_download_data(link_data):
                remove_keyword = ['<span class="infow">', '<i class="glyphicon glyphicon-', '">', '</span>', '</i></span>',
                                  'video', 'volume-', '</i>', '<', '>', '/']
                for i in range(0, len(remove_keyword)):
                    link_data = link_data.replace(remove_keyword[i], "")
                vid_data = link_data.split(" ")
                vid_data[2] = vid_data[2].replace("-", " ")
                return vid_data

            def approved_vid(data, req_format="MP4", req_quality_min=720, req_quality_max=720):
                vid_format = data[0]
                vid_quality = data[1]

                remove_keyword = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                for i in range(0, len(remove_keyword)):
                    vid_quality = vid_quality.replace(remove_keyword[i], "")
                vid_quality = int(vid_quality)
                return (vid_format == req_format) and (vid_quality >= req_quality_min) and (vid_quality <= req_quality_max)

            def send_vid_option(video_option, video_links):
                title = "Youtube download"
                text = Lines.download_youtube("pick one to download")
                header_pic = Picture.header("background")

                option = len(video_option)
                if option == 1:
                    actions = [URITemplateAction(label=video_option[0], uri=str(video_links[0]))]
                elif option == 2:
                    actions = [URITemplateAction(label=video_option[0], uri=str(video_links[0])),
                               URITemplateAction(label=video_option[1], uri=str(video_links[1]))]
                elif option == 3:
                    actions = [URITemplateAction(label=video_option[0], uri=str(video_links[0])),
                               URITemplateAction(label=video_option[1], uri=str(video_links[1])),
                               URITemplateAction(label=video_option[2], uri=str(video_links[2]))]
                elif option > 3:

                    reply = []
                    reply.append(Lines.download_youtube("header"))  # remember to put \n at the end
                    for i in range(0, len(video_option)):
                        reply.append(video_option[i])
                    reply.append(Lines.download_youtube("footer"))  # remember to put \n at the front
                    reply = "\n".join(reply)

                    actions = [URITemplateAction(label=video_option[0], uri=str(video_links[0])),
                               URITemplateAction(label=video_option[1], uri=str(video_links[1])),
                               URITemplateAction(label=video_option[2], uri=str(video_links[2])),
                               MessageTemplateAction(label='Others...', text=reply)]

                buttons_template = ButtonsTemplate(title=title, text=text, thumbnail_image_url=header_pic, actions=actions)
                template_message = TemplateSendMessage(alt_text=text, template=buttons_template)
                line_bot_api.push_message(address, template_message)

            req_format,req_quality_min,req_quality_max,default = get_spec()
            video_option = []
            video_links = []

            youtube_link = get_youtube_link()
            if youtube_link == "" :
                report = Lines.download_youtube("page not found")
                line_bot_api.push_message(address, TextSendMessage(text=report))
                cont = False
            else :
                cont = True

            # if youtube link is available
            if cont :
                page_url = get_genyoutube(youtube_link)
                try:
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    cont = True
                except:
                    report = Lines.download_youtube("page not found")
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    cont = False

            # if youtube download link is available
            if cont:
                page_source_code_text = con.read()
                mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                links = mod_page.find_all("a", {"rel": "nofollow"})
                for link in links:
                    try:
                        href = link.get("href")
                        vid_keyword = "http://redirector.googlevideo.com"
                        if vid_keyword in href:
                            link_data = str(BeautifulSoup(str(link), "html.parser").find('span', {"class": "infow"}))
                            data = get_download_data(link_data)
                            if approved_vid(data,req_format,req_quality_min,req_quality_max):
                                video_option.append(" ".join(data))
                                video_links.append(href)
                    except:
                        report = Lines.download_youtube("gathering video data failed")
                        line_bot_api.push_message(address, TextSendMessage(text=report))

                if len(video_option) > 0:
                    if default :
                        report = Lines.download_youtube("send option header") % "default settings"
                    else :
                        settings = ("format : "+str(req_format)+", min : "+str(req_quality_min)+"p, max : "+str(req_quality_max)+"p")
                        report = Lines.download_youtube("send option header") % settings

                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    send_vid_option(video_option, video_links)
                else:
                    report = Lines.download_youtube("no video found")
                    line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "Youtube download"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def summonerswar_wiki(cond="default"):

        try :
            def get_search_keyword():

                keyword = [' ', 'about', 'are', 'bad', 'build', 'good', 'how', 'hows', 'i', 'idea', 'info', 'infos', 'is',
                           'kato', 'me', 'meg', 'megumi', 'people', 'rating', 'ratings', 's', 'should', 'show', 'shows',
                           'skill', 'skills', 'stat', 'stats', 'summoner', 'summoners', 'summonerswar', 'sw', 'think',
                           'thought', 'to', 'use', 'uses', 'war', 'what', 'whats', 'worth', 'worthed', 'you', 'your'
                           ]

                filtered_text = OtherUtil.filter_words(text, "sw wiki")
                filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

                return filtered_text

            def get_page(cond="default"):
                if cond == "default":
                    keyword = get_search_keyword()

                    if len(keyword) > 1:
                        search_keyword = str("%20".join(keyword))
                    elif len(keyword) == 1 :
                        search_keyword = str(keyword[0])
                    else :
                        return None

                    page_url = "https://summonerswar.co/?s=" + '('+search_keyword+')'

                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                    search_table = BeautifulSoup(str(mod_page.findAll("div", {"class": "loop list row"})), "html.parser")
                    links = search_table.find_all("a")
                    for link in links:
                        title_text = link.text.strip().lower()
                        link = link.get("href")
                        if all(word in link for word in keyword) or all(word in title_text for word in keyword):
                            return link

                elif cond == "postback":
                    found_index = [i for i, x in enumerate(text) if x == '*']
                    index_start = found_index[0] + 1
                    index_end = found_index[1]
                    link = (text[index_start:index_end])
                    return link

            def get_name(mod_page):
                name = mod_page.find("h1", {"class": "main-title"})
                return name.text.strip()

            def get_pic(mod_page):
                image_src = "https://mobilegamerhub.com/wp-content/uploads/2017/02/summoners-war.png"
                search_keyword = get_search_keyword()
                images = mod_page.find_all("img")
                for image in images:
                    image_src = image.get("src")
                    if all(word in image_src.lower() for word in search_keyword):
                        return image_src

            def get_overview(mod_page):
                overview = mod_page.find_all("span", {"class": "detail-content"})
                grade = overview[0].text.strip()
                mons_type = overview[1].text.strip()
                usage = overview[4].text.strip()
                return grade, mons_type, usage

            def get_stats(mod_page, nb):
                table = mod_page.findAll("table")
                stats = []
                maxed_stat = []

                for row in table:
                    datas = row.find_all("td")
                    for data in datas:
                        data = data.text.strip()
                        stats.append(data)

                if nb == 5:
                    important_indexs = [(0, 19), (5, 24), (10, 29), (31, 43), (32, 44), (33, 45), (34, 46),
                                        (35, 47)]  # nat 5
                elif nb == 4:
                    important_indexs = [(0, 27), (7, 34), (14, 41), (43, 55), (44, 56), (45, 57), (46, 58),
                                        (47, 59)]  # nat 4
                elif nb == 3:
                    important_indexs = [(0, 35), (9, 44), (18, 53), (55, 67), (56, 68), (57, 69), (58, 70),
                                        (59, 71)]  # nat 3
                elif nb == 2:
                    important_indexs = [(0, 43), (11, 54), (22, 65), (67, 79), (68, 80), (69, 81), (70, 82),
                                        (71, 83)]  # nat 2

                for (a, b) in important_indexs:
                    try :
                        a = stats[a]
                    except :
                        a = "[undf]"
                    try :
                        b = stats[b]
                    except :
                        b = 0
                    stat = (a, b)
                    maxed_stat.append(stat)

                return maxed_stat

            def get_rating(mod_page):
                rating_category = mod_page.find_all("div", {"class": "col-md-6 col-xs-6"})
                rating_admin = mod_page.find_all("div", {"class": "ratings-panel editor-rating"})
                rating_users = mod_page.find_all("div", {"class": "ratings-panel user-rating"})
                ratings = [("RATING", "page's", "users's")]  # WORK ON THIS PART TO GIVE BETTER DIALOGUE

                for i in range(1, len(rating_category)):
                    category = str(rating_category[i].text.strip())
                    by_admin = str(rating_admin[i - 1].text.strip())
                    by_user = str(rating_users[i - 1].text.strip())
                    rating = (category, by_admin, by_user)
                    ratings.append(rating)
                return ratings

            def get_skills(mod_page):

                """ getting the skill desc part """
                skills_data = BeautifulSoup(str(mod_page.find_all("div", {"id": "content-anchor-inner"})),"html.parser")
                skills_desc = skills_data.find_all("p")
                skill_desc_list = []
                keyword = ["skill 1", "skill 2", "skill 3", "leader skill"]
                alter_keyword = [":","turn","passive"]

                for skill in skills_desc:
                    skill = skill.text.strip()
                    if any(word in skill.lower() for word in keyword):
                        skill_desc_list.append(skill)

                    else :
                        """ special case when skill is not written / theres desc and extra useless review """
                        try : # determine if there's leader skill
                            have_leader_skill = "leader skill" in skill_desc_list[0].lower()
                        except :
                            have_leader_skill = False

                        if have_leader_skill and (len(skill_desc_list) >= 4) :
                            break
                        elif not have_leader_skill and (len(skill_desc_list)>=3) :
                            break
                        elif any(word in skill for word in alter_keyword):
                            # if there's slot, then might be missed skill info...
                            skill_desc_list.append(skill)

                """ getting the skills up part """
                skills_level = skills_data.find_all("ul")
                skill_upgrade_list = []
                for skill in skills_level:
                    skill = skill.text.strip()
                    skill_upgrade_list.append(skill)

                """ combining both of them """
                skills = []
                if "leader skill" in skill_desc_list[0].lower():
                    skill_upgrade_list.insert(0," ")

                for i in range(0, len(skill_desc_list)):
                    try :
                        is_passive = "passive" in skill_desc_list[i].lower()
                    except :
                        is_passive = False

                    try :
                        has_passive_upgrade = all(word in skill_upgrade_list[i].lower() for word in ['lv','2'])
                    except :
                        has_passive_upgrade = False

                    if is_passive and (not has_passive_upgrade) :
                            skill = (skill_desc_list[i], " ")
                    else : # not passive or passive with upgrade
                        try :
                            skill = (skill_desc_list[i], skill_upgrade_list[i])
                        except :
                            skill = (skill_desc_list[i], " ")

                    skills.append(skill)


                return skills

            def get_procons(mod_page):
                mod_page = BeautifulSoup(str(mod_page.find_all("div", {"class": "col-wrapper"})), "html.parser")
                arguments = mod_page.find_all("p")
                procons = []
                for argument in arguments:
                    argument = argument.text.strip()
                    procons.append(argument)
                return procons

            try :
                report = []
                if cond == "default":
                    page_url = get_page()
                else:
                    page_url = get_page("postback")


                if page_url == None :
                    report.append(Lines.summonerswar_wiki("no keyword found"))
                    report = "\n".join(report)
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    cont = False
                else :
                    cont = True

                if cont :
                    """ opening web page """
                    try :
                        req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                        con = urllib.request.urlopen(req)
                        cont = True
                    except :
                        report.append(Lines.summonerswar_wiki("page not found"))
                        report = "\n".join(report)
                        line_bot_api.push_message(address, TextSendMessage(text=report))
                        cont = False

                if cont :
                    """ procesing web page """
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                    name = get_name(mod_page)
                    grade, mons_type, usage = get_overview(mod_page)

                    if cond == "default":
                        title = name + "\n" + grade
                        title = title[:39]
                        button_text = Lines.summonerswar_wiki("send button header")
                        header_pic = get_pic(mod_page)

                        buttons_template = ButtonsTemplate(title=title, text=button_text, thumbnail_image_url=header_pic, actions=[
                            PostbackTemplateAction(label='Overview', data=('summoners_war_wiki overview *' + page_url + '*')),
                            PostbackTemplateAction(label='Ratings', data=('summoners_war_wiki ratings *' + page_url + '*')),
                            PostbackTemplateAction(label='Stats', data=('summoners_war_wiki stats *' + page_url + '*')),
                            PostbackTemplateAction(label='Skills', data=('summoners_war_wiki skills *' + page_url + '*'))

                        ])
                        template_message = TemplateSendMessage(alt_text=button_text, template=buttons_template)
                        line_bot_api.push_message(address, template_message)

                        button_text = Lines.summonerswar_wiki("ask detailed page")
                        buttons_template = ButtonsTemplate(text=button_text, actions=[
                            URITemplateAction(label=Labels.confirmation("yes"), uri=page_url)])

                        template_message = TemplateSendMessage(alt_text=button_text, template=buttons_template)
                        line_bot_api.push_message(address, template_message)

                    else:

                        report.append(name + " " + grade)

                        if cond == "overview":

                            procons = get_procons(mod_page)
                            pros = procons[0]
                            cons = procons[1]

                            report.append("")
                            report.append(Lines.summonerswar_wiki("overview header") % (mons_type.lower(), usage.lower()))
                            report.append("")
                            report.append(Lines.summonerswar_wiki("good points"))
                            report.append(pros)
                            report.append("")
                            report.append(Lines.summonerswar_wiki("bad points"))
                            report.append(cons)

                        elif cond == "show stats":
                            report.append("")
                            report.append(Lines.summonerswar_wiki("stats header"))

                            nb = len(grade)
                            stats = get_stats(mod_page, nb)
                            for (stat_type, stat_value) in stats:
                                stat = '{}  :  {}'.format(stat_type, stat_value)
                                report.append(stat)

                        elif cond == "show ratings":
                            report.append("")
                            ratings = get_rating(mod_page)
                            for (categ, adm, users) in ratings:
                                rating = '{}  :  {}  |  {}'.format(categ, adm, users)
                                report.append(rating)

                        elif cond == "show skills":
                            report.append("")
                            report.append(Lines.summonerswar_wiki("skills header"))
                            report.append("")

                            skills = get_skills(mod_page)
                            for (desc, skillup) in skills:
                                report.append(desc)
                                report.append("")
                                if skillup != " " : # to reduce blankspace between leaderskill and first skill
                                    report.append(skillup)
                                    report.append("")

                        report = "\n".join(report)
                        line_bot_api.push_message(address, TextSendMessage(text=report))
            except Exception as e:
                print("ERROR DEF",e)
                report = Lines.summonerswar_wiki("random errors")
                line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "SW wiki"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def weather_forcast():

        try :
            def get_search_keyword():
                keyword = ['', ' ', '?', 'about', 'afternoon', 'are', 'area', 'around', 'at', 'bad', 'be',
                           'city', 'cold', 'cond', 'condition', 'do', 'does', 'for', 'forecast', 'going',
                           'gonna', 'good', 'have', 'hot', 'how', "how's", 'in', 'information', 'is', 'it',
                           'kato', 'kato,', 'like', 'look', 'looks', 'me', 'meg', 'meg,', 'megumi', 'megumi,',
                           'morning', 'near', 'nearby', 'now', 'please', 'pls', 'rain', 'said', 'show', 'sky',
                           'sunny', 'the', 'think', 'this', 'to', 'today', 'tomorrow', 'tonight', 'weather',
                           'weathers', 'what', "what's", 'whats', 'will', 'you'
                           ]

                filtered_text = OtherUtil.filter_words(text)
                filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

                return filtered_text

            def get_lat_long():
                geo_text = text[text.find("(") + 1: text.find(")")]  # getting the coordinate only
                lat_start = geo_text.find("(") + 1
                lat_end = geo_text.find(",")
                long_start = geo_text.find(",") + 1
                long_end = geo_text.find(")")
                latitude = geo_text[lat_start:lat_end].strip()
                longitude = geo_text[long_start:long_end].strip()
                return latitude, longitude

            def is_lat_long_valid():
                use_coordinate = False
                cont = True

                if all(word in text for word in ['(', ')', ',']):  # try to use geo location
                    latitude, longitude = get_lat_long()
                    try:
                        float(latitude)
                        float(longitude)
                        use_coordinate = True  # flag if coordinate is usable
                    except:
                        cont = False
                else:
                    cont = False

                return use_coordinate,cont

            def get_city_id(keyword, database="citylist.json"):
                city_id_list = []
                city_name_list = []

                if keyword == []:  # default location is Bandung
                    nonlocal default_keyword
                    city_id_list.append(1650357)
                    default_keyword = True

                else:
                    with open(database, encoding='utf8') as city_list:
                        data = json.load(city_list)
                        found = False
                        for city in keyword:
                            for item in data:
                                if city.lower() == item['name'].lower():
                                    city_id_list.append(item['id'])
                                    city_name_list.append(item['name'])
                                    found = True
                                else:
                                    pass
                        if not (found): # second attempt
                            for city in keyword:
                                for item in data:
                                    if city.lower() in item['name'].lower():
                                        city_id_list.append(item['id'])
                                        city_name_list.append(item['name'])
                                        found = True
                                    else:
                                        pass
                        if not (found):
                            city_id_list.append("not_found")

                return city_id_list, city_name_list

            def request_type():

                if "forecast" in text.lower():
                    req_type = "forecast"
                else:
                    req_type = "weather"

                return req_type

            def send_header(city_id_list,city_name_list):
                report = []
                report.append(Lines.weatherforecast("header"))
                if len(city_id_list) > 2:
                    report.append(" ")
                    report.append(Lines.weatherforecast("city search : 3 or more cities"))
                    for name in city_name_list:
                        report.append(name)
                    report.append(" ")
                elif len(city_name_list) == 2:
                    report.append(" ")
                    report.append(Lines.weatherforecast("city search : 2 cities") % city_name_list[1])
                    report.append(" ")

                if default_keyword :
                    report.append(" ")
                    report.append(Lines.weatherforecast("default location") % default_location)

                report = "\n".join(report)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def get_detail_page(city_id,city_name):
                if city_id != "not_found" :
                    owm_detail_page = "http://openweathermap.org/city/" + str(city_id)
                else :
                    city_id_list,city_name_list = get_city_id(city_name)
                    city_id = city_id_list[0]
                    owm_detail_page = "http://openweathermap.org/city/" + str(city_id)

                return owm_detail_page

            def send_weather():
                try:
                    city_name = weather_data["name"]
                except:
                    print("can't get city name (weather)")
                    city_name = "Undefined"
                try:
                    city_weather_type = weather_data["weather"][0]['main']
                    city_weather_description = weather_data["weather"][0]['description']
                except:
                    print("can't get weather data (weather)")
                    city_weather_type = "Undefined"
                    city_weather_description = "Undefined"
                try:
                    city_temp = weather_data["main"]['temp']
                    city_temp_min = weather_data["main"]['temp_min']
                    city_temp_max = weather_data["main"]['temp_max']
                except:
                    print("can't get temp data (weather)")
                    city_temp = "Undefined"
                    city_temp_min = "Undefined"
                    city_temp_max = "Undefined"

                """ Re-formating data to send """
                send_header(city_id_list, city_name_list)
                owm_detail_page = get_detail_page(city_id, city_name)
                title = "[ " + city_name + " ]"
                button_text = city_weather_description + " [ " + str(city_temp) + "°C ]" + "\n" + "Temp vary from " + str(city_temp_min) + "°C to " + str(city_temp_max) + "°C"
                header_pic = Picture.weatherforecast(city_weather_type.lower())
                buttons_template = ButtonsTemplate(title=title, text=button_text[:60], thumbnail_image_url=header_pic,
                                                   actions=[URITemplateAction(label='See detail info', uri=owm_detail_page)])

                """ Sending button and report """
                template_message = TemplateSendMessage(alt_text=button_text, template=buttons_template)
                line_bot_api.push_message(address, template_message)

                report = Lines.weatherforecast_tips(city_weather_type.lower())
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_forecast():
                try:
                    city_name = weather_data['city']['name']
                except:
                    city_name = "Undefined"

                city_weather_type = []
                city_weather_description = []
                city_temp = []
                city_temp_min = []
                city_temp_max = []
                city_date = []

                for i in range(0, 5):  # 5 is the max number of carousels allowed by line
                    try:
                        city_weather_type.append(weather_data['list'][i]['weather'][0]['main'])
                    except:
                        city_weather_type.append(" ")
                    try:
                        city_weather_description.append(weather_data['list'][i]['weather'][0]['description'])
                    except:
                        city_weather_description.append(" ")
                    try:
                        city_temp.append(weather_data['list'][i]['main']['temp'])
                    except:
                        city_temp.append(" ")
                    try:
                        city_temp_min.append(weather_data['list'][i]['main']['temp_min'])
                    except:
                        city_temp_min.append(" ")
                    try:
                        city_temp_max.append(weather_data['list'][i]['main']['temp_max'])
                    except:
                        city_temp_max.append(" ")
                    try:
                        city_date.append(weather_data['list'][i]['dt_txt'])
                    except:
                        city_date.append(" ")

                """ Re-formating data to send """
                title = []
                for i in range(0, 5):
                    title.append(city_name + "  " + city_date[i][5:16])

                owm_detail_page = get_detail_page(city_id, city_name)
                carousel_text = []
                for i in range(0, 5):
                    carousel_text.append(
                        city_weather_description[i] + " [ " + str(city_temp[i]) + "°C ]" + "\n" + "Temp vary from " + str(
                            city_temp_min[i]) + "°C to " + str(city_temp_max[i]) + "°C")

                header_pic = []
                for i in range(0, 5):
                    header_pic.append(Picture.weatherforecast(city_weather_type[i].lower()))

                send_header(city_id_list, city_name_list)

                carousel_template = CarouselTemplate(columns=[
                    CarouselColumn(title=title[0], text=carousel_text[0][:60], thumbnail_image_url=header_pic[0], actions=[
                        URITemplateAction(label='See detail..', uri=owm_detail_page)]),
                    CarouselColumn(title=title[1], text=carousel_text[1][:60], thumbnail_image_url=header_pic[1], actions=[
                        URITemplateAction(label='See detail..', uri=owm_detail_page)]),
                    CarouselColumn(title=title[2], text=carousel_text[2][:60], thumbnail_image_url=header_pic[2], actions=[
                        URITemplateAction(label='See detail..', uri=owm_detail_page)]),
                    CarouselColumn(title=title[3], text=carousel_text[3][:60], thumbnail_image_url=header_pic[3], actions=[
                        URITemplateAction(label='See detail..', uri=owm_detail_page)]),
                    CarouselColumn(title=title[4], text=carousel_text[4][:60], thumbnail_image_url=header_pic[4], actions=[
                        URITemplateAction(label='See detail..', uri=owm_detail_page)]),
                ])

                """ Sending carousel and report """
                template_message = TemplateSendMessage(alt_text=carousel_text[0], template=carousel_template)
                line_bot_api.push_message(address, template_message)

            """ basic flags and variable """
            owm_key_list = [
                "4d7355141b9838b1ac5799247095f61d", "48d8f519014923226491c62098640295", "32efe2580b5ec0d2767e55a9c2d581d1",
                "79f9585bf82fb571946ce4b0f1101665", "30128b74832097ef3ed57c642d56ebe8", "eb1b1af47cbca59d0b17c729071d1088",
                "aaae7f35207db74b0bde707b2ff54c81", "adcb9836b69d955ec042ffc8d6300feb", "a16c1867404a31a617abb68f86ffbedc"
            ]
            open_weather_map_key = random.choice(owm_key_list)
            default_location = "Bandung"
            cont = True
            use_coordinate = False
            use_city_id = False
            default_keyword = False


            """ getting keyword and city id based on text """
            keyword = get_search_keyword()
            city_id_list, city_name_list = get_city_id(keyword)
            city_id = city_id_list[0]
            request_type = request_type()

            # If there is at least one city which id match the keyword given,
            if city_id != "not_found":
                use_city_id = True

            # Wrong keyword or the city is not available, thus try to use geo location
            else:
                use_coordinate,cont = is_lat_long_valid() # create flags by validating latitude and longitude

            if cont: # If either city id or lat long is available
                owm_call_head = "http://api.openweathermap.org/data/2.5/" + request_type
                owm_call_tail = "&units=metric&appid=" + str(open_weather_map_key)

                if use_city_id:
                    owm_weather_call = owm_call_head + "?id=" + str(city_id) + owm_call_tail
                elif use_coordinate:
                    owm_weather_call = owm_call_head + "?lat=" + str(latitude) + "&lon=" + str(longitude) + owm_call_tail

                weather_data = requests.get(owm_weather_call).json()

                # only get the condition right now ( 1 data each )
                if request_type == "weather":
                    send_weather()

                # get 5 conditions every 3 hours ( data stored as list )
                elif request_type == "forecast":
                    send_forecast()

        except Exception as exception_detail:
            function_name = "Weather forecast"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def itb_arc_database():

        try:
            def get_keyword():

                index_start = text.find("'")+1
                index_end = text.rfind("'")
                keyword = text[index_start:index_end]

                return keyword

            def get_category():
                is_default_category = False

                if any(word in text for word in ["student", "students", "stud", "std", "stds", "studnt", "stdnt"]):
                    category = "student"
                elif any(word in text for word in ["lecturer", "lecture", "prof", "professor", "lctrer", "lctr", "dr"]):
                    category = "lecturer"
                elif any(word in text for word in ["major", "faculty", "fclty", "fclt", "mjr", "maj", "fac", "fac"]):
                    category = "major"
                else:
                    category = "student"
                    is_default_category = True

                return category, is_default_category

            def get_student_info():

                if search_result_count > 5:
                    max_data = 5
                else:
                    max_data = search_result_count

                for i in range(0, max_data):
                    student_name = ARC_ITB_api_data['result'][i]['fullname']
                    student_nim = ARC_ITB_api_data['result'][i]['nim']
                    student_major = ARC_ITB_api_data['result'][i]['major']['title']
                    student_faculty = ARC_ITB_api_data['result'][i]['major']['faculty']['title']
                    student_major_year = ARC_ITB_api_data['result'][i]['year']

                    search_result.append("NIM : " + str(student_nim))
                    search_result.append(student_name)
                    search_result.append(student_major + " [ " + str(student_major_year) + " ]")
                    search_result.append(student_faculty)
                    search_result.append(" ")

                search_result.append(Lines.itb_arc_database("footer"))

            def get_lecturer_info():

                if search_result_count > 5:
                    max_data = 5
                else:
                    max_data = search_result_count

                for i in range(0, max_data):
                    lecturer_name = ARC_ITB_api_data['result'][i]['fullname']
                    lecturer_nip = ARC_ITB_api_data['result'][i]['nip']

                    search_result.append(lecturer_name)
                    search_result.append("NIP : " + str(lecturer_nip))
                    search_result.append(" ")
                search_result.append(Lines.itb_arc_database("footer"))

            def get_major_info():

                if search_result_count > 5:
                    max_data = 5
                else:
                    max_data = search_result_count

                for i in range(0, max_data):
                    major_name = ARC_ITB_api_data['result'][i]['title']
                    major_code = ARC_ITB_api_data['result'][i]['code']
                    major_faculty = ARC_ITB_api_data['result'][i]['faculty']['title']

                    search_result.append("[ " + str(major_code) + " ] " + major_name)
                    search_result.append(major_faculty)
                    search_result.append(" ")
                search_result.append(Lines.itb_arc_database("footer"))

            def send_header():
                report = []

                report.append(Lines.itb_arc_database("header") % itb_keyword)
                if is_default_category:
                    report.append(" ")
                    report.append(Lines.itb_arc_database("default category"))

                report = "\n".join(report)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_result_count():
                report = []

                if search_result_count > 1:
                    report.append(Lines.itb_arc_database("count result plural") % (str(search_result_count)))
                    if search_result_count > 5:
                        report.append(" ")
                        report.append(Lines.itb_arc_database("only send top 5"))
                elif search_result_count == 1:
                    report.append(Lines.itb_arc_database("count result one"))
                else:
                    report.append(Lines.itb_arc_database("not found"))

                report = "\n".join(report)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_detail_info():
                report = "\n".join(search_result)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            cont = True  # default flag

            itb_keyword = get_keyword()
            search_category, is_default_category = get_category()

            ARC_api_call = "https://nim.arc.itb.ac.id/api//search/" + search_category + "/?keyword=" + itb_keyword + "&page=1&count=30"
            try :
                ARC_ITB_api_data = requests.get(ARC_api_call).json()
                search_result_count = ARC_ITB_api_data['totalCount']  # get the total result count
            except :
                report = Lines.itb_arc_database("database unreachable")
                line_bot_api.push_message(address, TextSendMessage(text=report))
                cont = False

            # If the data is successfully retrieved
            if cont :
                search_result = []
                send_header()
                send_result_count()

                # continue only if the result is available
                if search_result_count > 0:

                    # re - format the data to make it more beautiful
                    try :
                        if search_category == "student":
                            get_student_info()
                        elif search_category == "lecturer":
                            get_lecturer_info()
                        elif search_category == "major":
                            get_major_info()
                        send_detail_info()

                    except :
                        report = Lines.itb_arc_database("data formatting failed")
                        line_bot_api.push_message(address, TextSendMessage(text=report))


        except Exception as exception_detail:
            function_name = "ITB ARC database"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def anime_download_link():

        try :
            def get_keyword():
                try:
                    index_start = text.find("'") + 1
                    index_stop = text.rfind("'")
                    keyword = text[index_start:index_stop]
                    return keyword
                except:
                    return "not_found"

            def get_start_ep():
                is_default_start = True

                keyword = ['', ' ', '?', 'about', 'are', 'at', 'be', 'do', 'does', 'for', 'gonna', 'have',
                           'how', "how's", 'in', 'information', 'is', 'it', 'kato', 'kato,', 'like', 'me',
                           'meg', 'meg,', 'megumi', 'megumi,', 'now', 'please', 'pls', 'show', 'the', 'think',
                           'this', 'to', 'what', "what's", 'whats', 'will', 'you']

                filtered_text = OtherUtil.filter_words(text)
                filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

                keyword = ["ep", "epi", "epis", "ep.", "episode", "chap", "ch", "chapter", "epid"]

                for i in range(0, len(filtered_text)):
                    if any(word in filtered_text[i] for word in keyword):
                        try:
                            start_ep = int(filtered_text[i + 1])
                            is_default_start = False
                        except:
                            pass

                if is_default_start:
                    return 1, True
                else:
                    return start_ep, False

            def get_host_source():
                is_default_host = True
                keyword = ['', ' ', '?', 'about', 'are', 'at', 'be', 'do', 'does', 'for', 'gonna', 'have',
                           'how', "how's", 'in', 'information', 'is', 'it', 'kato', 'kato,', 'like', 'me',
                           'meg', 'meg,', 'megumi', 'megumi,', 'now', 'please', 'pls', 'show', 'the', 'think',
                           'this', 'to', 'what', "what's", 'whats', 'will', 'you']
                anime_hostlist = Database.anime_hostlist

                filtered_text = OtherUtil.filter_words(text)
                filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

                keyword = ["from", "fr", "source", "src", "frm", "sou"]

                for i in range(0, len(filtered_text)):
                    if any(word in filtered_text[i] for word in keyword):
                        try:
                            host_name = (filtered_text[i + 1])
                            for host in anime_hostlist:
                                if host_name in host:
                                    host_id = anime_hostlist[host]
                                    is_default_host = False

                        except:
                            pass

                if is_default_host:
                    return 99, True
                else:
                    return host_id, False

            def get_anime_pasted_link(keyword):

                if "pasted.co" in keyword : # enable direct link
                    return keyword
                else :
                    animelist = Database.animelist
                    try :
                        for anime in animelist:
                            if keyword in anime.lower():
                                return animelist[anime]
                    except :
                        pass
                    return "title not found"

            def get_primary_download_link_list(anime_pasted_link):
                page_url = anime_pasted_link + "/new.php"
                req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                con = urllib.request.urlopen(req)
                page_source_code_text = con.read()
                mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                datas = mod_page.find("textarea", {"class": "pastebox rounded"})
                download_link_list = datas.text.split("\n")  # get the list of links

                download_link_list_filtered = []
                for link in download_link_list:
                    if "http" in link:
                        download_link_list_filtered.append(link)

                return download_link_list_filtered

            def get_file_id(link):
                mirror_creator_keyword = "https://www.mirrorcreator.com/files/"
                index_start = link.find(mirror_creator_keyword) + len(mirror_creator_keyword)
                index_stop = index_start + 8
                file_id = link[index_start:index_stop]
                return str(file_id)

            def get_final_download_link(primary_download_link_list, start_ep=1):
                result = []
                success = False

                if start_ep > len(primary_download_link_list):  # check if the starting episode is available
                    result.append(Lines.anime_download_link("starting episode not aired"))
                    result.append(Lines.anime_download_link("send latest episode count") % str(len(primary_download_link_list)))


                else:
                    for i in range(start_ep - 1, (len(primary_download_link_list))):
                        current_ep = i + 1

                        primary_download_link = primary_download_link_list[i]
                        try:
                            index_start = primary_download_link.find("http")
                            shortened_link = primary_download_link[index_start:].strip()
                            download_link, status = unshortenit.unshorten_only(shortened_link)
                            file_id = get_file_id(download_link)
                        except:
                            pass

                        page_url = "https://www.mirrorcreator.com/downlink.php?uid=" + file_id
                        post_data = dict(uid=file_id, hostid=hostid)  # 99 is for dropjify , uid is the file name also
                        req_post = requests.post(page_url, data=post_data)
                        page_source_code_text_post = req_post.text
                        mod_page = BeautifulSoup(page_source_code_text_post, "html.parser")
                        final_download_link = mod_page.find("a", {"target": "_blank"})
                        if final_download_link is not None :
                            result.append("Ep. " + str(current_ep) + " : " + final_download_link.get("href"))
                            success = True
                        else :
                            result.append(Lines.anime_download_link("host not available") % (str(current_ep)))



                return result,success

            def send_header(cond="found"):
                report = []

                if cond == "found":
                    report.append(Lines.anime_download_link("header") % keyword)
                    if is_default_start:
                        report.append(" ")
                        report.append(Lines.anime_download_link("default start ep"))
                    if is_default_host:
                        report.append(" ")
                        report.append(Lines.anime_download_link("default host"))

                elif cond == "not_found":
                    report.append(Lines.anime_download_link("keyword not found"))

                report = "\n".join(report)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_final_result(result,success,is_send_animelist):
                if success : # title is found and episode is found
                    result.insert(0," ")
                    result.insert(0,Lines.anime_download_link("header for result"))

                report = "\n".join(result)
                line_bot_api.push_message(address, TextSendMessage(text=report))

                if is_send_animelist :  # only send if title is not found
                    send_animelist()

            def send_animelist():

                title = "Cyber12 Anime"
                button_text = Lines.anime_download_link("send animelist")
                link_2017 = "https://www.facebook.com/notes/cyber12-official-group/2017-on-going-anime-update/1222138241226544"
                link_2016 = "https://www.facebook.com/notes/cyber12-official-group/on-going-anime-update/976234155816955"

                buttons_template = ButtonsTemplate(title=title, text=button_text, actions=[
                    URITemplateAction(label='2017 Anime Update', uri=link_2017),
                    URITemplateAction(label='2016 Anime Update', uri=link_2016)])
                template_message = TemplateSendMessage(alt_text=button_text, template=buttons_template)
                line_bot_api.push_message(address, template_message)


            keyword = get_keyword()
            if keyword != "not_found" :  # flag to check if keyword is available
                start_ep, is_default_start = get_start_ep()
                hostid, is_default_host = get_host_source()
                send_header()

                anime_pasted_link = get_anime_pasted_link(keyword)
                if anime_pasted_link != "title not found" :
                    primary_download_link_list = get_primary_download_link_list(anime_pasted_link)
                    result,is_success = get_final_download_link(primary_download_link_list, start_ep)
                    is_send_animelist = False

                else : # the title is not found
                    result = [Lines.anime_download_link("title not found") % keyword]
                    is_success = False
                    is_send_animelist = True

                send_final_result(result, is_success,is_send_animelist)

            else:
                send_header("not_found")
                send_animelist()

        except Exception as exception_detail:
            function_name = "Anime Download Link"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def translate_text():

        try :
            class AzureAuthClient(object):
                """
                Provides a client for obtaining an OAuth token from the authentication service
                for Microsoft Translator in Azure Cognitive Services.
                """

                def __init__(self, client_secret):
                    """
                    :param client_secret: Client secret.
                    """

                    self.client_secret = client_secret
                    # token field is used to store the last token obtained from the token service
                    # the cached token is re-used until the time specified in reuse_token_until.
                    self.token = None
                    self.reuse_token_until = None

                def get_access_token(self):
                    '''
                    Returns an access token for the specified subscription.
                    This method uses a cache to limit the number of requests to the token service.
                    A fresh token can be re-used during its lifetime of 10 minutes. After a successful
                    request to the token service, this method caches the access token. Subsequent
                    invocations of the method return the cached token for the next 5 minutes. After
                    5 minutes, a new token is fetched from the token service and the cache is updated.
                    '''

                    if (self.token is None) or (datetime.utcnow() > self.reuse_token_until):
                        token_service_url = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'

                        request_headers = {'Ocp-Apim-Subscription-Key': self.client_secret}

                        response = requests.post(token_service_url, headers=request_headers)
                        response.raise_for_status()

                        self.token = response.content
                        self.reuse_token_until = datetime.utcnow() + timedelta(minutes=5)

                    return self.token

            def GetTextTranslation(finalToken, textToTranslate, fromLangCode, toLangCode):

                # Call to Microsoft Translator Service
                headers = {"Authorization ": finalToken}
                translateUrl = "http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&from={}&to={}".format(
                    textToTranslate, fromLangCode, toLangCode)

                translationData = requests.get(translateUrl, headers=headers)
                # parse xml return values
                translation = ElementTree.fromstring(translationData.text.encode('utf-8'))

                # display translation
                return translation.text

            def get_text():
                if "'" in text:
                    index_start = text.find("'") + 1
                    index_stop = text.rfind("'")
                    keyword = text[index_start:index_stop]
                    return keyword
                return ""

            def get_language(cond):
                # remove the text to translate, to minimize errors
                index_start = text.find("'") + 1
                index_stop = text.rfind("'")
                crop_text = text.replace(text[index_start:index_stop], '')

                keyword = ['', ' ', '?', 'about', 'are', 'at', 'be', 'do', 'does', 'for', 'gonna', 'have',
                           'how', "how's", 'information', 'is', 'it', 'kato', 'kato,', 'like', 'me',
                           'meg', 'meg,', 'megumi', 'megumi,', 'now', 'please', 'pls', 'show', 'the', 'think',
                           'this', 'what', "what's", 'whats', 'will', 'you']

                filtered_text = OtherUtil.filter_words(crop_text)
                filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

                if cond == "from":
                    specific_keyword = ['from', 'fr']
                elif cond == "to":
                    specific_keyword = ['in', 'to']

                found = False
                try:
                    for i in range(0, len(filtered_text) + 1):
                        if filtered_text[i] in specific_keyword:
                            language = (filtered_text[i + 1])
                            found = True
                            return language, found
                except:
                    pass

                return "", found

            def get_available_language():
                page_url = "https://msdn.microsoft.com/en-us/library/hh456380.aspx"
                req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                con = urllib.request.urlopen(req)
                page_source_code_text = con.read()
                mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                code_table = mod_page.find_all("td", {"data-th": "Language Code"})
                name_table = mod_page.find_all("td", {"data-th": "English Name"})

                language_table = {}
                # create dictionary of language available
                for i in range(0, len(code_table)):
                    language_code = code_table[i].text.strip()
                    language_name = name_table[i].text.strip()
                    language_table[language_name] = language_code

                return language_table

            def get_language_code(available_language, keyword):

                if keyword != "":

                    for key in available_language:  # if the keyword is already in form of code
                        if keyword in available_language[key].lower():
                            return available_language[key],key

                    for key in available_language:  # else if the keyword is in form of name
                        if keyword in key.lower():
                            return available_language[key],key

                return "",""

            cont = True  # create continue-flag
            result = []

            textToTranslate = get_text()

            # if the text is not available
            if textToTranslate == "":
                cont = False
                result.append(Lines.translate_text("text to translate not found"))

            # if text to translate is available
            if cont:
                available_language = get_available_language()

                # extract from-to language from the text
                from_lang, is_from_lang_found = get_language("from")
                to_lang, is_to_lang_found = get_language("to")
                from_lang_code,from_lang = get_language_code(available_language, from_lang)

                # if destination language is found
                if is_to_lang_found:
                    to_lang_code,to_lang = get_language_code(available_language, to_lang)

                # destination language not found
                else:
                    to_lang = "english"
                    to_lang_code = "en"
                    result.append(Lines.translate_text("destination language not found"))

            # if the destination language is found
            if cont:

                # if destination language is available
                if to_lang_code != '':
                    azure_keys = ['1c3ea2f61de74a4f8d3bdcbe4cce7316', '20039c3da1074c9bba90ebd7600f1381']
                    client_secret = random.choice(azure_keys)
                    auth_client = AzureAuthClient(client_secret)
                    raw_bearer_token = str(auth_client.get_access_token())
                    bearer_token = 'Bearer ' + raw_bearer_token[2:-1]
                    translated_text = GetTextTranslation(bearer_token, textToTranslate, from_lang_code, to_lang_code)
                    translated_text = translated_text.lower()

                # destination language not available
                else:
                    cont = False
                    result.append(Lines.translate_text("destination language not available") % to_lang)

            # if the destination language is available
            if cont:
                if textToTranslate != translated_text.lower():
                    result.append(Lines.translate_text("send translated").format(textToTranslate, to_lang, translated_text))
                else:
                    result.append(Lines.translate_text("already in that language") % to_lang)

            report = "\n".join(result)
            line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "Translate"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    """====================== Sub Function List ============================="""

    @staticmethod
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

    @staticmethod
    def join():

        reply = Lines.join("join")
        line_bot_api.reply_message(token, TextSendMessage(text=reply))
        report = Lines.join("report")
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    @staticmethod
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

    @staticmethod
    def tag_notifier(event):
        if any(word in text for word in Lines.jessin()):
            try :
                sender = line_bot_api.get_profile(event.source.user_id).display_name
            except :
                sender = "someone"
            report = Lines.tag_notifier() % (sender,original_text)
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    @staticmethod
    def notyetcreated():
        reply = Lines.notyetcreated()
        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    @staticmethod
    def false():
        reply = Lines.false()
        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    @staticmethod
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

    @staticmethod
    def removed(event):
        try :
            user_id = event.source.user_id
            user = userlist[user_id]
        except :
            user = "someone"

        report = Lines.removed("report") % (user)
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def TEST():
        return


class OtherUtil:

    @staticmethod
    def remove_symbols(word, cond="default"):
        """ Function to remove symbols from text """

        # Several type of symbol list
        if cond == "default":
            symbols = "!@#$%^&*()+=-`~[]{}\|;:'/?.>,<\""
        elif cond == "for wiki search":
            symbols = "!@#$%^&*+=-`~[]{}\|;:/?.>,<\""
        elif cond == "sw wiki":
            symbols = "1234567890!@#$%^&*()_+=-`~[]{}\|';:/?.>,<\""
        else:
            symbols = "!@#$%^&*()+=-`~[]{}\|;:'/?.>,<\""

        # symbols removal process
        for i in range(0, len(symbols)):
            word = word.replace(symbols[i], "")
        if len(word) > 0:
            return word

    @staticmethod
    def filter_words(text, cond="default"):
        """ Function to filter text from symbols, use remove_symbols function """

        split_text = text.split(" ")
        filtered_text = []
        for word in split_text:
            new_word = OtherUtil.remove_symbols(word, cond)
            if new_word is not None:
                filtered_text.append(new_word)

        return filtered_text

    @staticmethod
    def filter_keywords(text, keyword):
        """ Function to remove keywords (listed in a list) if it exist in the text """

        while any(word in text for word in keyword):
            for word in text:
                if word in keyword:
                    text.remove(word)
        return text

    @staticmethod
    def random_error(function_name,exception_detail):
        """ Function to serve as last resort logger when unexpected error happened.
        It send the exception via line push to Dev """

        # Report to let group or other normal user know that something unexpected happened
        report = Lines.dev_mode_general_error("common")
        line_bot_api.push_message(address, TextSendMessage(text=report))

        # Send back up notification to Dev, to let Dev know that something unexpected happened
        if address != jessin_userid:
            report = (Lines.dev_mode_general_error("dev") % (function_name,exception_detail))
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

"""========================================== End of Function List ================================================"""

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()


    app.run(debug=options.debug, port=options.port)

