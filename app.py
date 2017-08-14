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
import re

import requests
import urllib
import urllib.request
import Database
import unshortenit
import json
import apiai
import wikipedia

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
api_ai_access_token = '4ead94fa71234f82af81f8e92e72962a'
api_ai_access_token_megumi_II = "0e51518979fe4d7eba6b09d4d5ae0d41"
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

userlist = Database.userlist

userlist_update_count = 0
tag_notifier_on = True
MEGUMI_ONLINE = True


@app.route("/callback", methods=['POST'])
def callback():
    """ Get X-Line-Signature header value """

    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    print(body)

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
    else:
        address = event.source.user_id

    return address


def update_user_list(event):
    """ Function to notify if the userlist is updated TEMPORARILY """
    global userlist, userlist_update_count

    # If the add event come from personal chat
    if isinstance(event.source, SourceUser):
        # Get the list count before update
        userlist_init_count = len(userlist.keys())

        try:
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
                    for dev_user in Database.devlist:
                        line_bot_api.push_message(dev_user, template_message)

                    # Send report contain new user only
                    report = str("New user : \n'"+user_id+"': '"+user+"'")
                    for dev_user in Database.devlist:
                        line_bot_api.push_message(dev_user, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "Sending Userlist notification"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    """ Function to handle event that is a text message """

    global token, original_text, text, jessin_userid, user, tag_notifier_on, api_ai_response

    # Dev / your user id
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"

    # Get general information from event
    original_text = event.message.text
    text = original_text.lower()
    token = event.reply_token
    get_receiver_addr(event)
    update_user_list(event)

    if MEGUMI_ONLINE:

        # If the text contain calling
        if any(word in text for word in Lines.megumi()):

            # Enable direct pass to rules mode
            # megumi_bot_mode = "bot" in text[:5]

            # Try to use rules type action-mapping
            megumi_action = OtherUtil.function_rules_based_mapping(event)
            OtherUtil.megumi_logger(megumi_action, "Rules")
            print("ACTION :", megumi_action, "BY RULES")

            # Send the input text to API.AI for further natural language processing
            if megumi_action == "Function_false":
                api_ai_response = OtherUtil.api_ai(api_ai_access_token, text)
                try:
                    megumi_action = api_ai_response["result"]["action"]
                    print("ACTION :", megumi_action)
                except:
                    megumi_action = "Function_false"
                OtherUtil.megumi_logger(megumi_action, "AIAPI")

            # If API.AI failed again, try to check whether it's a default chat type input by sending to megumi II
            if megumi_action == "Function_false":
                api_ai_response = OtherUtil.api_ai(api_ai_access_token_megumi_II, text)
                try:
                    megumi_action = api_ai_response["result"]["action"]
                    print("ACTION :", megumi_action, "BY MEGUMI II")
                except:
                    megumi_action = "Function_false"

            # List of command available by sending text message
            if megumi_action == "Function_random_integer"           : Function.rand_int()
            elif megumi_action == "Function_choose_one"             : Function.choose_one_simple()
            elif megumi_action == "Function_date_time"              : Function.time_date()
            elif megumi_action == "Function_weather_forecast"       : Function.weather_forecast()
            elif megumi_action == "Function_show_cinema_schedule"   : Function.show_cinema_movie_schedule()
            elif megumi_action == "Function_anime_download_link"    : Function.anime_download_link()
            elif megumi_action == "Function_summoners_war_wiki"     : Function.summonerswar_wiki()
            elif megumi_action == "Function_itb_arc_database"       : Function.itb_arc_database()
            elif megumi_action == "Function_translate"              : Function.translate_text()
            elif megumi_action == "Function_wiki_search"            : Function.wiki_search()
            elif megumi_action == "Function_show_manual"            : Function.show_manual()
            elif megumi_action == "Function_download_youtube"       : Function.download_youtube()
            elif megumi_action == "Function_echo"                   : Function.echo()
            elif megumi_action == "Function_send_invite"            : Function.send_invite(event)
            elif megumi_action == "Function_report_bug"             : Function.report_bug(event)
            elif megumi_action == "Function_leave"                  : Function.leave(event)
            elif megumi_action == "Function_stalk_instagram"        : Function.stalk_instagram()
            elif megumi_action == "Function_play_music"             : Function.play_music()
            elif megumi_action == "Function_hoax_analyser"          : Function.hoax_or_fact()

            elif megumi_action == "Enable_dev_mode"                 : Function.dev_authority_check(event)
            elif megumi_action == "Dev_mode_print_userlist"         :
                if Function.dev_authority_check(event)                  : Function.dev_print_userlist()
            elif megumi_action == "Dev_mode_set_tag_notifier"       :
                if Function.dev_authority_check(event)                  : Function.dev_mode_set_tag_notifier()
            elif megumi_action == "Dev_mode_print_logger"       :
                if Function.dev_authority_check(event)                  : Function.dev_print_megumi_logger()

            elif megumi_action == "Function_false"                  : Function.false()
            else                                                    : Function.send_default_reply()

    # If megumi's in partial offline mode ( for temp development )
    else:
        report = Lines.general_lines("offline")
        line_bot_api.push_message(address, TextSendMessage(text=report))

    # Special tag / mention function
    if tag_notifier_on:
        Function.tag_notifier(event)

# @handler.add(MessageEvent, message=StickerMessage)
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

# @handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
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
    if MEGUMI_ONLINE:

        if original_text == 'ping':
            line_bot_api.reply_message(token, TextSendMessage(text='pong'))

        elif all(word in text for word in ["confirmation invitation"]):
            if all(word in text for word in ['confirmation invitation : yes'])              : Function.invite_respond(event, "yes")
            elif all(word in text for word in ['confirmation invitation : no'])             : Function.invite_respond(event, "no")
            elif all(word in text for word in ['confirmation invitation : pending'])        : Function.invite_respond(event, "pending")

        elif all(word in text for word in ["request", "cinema list please"])            :
            if all(word in text for word in ["xxi"])                                        : Function.show_cinema_list("xxi")
            elif all(word in text for word in ["cgv"])                                      : Function.show_cinema_list("cgv")

        elif all(word in text for word in ["summoners_war_wiki"])                       :
            if all(word in text for word in ["overview"])                                   : Function.summonerswar_wiki("overview")
            elif all(word in text for word in ["ratings"])                                  : Function.summonerswar_wiki("show ratings")
            elif all(word in text for word in ["stats"])                                    : Function.summonerswar_wiki("show stats")
            elif all(word in text for word in ["skills"])                                   : Function.summonerswar_wiki("show skills")

        elif all(word in text for word in ["show megumi manual"])                       : Function.show_manual()
        elif all(word in text for word in ["manual : "])                                : Function.show_manual("postback")

        elif all(word in text for word in ["megumi dev mode print userlist"])           :
            if Function.dev_authority_check(event)                                          :
                if all(word in text for word in ["print", "userlist"])                          : Function.dev_print_userlist()
                else                                                                            : Function.false()

    # If megumi's in partial offline mode ( for temp development )
    else:
        report = Lines.general_lines("offline")
        line_bot_api.push_message(address, TextSendMessage(text=report))


@handler.add(JoinEvent)
def handle_join(event):
    """ Function to handle join event (when bot join a chat room / group) """

    global token, jessin_userid

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
        """ Function to return random integer between the minimum and maximum number given in text.
        Usage example : meg, pick one num from 1 to 11 """

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
        """ Function to echo whatever surrounded by single apostrophe (').
         Usage example : Meg, try to say 'I love you <3' """

        try:
            # Find the index of apostrophe
            index_start = text.find("'") + 1
            index_stop = text.rfind("'")

            # Determine whether 2 apostrophe are exist and the text exist
            text_to_echo_available = (index_stop - index_start) >= 1

            # If there are at least 2 apostrophes found and the text (which should be echo-ed) is found as well
            if text_to_echo_available:
                echo_text = text[index_start:index_stop]
                report = Lines.echo("success") % echo_text

            # If the text is not found
            else:
                report = Lines.echo("failed")

            # Send the result
            line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "echo"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def choose_one_simple():
        """ Function to return one random item from listed items.
         Usage example : Meg, choose one between #pasta and #pizza """

        try:
            def get_options(tag):
                """ Function to return a list of found options """

                found = []
                split_text = text.split(" ")
                for word in split_text:

                    # If the word contain the item tag
                    if tag in word:
                        word = word.replace(tag, "")
                        is_word_valid = (word is not None) and (word != "")

                        # If the word is not None and not empty
                        if is_word_valid:
                            found.append(word)

                return found

            item_tag = '#'
            found_options = get_options(item_tag)

            # If the option(s) is/are available
            if len(found_options) > 0:
                result = random.choice(found_options)
                report = Lines.choose_one("success") % str(result)

            # Else if the options is not valid or not available
            else:
                report = Lines.choose_one("fail")

            line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "Choose one"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def time_date():
        """ Function to get the time and date from server.
         Usage example : Meg, what time is it in gmt +4 ?? """

        try:
            def find_gmt(default_gmt):
                """ Function to return specific gmt if listed in text """

                keyword = ['', ' ', '?', 'about', 'are', 'at', 'be', 'do', 'does', 'for', 'gonna', 'have',
                           'how', "how's", 'in', 'information', 'is', 'it', 'kato', 'kato,', 'like', 'me',
                           'meg', 'meg,', 'megumi', 'megumi,', 'now', 'please', 'pls', 'show', 'the', 'think',
                           'this', 'to', 'what', "what's", 'whats', 'will', 'you'
                           ]
                filtered_text = OtherUtil.filter_words(text, cond="date and time")
                filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

                # Initial state for timezone
                timezone = default_gmt

                keyword = ["gmt"]
                # Search for number which follow 'gmt' in text
                for i in range(0, len(filtered_text)):

                    # If the keyword is found
                    if any(word in filtered_text[i] for word in keyword):
                        try:
                            timezone = int(filtered_text[i + 1])
                            return timezone
                        except Exception:
                            # When user said 'time in gmt' it means gmt +0
                            timezone = 0

                return timezone

            def valid_gmt(gmt):
                """ Return boolean whether the GMT is valid or not """

                if (gmt > 12) or (gmt < (-12)):
                    return False
                else:
                    return True

            def ordinal(n):
                """ Function to return an ordinal style of a number """
                return str("%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4]))

            def convert_am_pm(hh):
                """ Function to change 24 hours format into 12 hours format with Am or Pm """

                am_pm = "am"

                if int(hh) > 12:
                    hh = int(hh)
                    hh -= 12
                    hh = str(hh)
                    am_pm = "pm"

                return hh, am_pm

            # General variable
            default_gmt = 7
            report = ""
            cont = True

            gmt_timezone = find_gmt(default_gmt)
            is_gmt_valid = valid_gmt(gmt_timezone)

            # Happen when gmt is not valid
            if not is_gmt_valid:
                report = "I think the timezone is a little bit off... should be between -12 to 12 isn't ??"
                cont = False

            # If the GMT is valid, format the data
            if cont:

                split_time = time.ctime(time.time() + gmt_timezone * 3600).split(" ")

                # If there's unwanted element in the list
                if ('' in split_time) or (None in split_time):

                    # Remove the unwanted element
                    for element in split_time:
                        if (element == '') or (element is None):
                            split_time.remove(element)

                try:
                    # Gather the date and time data into several variable
                    splitted_hour = split_time[3].split(":")
                    day = Lines.day()[split_time[0]]
                    MM = Lines.month()[split_time[1].lower()]
                    DD = split_time[2]
                    YYYY = split_time[4]
                    hh = splitted_hour[0]
                    mm = splitted_hour[1]

                except:
                    report = Lines.date_time("formatting error")
                    cont = False

            # If the data formatting success, send the result
            if cont:

                # If user ask for date / day
                if any(word in text for word in ["date", "day"]):
                    report = Lines.date_time("show date").format(day, DD, ordinal(int(DD)), MM, YYYY)

                # Else if user ask for time
                elif "time" in text:
                    hh, AmPm = convert_am_pm(hh)
                    report = Lines.date_time("show time").format(hh, mm, AmPm)

            line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "Time and Date"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def send_invite(event):
        """ Function to send button template as invitation. Detail and participant list is given in text.
         Usage example : meg, can you send invite 'Go to the beach' to close-friend ? """

        try:
            global invitation_sender, invitation_sender_id

            def get_invitation_data():
                """ Function to find the description of invitation from text """

                # Find the index of apostrophe
                index_start = text.find("'")+1
                index_stop = text.rfind("'")

                # Determine whether 2 apostrophe are exist and the text exist
                text_available = (index_stop - index_start) >= 1

                if text_available:
                    invite_desc = text[index_start:index_stop]
                    no_invite_desc = False
                else:
                    invite_desc = " (つ≧▽≦)つ "
                    no_invite_desc = True

                return invite_desc, no_invite_desc

            def get_participant_list():
                """ Function to find participant list from text """

                try:
                    # Get the participant list name
                    filtered_text = OtherUtil.filter_words(text)
                    invite_list_index = filtered_text.index("to") + 1
                    list_name = filtered_text[invite_list_index]

                    # Try to find the list from database
                    invite_list = Database.list_dictionary[list_name]
                    no_invite_list = False

                # If the list is not listed in database, or the list name is unavailable
                except Exception:
                    invite_list = Database.list_dictionary["dev"]
                    no_invite_list = True

                return invite_list, no_invite_list

            # General variable
            cont = True
            report = []
            desc, no_desc = get_invitation_data()
            invite_list, no_invite_list = get_participant_list()

            # If there is missing element, send special notification
            if no_desc or no_invite_list:
                if no_desc:
                    report.append(Lines.invite_report("desc missing"))
                    cont = True
                if no_invite_list:
                    report.append(Lines.invite_report("participant list missing"))
                    cont = False

                report = "\n".join(report)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            # If the participant list is valid, create the invitation
            if cont:

                # Default variable for template message
                header_pic = Picture.header("background")
                title = 'Invitation'

                # Get the sender information
                try:
                    invitation_sender_id = event.source.user_id
                    invitation_sender = userlist[invitation_sender_id]
                except Exception:
                    invitation_sender = "someone"

                # Generate the invitation
                buttons_template = ButtonsTemplate(title=title, text=desc, thumbnail_image_url=header_pic, actions=[
                    PostbackTemplateAction(label='Count me in', data='confirmation invitation : yes'),
                    PostbackTemplateAction(label='No thanks', data='confirmation invitation : no'),
                    PostbackTemplateAction(label='Decide later', data='confirmation invitation : pending')
                ])
                template_message = TemplateSendMessage(alt_text=desc, template=buttons_template)

                # Sending the invitation
                try:
                    report = Lines.invite("header") % invitation_sender
                    invitation_sent = 0

                    # Send the invitation to user listed in the participant list
                    for participant in invite_list:
                        line_bot_api.push_message(participant, TextSendMessage(text=report))
                        line_bot_api.push_message(participant, template_message)
                        invitation_sent += 1

                    # If the invitation request is sent via personal chat, send confirmation of invitations sent
                    if invitation_sender != "someone":
                        report = Lines.invite("success") % (str(invitation_sent))
                        line_bot_api.push_message(invitation_sender_id, TextSendMessage(text=report))

                # If there's unexpected error while sending the invite
                except Exception:

                    # If the sender is known, send 'failed' notification to the sender
                    if invitation_sender != "someone":
                        report = Lines.invite("failed")
                        line_bot_api.push_message(invitation_sender_id, TextSendMessage(text=report))
                    raise

        except Exception as exception_detail:
            function_name = "Send Invite"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def invite_respond(event, cond):
        """ Function to notice the invitation sender about the response from participants.
         Usage example: (none : passive function) """

        try:
            global invitation_sender

            # Check whether invitation sender is available, if not set invitation sender as 'someone'
            try:
                sender_known = (invitation_sender != "someone") and (invitation_sender is not None)
            except:
                sender_known = False

            # Get the responder data
            try:
                responder_id = event.source.user_id
                responder = userlist[responder_id]
            except Exception:
                responder_id = address
                responder = "someone"

            # Send report to responder if their respond is recorded
            report = Lines.invite_report("respond recorded")
            line_bot_api.push_message(responder_id, TextSendMessage(text=report))

            # Send report to sender about the response
            try:
                report = Lines.invite_report(cond) % responder

                # If the sender is known, send the report
                if sender_known:
                    line_bot_api.push_message(invitation_sender_id, TextSendMessage(text=report))

                # If the sender is unknown / group / room, send the report to default userid instead
                else:
                    line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

            # If there's unexpected error
            except Exception:
                raise

        except Exception as exception_detail:
            function_name = "Invite respond"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def show_cinema_movie_schedule():
        """ Function to show list of movies playing at certain cinemas.
         Usage example : Meg, can you show me citylink xxi movie schedule ? """

        try:
            cont = True

            # If the cinema is not specified, send notification, stop process
            if not(any(word in text for word in ["xxi", "cgv"])):
                report = Lines.show_cinema_movie_schedule("specify the company")
                line_bot_api.push_message(address, TextSendMessage(text=report))
                cont = False

            # If the cinema is specified either xxi or cgv
            if cont:

                # The cinema is one of the XXI cinemas
                if "xxi" in text:

                    def get_cinema_keyword():
                        """ Function to get cinema's name keyword from text """

                        keyword = ['are', 'at', 'can', 'film', 'help', 'is', 'kato', 'list', 'me', 'meg', 'megumi',
                                   'movie', 'movies', 'playing', 'please', 'pls', 'schedule', 'show',
                                   'showing', 'you', 'xxi', 'what']
                        search_keyword = OtherUtil.filter_words(text)
                        search_keyword = OtherUtil.filter_keywords(search_keyword, keyword)

                        return search_keyword

                    def get_cinema_list(search_keyword):
                        """ Function to return available cinema list """

                        cinemas = []
                        page_url = "http://www.21cineplex.com/theaters"

                        # Open the XXI page
                        try:
                            req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                            con = urllib.request.urlopen(req)
                            page_source_code_text = con.read()
                            mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                        # Failed to open the XXI page
                        except Exception:
                            report = Lines.show_cinema_movie_schedule("failed to open the the page")
                            line_bot_api.push_message(address, TextSendMessage(text=report))
                            raise

                        # Get the cinema's link that fulfil the keyword
                        links = mod_page.findAll('a')
                        for link in links:
                            cinema_link = link.get("href")
                            if all(word in cinema_link for word in
                                   (["http://www.21cineplex.com/theater/bioskop"] + search_keyword)):
                                cinemas.append(cinema_link)

                        # Just in case there are duplicate link, remove the duplicates
                        if len(cinemas) > 1:
                            cinemas = set(cinemas)

                        return cinemas

                    def get_movie_data(cinema):
                        """ Function to return the movie's data, in form of (movie, description, schedule) """

                        # Default variable
                        movielist = []
                        desclist = []
                        schedulelist = []

                        # Open the page to parse
                        try:
                            req = urllib.request.Request(cinema, headers={'User-Agent': "Magic Browser"})
                            con = urllib.request.urlopen(req)
                            page_source_code_text = con.read()
                            mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                            mod_schedule_table = BeautifulSoup(
                                str(mod_page.find("table", {"class": "table-theater-det"})), "html.parser")

                        # If failed to open the page
                        except Exception:
                            report = Lines.show_cinema_movie_schedule("failed to open the the page")
                            line_bot_api.push_message(address, TextSendMessage(text=report))
                            raise

                        # Finding all movie's title, description, and showtime
                        try:
                            # Get the movie's title and description
                            movies = mod_schedule_table.findAll('a')
                            for movie in movies:

                                # Get the title
                                title = movie.string
                                if title is not None:
                                    movielist.append(title)

                                    # Get the description (nb: put here to limit number of desc <= number of title)
                                    movie_description = movie.get("href")

                                    # If the description is already existed before, don't append it again
                                    if movie_description in desclist:
                                        desclist.append("  ")
                                    else:
                                        desclist.append(movie_description)

                            # Get movie's showtime
                            showtimes = mod_schedule_table.findAll("td", {"align": "right"})
                            for showtime in showtimes:
                                schedulelist.append(showtime.string)

                        except Exception:
                            report = Lines.show_cinema_movie_schedule("failed to get movie data")
                            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))
                            raise

                        moviedata = zip(movielist, desclist, schedulelist)
                        return moviedata

                    def get_cinema_name(cinema_link):
                        """ Function to get cinema name """

                        # Get the cinema name
                        index_start = cinema_link.find("-") + 1
                        index_end = cinema_link.find(",")
                        cinema_name = cinema_link[index_start:index_end]
                        cinema_name = cinema_name.replace("-", " ")

                        # Special case TSM
                        if cinema_name == "tsm xxi":
                            if cinema_link == "http://www.21cineplex.com/theater/bioskop-tsm-xxi,186,BDGBSM.htm":
                                cinema_name = "tsm xxi (Bandung)"
                            elif cinema_link == "http://www.21cineplex.com/theater/bioskop-tsm-xxi,335,UPGTSM.htm":
                                cinema_name = "tsm xxi (Makassar)"

                        return cinema_name

                    def request_cinema_list():
                        """ Function to send confirmation whether send request cinema list or not """

                        # Generate button template
                        confirmation = Lines.show_cinema_movie_schedule("asking to show cinema list")
                        buttons_template = ButtonsTemplate(text=confirmation, actions=[
                                PostbackTemplateAction(label="Sure...", data='request xxi cinema list please',
                                                       text='Sure...')])
                        template_message = TemplateSendMessage(alt_text=confirmation, template=buttons_template)

                        # Send the template
                        line_bot_api.push_message(address, template_message)

                    search_keyword = get_cinema_keyword()

                    # If the cinema keyword is unspecified
                    if search_keyword == [] or search_keyword == [""]:
                        report = Lines.show_cinema_movie_schedule("No keyword found")
                        line_bot_api.push_message(address, TextSendMessage(text=report))
                        ask_for_request = True

                    # If keyword is found
                    else:
                        cinemas = get_cinema_list(search_keyword)

                        # Process the cinemas found
                        if len(cinemas) <= 0:
                            report = Lines.show_cinema_movie_schedule("No cinema found") % (", ".join(search_keyword))
                            ask_for_request = True

                        elif len(cinemas) > 2:
                            report = Lines.show_cinema_movie_schedule("Too many cinemas") % (", ".join(search_keyword))
                            ask_for_request = True

                        # If there is one (or 2 at most) cinema(s) found, then process it
                        else:

                            # Generate header for every type of reply
                            report = [Lines.show_cinema_movie_schedule("header") % str(", ".join(search_keyword))]

                            # Re-formatting data before sending
                            try:

                                # Getting data from every cinemas which fulfil keywords
                                for cinema in cinemas:

                                    # Gather the data and re-format it
                                    cinema_name = get_cinema_name(cinema)
                                    movie_data = get_movie_data(cinema)
                                    report.append(Lines.show_cinema_movie_schedule("cinema name") % cinema_name)

                                    for data in movie_data:
                                        report.append(data[0])  # movie title
                                        report.append(data[1])  # movie description
                                        report.append(data[2])  # movie schedule
                                        report.append("\n")

                                report.append(Lines.show_cinema_movie_schedule("footer"))
                                report = "\n".join(report)

                                ask_for_request = False

                            # If there's unexpected error related to formatting
                            except Exception:
                                report = Lines.show_cinema_movie_schedule("failed to show movie data")
                                line_bot_api.push_message(address, TextSendMessage(text=report))
                                raise

                        # Send report for every conditions
                        line_bot_api.push_message(address, TextSendMessage(text=report))

                    # If there's some problem with cinema's name, ask to send cinema list
                    if ask_for_request:
                        request_cinema_list()

                # The cinema is one of the CGV cinemas
                elif "cgv" in text:

                    def get_cinema_list(search_keyword):
                        """ Function to return available cinema list """

                        cinemas_name = []
                        cinemas_link = []
                        page_url = "https://www.cgv.id/en/schedule/cinema/"

                        # Open the web page to parse data
                        try:
                            req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                            con = urllib.request.urlopen(req)
                            page_source_code_text = con.read()
                            mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                        # Failed to open the page
                        except Exception:
                            report = Lines.show_cinema_movie_schedule("failed to open the the page")
                            line_bot_api.push_message(address, TextSendMessage(text=report))
                            raise

                        # Parse the web page to find cinema name and link
                        links = mod_page.findAll('a', {"class": "cinema_fav"})
                        for link in links:
                            cinema_name = link.string
                            cinema_link = "https://www.cgv.id" + link.get("href")

                            # If there's cinema's name which fulfil the search keyword, append it to list
                            if all(word in cinema_name.lower() for word in search_keyword):
                                cinemas_name.append(cinema_name)
                                cinemas_link.append(cinema_link)

                        cinemas = zip(cinemas_name, cinemas_link)
                        return cinemas

                    def get_movie_data(cinema):
                        """ Function to return the movie's data, in form of (movie, description, schedule) """

                        # Initializing general variable
                        movielist = []
                        desclist = []
                        schedulelist = []

                        # Open the web page to parse data
                        try:
                            req = urllib.request.Request(cinema, headers={'User-Agent': "Magic Browser"})
                            con = urllib.request.urlopen(req)
                            page_source_code_text = con.read()
                            mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                        # If failed to open the page
                        except Exception:
                            report = Lines.show_cinema_movie_schedule("failed to open the the page")
                            line_bot_api.push_message(address, TextSendMessage(text=report))
                            raise

                        # Gather the data
                        try:
                            # Get the raw data
                            mod_schedule_table = BeautifulSoup(
                                str(mod_page.findAll("div", {"class": "schedule-lists"})), "html.parser")
                            movies_data = BeautifulSoup(
                                str(mod_schedule_table.findAll("div", {"class": "schedule-title"})), "html.parser")
                            movies = movies_data.findAll("a")

                            # Get the movie's name and description
                            for movie in movies:
                                movie_name = movie.string
                                movie_desc = "https://www.cgv.id" + movie.get("href")
                                movielist.append(movie_name)
                                desclist.append(movie_desc)

                        # If failed to get the data
                        except Exception:
                            report = Lines.show_cinema_movie_schedule("failed to get movie data")
                            line_bot_api.push_message(address, TextSendMessage(text=report))
                            raise

                        # Get the movie's schedule
                        schedules = mod_schedule_table.findAll("a", {"id": "load-schedule-time"})
                        last_movie = ""  # Iteration of the last processed movie
                        for schedule in schedules:
                            movie_title = schedule.get("movietitle")
                            time = schedule.string

                            # Determine whether current movie is different from the last one or not
                            if movie_title != last_movie:
                                schedulelist.append("#")
                                last_movie = movie_title

                            # If the showtime is available
                            if time != ", ":
                                schedulelist.append(time)

                        # Re-formatting the schedulelist
                        schedulelist = " ".join(schedulelist)
                        schedulelist = schedulelist.split("#")

                        # Try to remove empty space in schedule list
                        try:
                            schedulelist.remove("")
                        except Exception:
                            pass

                        moviedata = zip(movielist, desclist, schedulelist)
                        return moviedata

                    def request_cinema_list():
                        """ Function to ask whether to show cinema list or not """

                        # Generate the button template
                        confirmation = Lines.show_cinema_movie_schedule("asking to show cinema list")
                        buttons_template = ButtonsTemplate(text=confirmation, actions=[
                            PostbackTemplateAction(label="Sure...", data='request cgv cinema list please',
                                                   text='Sure...')])
                        template_message = TemplateSendMessage(alt_text=confirmation, template=buttons_template)
                        line_bot_api.push_message(address, template_message)

                    # First filter of keywords and default text filter
                    keyword = ['are', 'at', 'can', 'cgv', 'film', 'help', 'is', 'kato', 'list', 'me',
                               'meg', 'megumi', 'movie', 'movies', 'playing', 'please', 'pls',
                               'schedule', 'show', 'showing', 'what']
                    search_keyword = OtherUtil.filter_words(text)
                    search_keyword = OtherUtil.filter_keywords(search_keyword, keyword)

                    # If keyword is unspecified
                    if search_keyword == [] or search_keyword == [""]:
                        report = Lines.show_cinema_movie_schedule("No keyword found")
                        line_bot_api.push_message(address, TextSendMessage(text=report))
                        ask_for_request = True

                    # If keyword is found
                    else:
                        # Get cinema's name and cinema's url in a list
                        cinemas = get_cinema_list(search_keyword)

                        # Re-format the cinema's name and cinema's link before append to main cinemas data
                        found_cinema_name = []
                        found_cinema_link = []
                        for cinema in cinemas:
                            found_cinema_name.append(cinema[0])
                            found_cinema_link.append(cinema[1])

                        found_cinema = zip(found_cinema_name, found_cinema_link)

                        # Process the cinemas found
                        if len(found_cinema_name) <= 0:
                            report = Lines.show_cinema_movie_schedule("No cinema found") % (", ".join(search_keyword))
                            ask_for_request = True
                        elif len(found_cinema_name) > 2:
                            report = Lines.show_cinema_movie_schedule("Too many cinemas") % (", ".join(search_keyword))
                            ask_for_request = True

                        # If there is one (or 2 at most) cinema(s) found, then process it
                        else:

                            # Generate header for every type of reply
                            report = [Lines.show_cinema_movie_schedule("header") % str(", ".join(search_keyword))]

                            # Re-formatting data before sending
                            try:

                                # Gather the data and re-format it
                                for cinema in found_cinema:
                                    cinema_name = cinema[0]                 # cinema [0] is the cinema name
                                    moviedata = get_movie_data(cinema[1])   # cinema [1] is the cinema link
                                    report.append(Lines.show_cinema_movie_schedule("cinema name") % cinema_name)
                                    for data in moviedata:
                                        report.append(data[0])  # movie title
                                        report.append(data[1])  # movie description
                                        report.append(data[2])  # movie schedule
                                        report.append("\n")

                                # Send the report to user
                                report.append(Lines.show_cinema_movie_schedule("footer"))
                                report = "\n".join(report)
                                ask_for_request = False

                            # If there's unexpected error related to formatting
                            except Exception:
                                report = Lines.show_cinema_movie_schedule("failed to show movie data")
                                line_bot_api.push_message(address, TextSendMessage(text=report))
                                raise

                        # Send report for every conditions
                        line_bot_api.push_message(address, TextSendMessage(text=report))

                    # If there's some problem with cinema's name, ask to send cinema list
                    if ask_for_request:
                        request_cinema_list()

        except Exception as exception_detail:
            function_name = "Show cinema movie schedule"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def show_cinema_list(cond):
        """ Function to send list of cinema available.
         Usage example : (none : passive function) """

        try:
            # The requested list if XXI cinemas
            if cond == "xxi":

                def get_cinema_list():
                    """ Function to get raw data of cinema list """

                    # Open the web page to parse the data
                    cinemas = []
                    page_url = "http://www.21cineplex.com/theaters"
                    try:
                        req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                        con = urllib.request.urlopen(req)
                        page_source_code_text = con.read()
                        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                    except:
                        report = Lines.general_lines("failed to open page") % page_url
                        line_bot_api.push_message(address, TextSendMessage(text=report))
                        raise

                    # Get every links and filter it to find cinema's link
                    links = mod_page.findAll('a')
                    for link in links:
                        cinema_link = link.get("href")
                        if all(word in cinema_link for word in ["http://www.21cineplex.com/theater/bioskop"]):
                            cinemas.append(cinema_link)

                    # Just in case, remove duplicate
                    cinemas = set(cinemas)
                    return cinemas

                def get_cinema_name(cinema_link):
                    """ Function to return name of the cinema's link """

                    # Get the name from the link
                    index_start = cinema_link.find("-") + 1
                    index_end = cinema_link.find(",")
                    cinema_name = cinema_link[index_start:index_end]
                    cinema_name = cinema_name.replace("-", " ")

                    # Special case for TSM (nb : 2 different cinemas use same name)
                    if cinema_name == "tsm xxi":
                        if cinema_link == "http://www.21cineplex.com/theater/bioskop-tsm-xxi,186,BDGBSM.htm":
                            cinema_name = "tsm xxi (Bandung)"
                        elif cinema_link == "http://www.21cineplex.com/theater/bioskop-tsm-xxi,335,UPGTSM.htm":
                            cinema_name = "tsm xxi (Makassar)"

                    return cinema_name

                # General variable
                cinema_list = []
                cinemas = get_cinema_list()

                # Re-formatting the cinema list (sort, format, add header, join text)
                for cinema in cinemas:
                    cinema_list.append(get_cinema_name(cinema))                              # Get the cinema's name
                cinema_list = sorted(cinema_list)                                            # Sort the name
                cinema_list.insert(0, Lines.show_cinema_movie_schedule("show cinema list"))  # Give header
                report = "\n".join(cinema_list)

                # Just in case the report is too long, split it into 2 post
                if len(report) > 1800:
                    report1 = report[:1800]+"..."
                    report2 = "..."+report[1801:]
                    line_bot_api.push_message(address, TextSendMessage(text=report1))
                    line_bot_api.push_message(address, TextSendMessage(text=report2))
                else:
                    line_bot_api.push_message(address, TextSendMessage(text=report))

            # The requested list if XXI cinemas
            elif cond == "cgv":

                # General variable
                cinema_list = []
                page_url = "https://www.cgv.id/en/schedule/cinema/"

                # Open the page
                try:
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                except:
                    report = Lines.general_lines("failed to open page") % page_url
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Parse the web to get data
                cinemas = mod_page.findAll('a', {"class": "cinema_fav"})
                for cinema in cinemas:
                    cinema = cinema.string
                    cinema_list.append(cinema)

                # Re-formatting the data (sort, create header, join text)
                cinema_list = sorted(cinema_list)
                cinema_list.insert(0, Lines.show_cinema_movie_schedule("show cinema list"))
                report = "\n".join(cinema_list)

                # Just in case the report is too long, split it into 2 post
                if len(report) > 1800:
                    report1 = report[:1800] + "..."
                    report2 = "..." + report[1801:]
                    line_bot_api.push_message(address, TextSendMessage(text=report1))
                    line_bot_api.push_message(address, TextSendMessage(text=report2))
                else:
                    line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "Show cinema list"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def itb_arc_database():
        """ Function to search for ITB students information based on internal database """

        try:
            def get_keyword():
                """ Function to return keyword found in text """

                # Find the index of apostrophe
                index_start = text.find("'") + 1
                index_stop = text.rfind("'")

                # Determine whether 2 apostrophe are exist and the text exist
                text_available = (index_stop - index_start) >= 1
                if text_available:
                    keyword = text[index_start:index_stop]
                    return keyword

                else:
                    return "keyword not found"

            def get_category():
                """ Function to return search category found on text, and 'is default' boolean """

                is_default_category = False

                # Check for several keyword which represent each category
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
                """ Function to crawl ARC - ITB database and get student information """

                # Maximum data shown is 5, nb : search_result_count is a main function variable
                if search_result_count > 5:
                    max_data = 5
                else:
                    max_data = search_result_count

                # iterate raw data to re-format and gather the needed data
                try:
                    for i in range(0, max_data):
                        student_nim = arc_itb_api_data['result'][i]['nim']
                        student_name = arc_itb_api_data['result'][i]['fullname']
                        student_major = arc_itb_api_data['result'][i]['major']['title']
                        student_major_year = arc_itb_api_data['result'][i]['year']
                        student_faculty = arc_itb_api_data['result'][i]['major']['faculty']['title']

                        search_result.append("NIM : " + str(student_nim))
                        search_result.append(student_name)
                        search_result.append(student_major + " [ " + str(student_major_year) + " ]")
                        search_result.append(student_faculty)
                        search_result.append(" ")

                    search_result.append(Lines.itb_arc_database("footer"))

                except:
                    report = Lines.general_lines("formatting error") % "student's information"
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

            def get_lecturer_info():
                """ Function to crawl ARC - ITB database and get lecturer information """

                # Maximum data shown is 5, nb : search_result_count is a main function variable
                if search_result_count > 5:
                    max_data = 5
                else:
                    max_data = search_result_count

                # iterate raw data to re-format and gather the needed data
                try:

                    for i in range(0, max_data):
                        lecturer_name = arc_itb_api_data['result'][i]['fullname']
                        lecturer_nip = arc_itb_api_data['result'][i]['nip']

                        search_result.append(lecturer_name)
                        search_result.append("NIP : " + str(lecturer_nip))
                        search_result.append(" ")
                    search_result.append(Lines.itb_arc_database("footer"))

                except:
                    report = Lines.general_lines("formatting error") % "lecturer's information"
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

            def get_major_info():
                """ Function to crawl ARC - ITB database and get major information """

                # Maximum data shown is 5, nb : search_result_count is a main function variable
                if search_result_count > 5:
                    max_data = 5
                else:
                    max_data = search_result_count

                # iterate raw data to re-format and gather the needed data
                try:
                    for i in range(0, max_data):
                        major_name = arc_itb_api_data['result'][i]['title']
                        major_code = arc_itb_api_data['result'][i]['code']
                        major_faculty = arc_itb_api_data['result'][i]['faculty']['title']

                        search_result.append("[ " + str(major_code) + " ] " + major_name)
                        search_result.append(major_faculty)
                        search_result.append(" ")
                    search_result.append(Lines.itb_arc_database("footer"))
                except:
                    report = Lines.general_lines("formatting error") % "major's information"
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

            def send_header():
                """ Function to create headers """

                report = [Lines.itb_arc_database("header") % itb_keyword]
                if is_default_category:
                    report.append(" ")
                    report.append(Lines.itb_arc_database("default category"))

                report = "\n".join(report)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_result_count():
                """ Function to send main result found count (still a part of header) """
                report = []

                # Differentiate if the data found is singular or plural
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
                """ Function to send all detailed result """

                report = "\n".join(search_result)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def backup_itb_data(keyword):
                """ Function to run backup search on carinim.cf as a backup database
                nb : It's not modular programming instead of bulk part of code due to laziness... (my bad)"""

                search_result = []
                send_header()

                # Determine whether keyword is name or nim
                try:
                    keyword_nim = str(int(keyword))
                    keyword_nama = ""
                except:
                    keyword_nim = ""
                    keyword_nama = keyword

                # Try to open the page
                page_url = str("http://carinim.cf/nim.php?nama=" + keyword_nama + "&nim=" + keyword_nim)
                try:
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                except:
                    report = Lines.general_lines("failed to open page") % page_url
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Try to crawl the data needed
                try:
                    raw_data_tables = BeautifulSoup(str(mod_page.findAll("table")), "html.parser")
                    raw_datas = raw_data_tables.findAll("tr")

                    # Try to re-format the data, only pick top 5 data
                    found_count = 0
                    for i in range(0, len(raw_datas)):
                        if len(str(raw_datas[i])) < 250:
                            raw_data = raw_datas[i].text.strip().split("\n")

                            student_nim = raw_data[2]
                            student_name = raw_data[1]
                            student_major = raw_data[3]
                            student_major_year = str("20" + str(student_nim[3:5]))

                            if found_count < 5:
                                search_result.append("NIM : " + str(student_nim))
                                search_result.append(student_name)
                                search_result.append(student_major + " [ " + str(student_major_year) + " ]")
                                search_result.append(" ")

                            found_count += 1

                except:
                    report = Lines.general_lines("formatting error") % "student's data"
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Differentiate if the data found is singular or plural
                report = []
                if found_count > 1:
                    report.append(Lines.itb_arc_database("count result plural") % (str(found_count)))
                    if found_count == 5:
                        report.append(" ")
                        report.append(Lines.itb_arc_database("only send top 5"))
                elif found_count == 1:
                    report.append(Lines.itb_arc_database("count result one"))
                else:
                    report.append(Lines.itb_arc_database("not found"))

                # Send pre-result header
                report = "\n".join(report)
                line_bot_api.push_message(address, TextSendMessage(text=report))

                # If the data is found and successfully gathered, send it to user
                if found_count >= 1:
                    report = "\n".join(search_result)
                    line_bot_api.push_message(address, TextSendMessage(text=report))

            cont = True
            itb_keyword = get_keyword()
            search_category = "student"
            search_result_count = 0

            # Check whether ITB keyword is found, if it's not, then stop the process and report to user
            if itb_keyword == "keyword not found":
                report = Lines.general_lines("search fail") % "itb keyword"
                line_bot_api.push_message(address, TextSendMessage(text=report))
                cont = False

            # If the keyword is found, try to search for the data
            if cont:
                search_category, is_default_category = get_category()
                arc_api_call = "https://nim.arc.itb.ac.id/api//search/" + search_category + "/?keyword=" + itb_keyword + "&page=1&count=30"

                # Try to use default ARC-ITB database
                try:
                    arc_itb_api_data = requests.get(arc_api_call).json()
                    search_result_count = arc_itb_api_data['totalCount']  # get the total result count

                # If it's failed, send notice and try to use sub database (carinim.cf)
                except:
                    report = Lines.itb_arc_database("database unreachable")
                    line_bot_api.push_message(address, TextSendMessage(text=report))

                    # Try to use sub database
                    try:
                        backup_itb_data(itb_keyword)
                    except Exception as e:
                        report = (Lines.itb_arc_database("sub database unreachable") + "\n\n" + e)
                        line_bot_api.push_message(address, TextSendMessage(text=report))

                    cont = False

            # If the data is successfully retrieved
            if cont:
                search_result = []
                send_header()
                send_result_count()

                # continue only if the result is available
                if search_result_count > 0:

                    # re-format the data
                    try:
                        if search_category == "student":
                            get_student_info()
                        elif search_category == "lecturer":
                            get_lecturer_info()
                        elif search_category == "major":
                            get_major_info()
                        send_detail_info()

                    # If there's error in formatting process, send a report to user
                    except:
                        report = Lines.itb_arc_database("data formatting failed")
                        line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "ITB ARC database"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def anime_download_link():
        """ Function to return anime download link list according to text.
        Usage example : Meg, show me anime download link 'title' <ep 2> <from zippy> """

        try:

            def get_keyword(cond="default"):
                """ Function to return search keyword (either anime title, or link) """

                # Some feature need keyword match case (ex : adf.ly)
                if cond == "original":
                    # Find the keyword in original text
                    try:
                        index_start = original_text.find("'") + 1
                        index_stop = original_text.rfind("'")
                        keyword = original_text[index_start:index_stop]
                        return keyword
                    except:
                        return "not_found"

                # If keyword doesn't need to match case
                else:
                    # Find the keyword in text
                    try:
                        index_start = text.find("'") + 1
                        index_stop = text.rfind("'")
                        keyword = text[index_start:index_stop]
                        return keyword
                    except:
                        return "not_found"

            def get_start_ep():
                """ Function to return starting episode from text """

                is_default_start = True
                start_ep = 1  # Default starting episode

                # Simple text filtering
                keyword = ['', ' ', '?', 'about', 'are', 'at', 'be', 'do', 'does', 'for', 'gonna', 'have',
                           'how', "how's", 'in', 'information', 'is', 'it', 'kato', 'kato,', 'like', 'me',
                           'meg', 'meg,', 'megumi', 'megumi,', 'now', 'please', 'pls', 'show', 'the', 'think',
                           'this', 'to', 'what', "what's", 'whats', 'will', 'you']
                filtered_text = OtherUtil.filter_words(text)
                filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

                # Find the starting episode using 'next-text after the found-keyword' scheme
                keyword = ["ep", "epi", "epis", "ep.", "episode", "chap", "ch", "chapter", "epid"]
                for i in range(0, len(filtered_text)):
                    if any(word in filtered_text[i] for word in keyword):

                        # Make sure the starting episode is in form of number
                        try:
                            start_ep = int(filtered_text[i + 1])
                            is_default_start = False
                        except:
                            pass

                return start_ep, is_default_start

            def get_host_source():
                """ Function to return chosen file-hosting's id """

                # General variable
                is_default_host = True
                host_id = 15  # Default file-hosting is zippyshare
                anime_hostlist = Database.anime_hostlist

                # Simple text filtering
                keyword = ['', ' ', '?', 'about', 'are', 'at', 'be', 'do', 'does', 'for', 'gonna', 'have',
                           'how', "how's", 'in', 'information', 'is', 'it', 'kato', 'kato,', 'like', 'me',
                           'meg', 'meg,', 'megumi', 'megumi,', 'now', 'please', 'pls', 'show', 'the', 'think',
                           'this', 'to', 'what', "what's", 'whats', 'will', 'you']
                filtered_text = OtherUtil.filter_words(text)
                filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

                # Find the file-hosting id using 'next-text after the found-keyword' scheme
                keyword = ["from", "fr", "source", "src", "frm", "sou"]
                for i in range(0, len(filtered_text)):
                    if any(word in filtered_text[i] for word in keyword):

                        # If file-hosting-candidate's name is found
                        try:
                            host_name = filtered_text[i + 1]

                            # Try to find the host id in the database
                            for host in anime_hostlist:
                                if host_name in host:
                                    host_id = anime_hostlist[host]
                                    is_default_host = False

                        except:
                            pass

                return host_id, is_default_host

            def get_process_starting_point(keyword):
                """ Function to enable direct pass if mirrorcreator or adf.ly link is already stated explicitly """

                direct_pass = any(word in keyword for word in ["mirrorcreator", "adf.ly"])
                return direct_pass

            def get_anime_pasted_link(keyword):
                """ Function to get pasted.co link """

                # If the 'pasted.co' is explicitly writen, enable direct process
                if "pasted.co" in keyword:
                    return keyword

                # Search database using anime's title to get the pasted.co link
                animelist = Database.animelist
                try:
                    for anime in animelist:
                        if keyword in anime.lower():
                            return animelist[anime]
                except:
                    pass

                # If the pasted.co link is not found
                return "title not found"

            def get_primary_download_link_list(anime_pasted_link):
                """ Extract links (adfly or mirrorcreator) from pasted.co """

                # If the 'adfly or mirrorcreator' is explicitly writen, enable direct process
                if any(word in text for word in ["mirrorcreator", "adf.ly"]):
                    return [keyword]

                page_url = anime_pasted_link + "/new.php"

                # Open the page (pasted.co)
                try:
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                except:
                    report = Lines.general_lines("failed to open page") % page_url
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Parse the web to get raw data (list of links)
                datas = mod_page.find("textarea", {"class": "pastebox rounded"})
                download_link_list = datas.text.split("\n")

                # Append found link to list
                download_link_list_filtered = []
                for link in download_link_list:
                    if "http" in link:
                        download_link_list_filtered.append(link)

                return download_link_list_filtered

            def get_file_id(link):
                """ Function to return file id from mirrorcreator link """

                # General variable
                file_id = " "
                mirror_creator_keyword = "https://www.mirrorcreator.com/files/"
                file_id_found = link.find(mirror_creator_keyword) != -1

                # If the keyword is found, try to get the file_id
                if file_id_found:
                    index_start = link.find(mirror_creator_keyword) + len(mirror_creator_keyword)
                    index_stop = index_start + 8
                    file_id = str(link[index_start:index_stop])

                return file_id, file_id_found

            def get_final_download_link(primary_download_link_list, start_ep=1):
                """ Function to return final download link from file-hosting """

                # General variable
                result = []
                success = False
                cont = True
                enable_dev_mode_extension = dev_mode_extension_check()

                # Check if the starting episode is available, if not, send notification
                latest_episode_count = len(primary_download_link_list)
                if start_ep > latest_episode_count:
                    result.append(Lines.anime_download_link("starting episode not aired"))
                    result.append(Lines.anime_download_link("send latest episode count") % str(latest_episode_count))
                    cont = False

                # If the starting episode is available
                if cont:

                    # Iterate from start episode to the last one
                    for i in range(start_ep - 1, (len(primary_download_link_list))):
                        current_ep = i + 1
                        primary_download_link = primary_download_link_list[i]

                        # Extract the mirror creator link / adfly link from every lines in pasted.co
                        try:
                            index_start = primary_download_link.find("http")
                            shortened_link = primary_download_link[index_start:].strip()
                            download_link, status = unshortenit.unshorten_only(shortened_link)

                        # If there's error when trying to get mirrorcreator link, just pass it and go to next one
                        except Exception:
                            break

                        # Get the file id from the mirrorcreator link found before
                        file_id, file_id_found = get_file_id(download_link)
                        if file_id_found:

                            # POST the data to mirrorcreator to get the download link
                            page_url = "https://www.mirrorcreator.com/downlink.php?uid=" + file_id
                            try:
                                post_data = dict(uid=file_id, hostid=hostid)
                                req_post = requests.post(page_url, data=post_data)
                                page_source_code_text_post = req_post.text
                                mod_page = BeautifulSoup(page_source_code_text_post, "html.parser")

                            except:
                                report = Lines.general_lines("failed to open page") % page_url
                                line_bot_api.push_message(address, TextSendMessage(text=report))
                                raise

                            # Get the final download link from POST request
                            final_download_links = mod_page.find_all("a", {"target": "_blank"})
                            final_download_link = None
                            for final_download_links_candidate in final_download_links:

                                # Avoid the ADS (It wasn't there first time)
                                temp_word = str(final_download_links_candidate.get("href"))

                                # If the link is listed in anime host list, set it to final download link
                                if any(word in temp_word for word in list(Database.anime_hostlist.keys())):
                                    final_download_link = temp_word

                            # If the final download link is available, append it to result
                            if final_download_link is not None:

                                # Formatting : Do not show current episode if there's only one link
                                if len(primary_download_link_list) < 2:
                                    result.append(final_download_link)

                                # Formatting : Show current episode if there're more than one links
                                else:
                                    result.append("Ep. " + str(current_ep) + " : " + final_download_link)
                                success = True

                                # DEV MODE : enable direct link only for zippyshare and dev
                                if enable_dev_mode_extension:
                                    direct_link = str(dev_mode_zippy_extension(final_download_link))
                                    result.append("[" + direct_link + "]")
                                    result.append(" ")

                            else:
                                result.append(Lines.anime_download_link("host not available") % (str(current_ep)))

                return result, success

            def send_header(cond="found", dev_mode_enable=False):
                """ Function to send header """
                report = []

                # If dev mode is enabled, execute it in dev mode style
                if dev_mode_enable:
                    report.append("[Executing in Dev Mode]\n")

                # If search keyword is found, sending notification about search keyword and default settings
                if cond == "found":
                    report.append(Lines.anime_download_link("header") % keyword)

                    # If starting episode is not specified
                    if is_default_start:
                        report.append(" ")
                        report.append(Lines.anime_download_link("default start ep"))

                    # If file-hosting is not specified
                    if is_default_host:
                        report.append(" ")
                        report.append(Lines.anime_download_link("default host"))

                # If direct pass is enabled
                elif cond == "direct pass":
                    report.append(Lines.anime_download_link("header") % keyword)

                    # If file-hosting is not specified
                    if is_default_host:
                        report.append(" ")
                        report.append(Lines.anime_download_link("default host"))

                # If search keyword is not found
                elif cond == "not_found":
                    report.append(Lines.anime_download_link("keyword not found"))

                # Send the report
                report = "\n".join(report)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_final_result(result, success, is_send_animelist):
                """ Function to send the final result that contains final download links """

                # If anime's title is found and starting episode is found, create header into report
                if success:
                    # nb : It's created backwardly, but it will show with the right sequence
                    result.insert(0, " ")
                    result.insert(0, Lines.anime_download_link("header for result"))

                report = "\n".join(result)
                line_bot_api.push_message(address, TextSendMessage(text=report))

                # Only send list of animes available if the title is not found
                if is_send_animelist:
                    send_animelist()

            def send_animelist():
                """ Function to send links of 2016 and 2017 anime list from cyber12 """

                # Generate the button template and send it
                title = "Cyber12 Anime"
                button_text = Lines.anime_download_link("send animelist")
                link_2017 = "https://www.facebook.com/notes/cyber12-official-group/2017-on-going-anime-update/1222138241226544"
                link_2016 = "https://www.facebook.com/notes/cyber12-official-group/on-going-anime-update/976234155816955"
                buttons_template = ButtonsTemplate(title=title, text=button_text, actions=[
                    URITemplateAction(label='2017 Anime Update', uri=link_2017),
                    URITemplateAction(label='2016 Anime Update', uri=link_2016)])
                template_message = TemplateSendMessage(alt_text=button_text, template=buttons_template)
                line_bot_api.push_message(address, template_message)

            def dev_mode_zippy_extension(page_url):
                """ Function to return direct download link from zippyshare.
                < warning > DO NOT USE IF EXCEPTION OCCUR, limit to dev only.
                < warning > This function is really unstable """

                direct_download_raw_data = ""

                # Open the zippy link to get the raw data
                try:
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                except:
                    return Lines.anime_download_link("dev mode extension failed") % "open page"

                # Parse the raw data to find complete-direct-link's parts
                try:
                    raw_datas = mod_page.find_all("script", {"type": "text/javascript"})
                    download_button_keyword = "document.getElementById('dlbutton').href"

                    # Search for download button keyword in the raw data
                    for raw_data in raw_datas:
                        if download_button_keyword in raw_data.text.strip():
                            direct_download_raw_data = raw_data.text.strip()

                except:
                    return Lines.anime_download_link("dev mode extension failed") % "parsing data"

                # Re-construct the complete link and re-format the data
                try:
                    # Get the complete-direct-link's header (ex: http://www69.zippyshare.com)
                    index_stop = page_url.find(".com/v/") + 4
                    link_header = page_url[:index_stop]

                    # Get the complete-direct-link's file id (ex: /d/DuGHrENZ/ )
                    index_start = page_url.find(".com/v/") + 7
                    index_stop = page_url.find('/file.html') + 1
                    link_fileid = "/d/" + page_url[index_start:index_stop]

                    # Get the complete-direct-link's token (ex: 49899) < WARNING : It use eval() >
                    index_start = direct_download_raw_data.find('/" + (') + 6
                    index_stop = direct_download_raw_data.find(') + "/')
                    link_token = direct_download_raw_data[index_start:index_stop]
                    link_token = str(eval(link_token))

                    # Get the complete-direct-link's file name (ex: /%5bCCM%5d_Kakegurui_-_04.mp4)
                    index_start = direct_download_raw_data.find(') + "/') + 5
                    index_stop = direct_download_raw_data.find('.mp4";') + 4
                    link_filename = direct_download_raw_data[index_start:index_stop]

                    # Re-construct the complete direct link
                    complete_direct_link = (link_header + link_fileid + link_token + link_filename)
                    return complete_direct_link

                except:
                    return Lines.anime_download_link("dev mode extension failed") % "re construct complete link"

            def dev_mode_extension_check():
                """ Function to check whether dev mode extension is enabled """

                if all(word in text for word in ["dev", "mode"]):
                    if hostid == 15:  # Only available for zippyshare
                        dev_extension_user_check = Function.dev_authority_check(address, cond="address")
                        if dev_extension_user_check:
                            return True

                return False

            # General variable and it's default value
            anime_pasted_link = " "
            start_ep = 1
            direct_pass = False  # If the keyword is already in form of mirror link or adf.ly, enable direct pass

            # Get the keyword from text
            keyword = get_keyword()
            cont = keyword != "not_found"

            # If keyword is available, get the starting episode and file host, and pasted.co link
            if cont:

                start_ep, is_default_start = get_start_ep()
                hostid, is_default_host = get_host_source()
                direct_pass = get_process_starting_point(keyword)  # Determine whether direct processing is available
                enable_dev_mode_extension = dev_mode_extension_check()  # Determine whether dev mode extension is available

                # Send header according to condition
                if direct_pass:
                    send_header(cond="direct pass", dev_mode_enable=enable_dev_mode_extension)
                else:
                    send_header(dev_mode_enable=enable_dev_mode_extension)

            # If the keyword is not found, send notification and end the process
            else:
                send_header("not_found")
                send_animelist()
                cont = False

            # If keyword is available and keyword is not mirror / adf.ly link, get the pasted.co link
            if cont and not direct_pass:

                anime_pasted_link = get_anime_pasted_link(keyword)
                cont = anime_pasted_link != "title not found"

            # If anime pasted.co link is available or it's direct pass
            if cont:

                # If the keyword is already in form of mirror link or adf.ly
                if direct_pass:
                    # Re- assign keyword with original match case keyword (before lowered)
                    keyword = get_keyword("original")
                    primary_download_link_list = [keyword]

                # Continuation from previous process
                else:
                    primary_download_link_list = get_primary_download_link_list(anime_pasted_link)

                result, is_success = get_final_download_link(primary_download_link_list, start_ep)
                is_send_animelist = False

            # If the title is not found, append notification and enable sending anime list
            else:
                result = [Lines.anime_download_link("title not found") % keyword]
                is_success = False
                is_send_animelist = True

            # Send the final result to user
            send_final_result(result, is_success, is_send_animelist)

        except Exception as exception_detail:
            function_name = "Anime Download Link"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def download_youtube():
        """ Function to return download link for youtube video with certain specification """

        try:
            def get_keyword():
                """ Function to return search keyword """

                # Find the index of apostrophe
                index_start = text.find("'") + 1
                index_stop = text.rfind("'")

                # Determine whether 2 apostrophe are exist and the text exist
                text_available = (index_stop - index_start) >= 1
                if text_available:
                    keyword = original_text[index_start:index_stop]
                    return keyword
                else:
                    return "keyword not found"

            def get_youtube_videos(keyword):
                """ Function to return a list of videos found on youtube matching search keyword """

                # Enable direct pass if keyword is a youtube link already
                if "https://www.youtube.com/watch?v=" in keyword:
                    return [keyword]

                page_url = str("https://www.youtube.com/results?search_query=" + keyword + "&spf=navigate")

                # Try to open the page
                try:
                    super_raw_json = requests.get(page_url).json()
                    super_raw_content = super_raw_json[1]["body"]["content"]
                    mod_page = BeautifulSoup(super_raw_content, "html.parser")
                except:
                    report = Lines.general_lines("failed to open page") % page_url
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Try to parse the web for information, search key and listed videos
                try:
                    found_videos = []

                    # Use REGEX to get the youtube video id
                    for m in re.finditer('/watch\?v=', str(mod_page)):
                        index_start = m.start()
                        index_stop = m.end() + 11
                        youtube_link = "https://www.youtube.com" + str(mod_page)[index_start:index_stop]

                        found_videos.append(youtube_link)

                    # Remove duplicates and return the list and the search key
                    found_videos = list(set(found_videos[:5]))[:3]
                    return found_videos

                except:
                    report = Lines.general_lines("formatting error") % "youtube link list"
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

            def get_youtube_video_title(page_url):
                """ Return the title of a youtube video """

                # Try to open the page
                try:
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                except:
                    report = Lines.general_lines("failed to open page") % page_url
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Get the video title
                title = mod_page.find("title").text.strip()

                # Remove ' - youtube ' from title
                if "youtube" in title.lower():
                    index_stop = title.rfind(" - ")
                    title = title[:index_stop]

                return title

            def get_spec():
                """ Function to get requested video's spec and format from the text """

                # Default format
                vid_format = "MP4"
                vid_quality_min = 720
                vid_quality_max = 720
                default = True

                # List of available video and audio format
                video_audio_format_list = ['3g2', '3gp', 'aa', 'aac', 'aax', 'act', 'amr', 'amv', 'asf', 'au', 'avi',
                                           'awb', 'dct', 'drc', 'dss', 'dvf', 'f4a', 'f4b', 'f4p', 'f4v', 'flac', 'flv',
                                           'gif', 'gifv', 'm4a', 'm4b', 'm4p', 'm4v', 'mkv', 'mmf', 'mng', 'mov', 'mp2',
                                           'mp3', 'mp4', 'mpc', 'mpe', 'mpeg', 'mpg', 'mpv', 'msv', 'ogg', 'ogv', 'rm',
                                           'rmvb', 'vob', 'wav', 'webm', 'wma', 'wmv', 'yuv']

                # If requested format is valid and available, use it as download format
                if any(word in text for word in video_audio_format_list):
                    split_text = text.split(" ")
                    for word in split_text:
                        if word in video_audio_format_list:
                            vid_format = word
                            default = False

                # If there's specified quality is valid and available, use it as download format
                if any(word in text for word in ['min', 'max']):
                    split_text = text.split(" ")
                    index = 0
                    for word in split_text:

                        # If minimum quality is specified
                        if 'min' in word:
                            try:
                                vid_quality_min = int(split_text[index + 1])
                                default = False
                            except:
                                pass

                        # If maximum quality is specified
                        if 'max' in word:
                            try:
                                vid_quality_max = int(split_text[index + 1])
                                default = False
                            except:
                                pass

                        index = index + 1

                return vid_format.upper(), vid_quality_min, vid_quality_max, default

            def get_genyoutube(youtube_links):
                """ Function to return genyoutube links from youtube link """

                genyoutube_links = []
                for youtube_link in youtube_links:
                    if "https://www.youtube.com/watch?v=" in youtube_link:
                        video_id = youtube_link.replace("https://www.youtube.com/watch?v=", "")
                    elif "https://youtu.be/" in youtube_link:
                        video_id = youtube_link.replace("https://youtu.be/", "")
                    else:
                        video_id = "not found"

                    genyoutube_links.append("http://video.genyoutube.net/" + str(video_id))

                return genyoutube_links

            def get_genyoutube_video_option(page_url):
                """ Function to return list of video options and video links found for each youtube link """

                video_option = []
                video_links = []
                # Try to open the genyoutube page
                try:
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                except:
                    report = Lines.download_youtube("page not found")
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # If the genyoutube page is opened, parse the page
                try:
                    links = mod_page.find_all("a", {"rel": "nofollow"})
                    for link in links:
                        href = link.get("href")
                        vid_keyword = "http://redirector.googlevideo.com"

                        # If found link has video keyword listed above, try to get the link data and format
                        if vid_keyword in href:
                            link_data = str(BeautifulSoup(str(link), "html.parser").find('span', {"class": "infow"}))
                            data = get_download_data(link_data)

                            # If found data fulfil the requirements format, put it in the final result
                            if approved_vid(data, req_format, req_quality_min, req_quality_max):
                                video_option.append(" ".join(data))
                                video_links.append(href)
                except:
                    report = Lines.download_youtube("gathering video data failed")
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                return video_option, video_links

            def get_download_data(link_data):
                """ Function to return video data (ex : .mp4 720 )"""

                remove_keyword = ['<span class="infow">', '<i class="glyphicon glyphicon-', '">', '</span>', '</i></span>',
                                  'video', 'volume-', '</i>', '<', '>', '/']

                for i in range(0, len(remove_keyword)):
                    link_data = link_data.replace(remove_keyword[i], "")
                vid_data = link_data.split(" ")
                vid_data[2] = vid_data[2].replace("-", " ")  # extra formatting for certain data

                return vid_data

            def approved_vid(data, req_format="MP4", req_quality_min=720, req_quality_max=720):
                """ Function to filter video which format fulfil requirements """

                # Get the video's format and quality
                vid_format = data[0]
                vid_quality = data[1]

                # Remove unnecessary alphabet in quality (eg 'p' in 720p)
                remove_keyword = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                for i in range(0, len(remove_keyword)):
                    vid_quality = vid_quality.replace(remove_keyword[i], "")

                # Make sure the quality is a number
                try:
                    vid_quality = int(vid_quality)
                except:
                    vid_quality = 0

                # Return boolean that represent if video's format fulfil requirements
                return (vid_format == req_format) and (vid_quality >= req_quality_min) and (vid_quality <= req_quality_max)

            def send_confirmation(keyword):
                """ Function to send header as confirmation that request is on process """

                report = (Lines.download_youtube("roger")).format(keyword)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_header(req_format, req_quality_min, req_quality_max, default):
                """ Function to send header """

                if default:
                    report = Lines.download_youtube("send option header") % "default settings (mp4 720p)"
                else:
                    settings = ("format : " + str(req_format) + ", min : " + str(req_quality_min) + "p, max : " + str(req_quality_max) + "p")
                    report = Lines.download_youtube("send option header") % settings

                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_vid_option(video_option, video_links, video_title):
                """ Function to send the video download link to user in form of button template """

                # Generate button header
                text = str(video_title + "\n" + Lines.download_youtube("pick one to download"))

                # Button row proportionate to how many videos available for download
                option = len(video_option)

                # Options more than 3
                if option > 3:

                    # Create list of other videos option
                    report = [Lines.download_youtube("header : too much option")]
                    for i in range(0, len(video_option)):
                        report.append(video_option[i])
                    report.append(Lines.download_youtube("footer : too much option"))
                    report = "\n".join(report)

                    actions = [URITemplateAction(label=video_option[0], uri=str(video_links[0])),
                               URITemplateAction(label=video_option[1], uri=str(video_links[1])),
                               URITemplateAction(label=video_option[2], uri=str(video_links[2])),
                               MessageTemplateAction(label='Others...', text=report)]

                else:
                    actions = []
                    for i in range(0, option):
                        actions.append(URITemplateAction(label=video_option[i], uri=str(video_links[i])))

                # Send the final result to user
                buttons_template = ButtonsTemplate(text=text, actions=actions)
                template_message = TemplateSendMessage(alt_text=text, template=buttons_template)
                line_bot_api.push_message(address, template_message)

            def send_footer(count):
                """ Function to send footer to end the request, if not time out """

                if count > 1:
                    report = Lines.download_youtube("footer plural")
                else:
                    report = Lines.download_youtube("footer singular")
                line_bot_api.push_message(address, TextSendMessage(text=report))

            # General variable
            cont = True
            req_format, req_quality_min, req_quality_max, default = get_spec()
            youtube_links = []

            keyword = get_keyword()
            if keyword == "keyword not found":
                report = Lines.general_lines("search fail") % "keyword"
                line_bot_api.push_message(address, TextSendMessage(text=report))
                cont = False

            if cont:
                send_confirmation(keyword)
                youtube_links = get_youtube_videos(keyword)

                # If youtube link is not available in text
                if len(youtube_links) == 0:
                    report = Lines.download_youtube("page not found")
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    cont = False

            # If youtube link is available, try to open genyoutube version
            if cont:
                page_urls = get_genyoutube(youtube_links)
                video_sent_count = 0

                # Check for every youtube link found
                for i in range(0, len(page_urls)):

                    video_option, video_links = get_genyoutube_video_option(page_urls[i])
                    video_title = get_youtube_video_title(youtube_links[i])

                    # If there's at least 1 video found and fulfil the requirements
                    if len(video_option) > 0:

                        # Send header only once
                        if video_sent_count == 0:
                            send_header(req_format, req_quality_min, req_quality_max, default)

                        send_vid_option(video_option, video_links, video_title)
                        video_sent_count += 1

                if video_sent_count == 0:
                    report = (Lines.download_youtube("no video found")).format(req_format, req_quality_min, req_quality_max)
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                else:
                    send_footer(video_sent_count)

        except Exception as exception_detail:
            function_name = "Youtube download"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def translate_text():
        """ Function to translate certain part of text into another language """

        try:
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
                    """
                    Returns an access token for the specified subscription.
                    This method uses a cache to limit the number of requests to the token service.
                    A fresh token can be re-used during its lifetime of 10 minutes. After a successful
                    request to the token service, this method caches the access token. Subsequent
                    invocations of the method return the cached token for the next 5 minutes. After
                    5 minutes, a new token is fetched from the token service and the cache is updated.
                    """

                    if (self.token is None) or (datetime.utcnow() > self.reuse_token_until):
                        token_service_url = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'

                        request_headers = {'Ocp-Apim-Subscription-Key': self.client_secret}

                        response = requests.post(token_service_url, headers=request_headers)
                        response.raise_for_status()

                        self.token = response.content
                        self.reuse_token_until = datetime.utcnow() + timedelta(minutes=5)

                    return self.token

            def get_text_translation(final_token, text_to_translate, from_lang_code, to_lang_code):

                # Call to Microsoft Translator Service
                headers = {"Authorization ": final_token}
                translate_url = "http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&from={}&to={}".format(
                    text_to_translate, from_lang_code, to_lang_code)

                translation_data = requests.get(translate_url, headers=headers)
                # Parse xml return values
                translation = ElementTree.fromstring(translation_data.text.encode('utf-8'))

                # Display translation
                return translation.text

            def get_text():
                """ Function to crop the text which going to be translated from the original text """

                if "'" in text:
                    index_start = text.find("'") + 1
                    index_stop = text.rfind("'")
                    keyword = text[index_start:index_stop]
                    return keyword

                return ""

            def get_language(cond):
                """ Function to return the language of text, either 'from' or 'to' """

                # Remove the text to translate, to minimize errors
                index_start = text.find("'") + 1
                index_stop = text.rfind("'")
                crop_text = text.replace(text[index_start:index_stop], '')

                keyword = ['', ' ', '?', 'about', 'are', 'at', 'be', 'do', 'does', 'for', 'gonna', 'have',
                           'how', "how's", 'information', 'is', 'it', 'kato', 'kato,', 'like', 'me',
                           'meg', 'meg,', 'megumi', 'megumi,', 'now', 'please', 'pls', 'show', 'the', 'think',
                           'this', 'what', "what's", 'whats', 'will', 'you']

                filtered_text = OtherUtil.filter_words(crop_text)
                filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

                # Determine the keyword to use, whether it's source language or destination language
                if cond == "from":
                    specific_keyword = ['from', 'fr']
                elif cond == "to":
                    specific_keyword = ['in', 'to', 'into']
                else:
                    specific_keyword = [""]

                # Searching the text for language code or language name
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
                """ Function to return available language for translation """

                # Try to open the page
                try:
                    page_url = "https://msdn.microsoft.com/en-us/library/hh456380.aspx"
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                except:
                    report = Lines.general_lines("failed to open page") % page_url
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Try to parse the page
                try:
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                    code_table = mod_page.find_all("td", {"data-th": "Language Code"})
                    name_table = mod_page.find_all("td", {"data-th": "English Name"})

                    # Create dictionary of language available
                    language_table = {}
                    for i in range(0, len(code_table)):
                        language_code = code_table[i].text.strip()
                        language_name = name_table[i].text.strip()
                        language_table[language_name] = language_code

                    return language_table

                except:
                    report = Lines.general_lines("formatting error") % "list of available language"
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

            def get_language_code(available_language, keyword):
                """ Function to return the language into respectively code """

                # If the keyword is not empty
                if keyword != "":

                    # If the keyword is already in form of code
                    for key in available_language:
                        if keyword in available_language[key].lower():
                            return available_language[key], key

                    # If the keyword is in form of name
                    for key in available_language:
                        if keyword in key.lower():
                            return available_language[key], key

                return "", ""

            # General variable
            cont = True
            result = []
            text_to_translate = get_text()

            # Just to escape 'might be referenced before assignment' warning which will never happened in the first place...
            available_language = None
            to_lang_code = ''
            to_lang = ''
            from_lang_code = ''
            translated_text = ''

            # if the text is not available, send report and end the process
            if text_to_translate == "":
                result.append(Lines.translate_text("text to translate not found"))
                cont = False

            # if text to translate is available, try to get the languages list
            if cont:
                available_language = get_available_language()  # this might return void
                if available_language is None:
                    result.append(Lines.translate_text("language list not found"))
                    cont = False

            # If the available language is listed and available, try to extract source and destination languages
            if cont:

                # Extract from-to language from the text
                from_lang, is_from_lang_found = get_language("from")
                to_lang, is_to_lang_found = get_language("to")
                from_lang_code, from_lang = get_language_code(available_language, from_lang)

                # If destination language is found
                if is_to_lang_found:
                    to_lang_code, to_lang = get_language_code(available_language, to_lang)

                # Destination language not found
                else:
                    to_lang = "english"
                    to_lang_code = "en"
                    result.append(Lines.translate_text("destination language not found"))

            # if the destination language is found, try to do the translation
            if cont:

                # if destination language is available, get the translation
                if to_lang_code != '':
                    azure_keys = ['1c3ea2f61de74a4f8d3bdcbe4cce7316', '20039c3da1074c9bba90ebd7600f1381']
                    client_secret = random.choice(azure_keys)
                    auth_client = AzureAuthClient(client_secret)
                    raw_bearer_token = str(auth_client.get_access_token())
                    bearer_token = 'Bearer ' + raw_bearer_token[2:-1]
                    translated_text = get_text_translation(bearer_token, text_to_translate, from_lang_code, to_lang_code)
                    translated_text = translated_text.lower()

                # destination language not available
                else:
                    result.append(Lines.translate_text("destination language not available") % to_lang)
                    cont = False

            # if the text is translated, send it to user
            if cont:

                # If the text is different from the original text (before translation)
                if text_to_translate != translated_text.lower():
                    result.append(Lines.translate_text("send translated").format(text_to_translate, to_lang, translated_text))

                # If the text is the same as before
                else:
                    result.append(Lines.translate_text("already in that language") % to_lang)

            report = "\n".join(result)
            line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "Translate"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def wiki_search():
        """ Function to get information about certain part of text, from Wikipedia """

        try:
            def getting_page_title(mod_page):
                """ Function to return wikipedia page title """

                try:
                    first_heading = mod_page.findAll("h1", {"id": "firstHeading"})
                    page_title = first_heading[0].string
                    return page_title
                except:
                    return "page title doesn't exist"

            def is_specific(mod_page):
                """ Function to check whether the designated page is specific or not """

                content = str(mod_page.find_all('p'))
                keyword = ["commonly refers to", "may also refer to", "may refer to"]

                # If keyword found in the page, the page is not specific
                if any(word in content for word in keyword):
                    return False
                else:
                    return True

            def has_disambiguation(mod_page):
                """ Function to check whether keyword has other disambiguation """

                content = str(mod_page.find_all('a', {"class": "mw-disambig"}))
                keyword = ["disambiguation"]

                # If the keyword is found in the page, then the keyword has disambiguation
                if any(word in content for word in keyword):
                    return True
                else:
                    return False

            def first_paragraph_coordinate(mod_page):
                """ Function to return boolean whether first paragraph is coordinate or not """

                content = str(mod_page.find('p'))
                keyword = ["coordinate"]

                # If keyword found in the first paragraph, then it's a coordinate
                if any(word in content for word in keyword):
                    return True
                else:
                    return False

            def get_paragraph(mod_page, cond='first'):
                """ Function to return first paragraph* of the page.
                note: Certain condition might result in failure and get more than one or less than one paragraph """

                def filter_paragraph_contents(content, start_sym='<', end_sym='>'):
                    """ Function to remove classic wikipedia's indexing and citation"""

                    need_filter = (start_sym or end_sym) in content
                    # Remove all indexing and citation
                    while need_filter:
                        start_index = content.find(start_sym)
                        stop_index = content.find(end_sym) + 1
                        content = content.replace(str(content[start_index:stop_index]), "")
                        need_filter = (start_sym or end_sym) in content

                    # Return clean paragraph
                    return content

                # If the first paragraph is un-usable, use second paragraph instead.
                if cond == 'second':
                    start_paragraph = 1

                # Else use first paragraph only
                else:
                    start_paragraph = 0

                # General variable
                content = mod_page.find_all('p')
                result = []
                letter_count = 0

                # Get paragraph until word count about 500 - 850 words.. can be less than 500, but not more than 850
                while letter_count < 500 and start_paragraph <= len(content):

                    # Formatting the paragraph
                    paragraph_text = content[start_paragraph].text.strip()
                    paragraph_text = filter_paragraph_contents(str(paragraph_text), '<', '>')
                    paragraph_text = filter_paragraph_contents(str(paragraph_text), '[', ']')

                    # If after append the temporary text, the letter count still less than 850, append it and crawl next paragraph
                    if letter_count + len(paragraph_text) < 850:
                        result.append(paragraph_text)
                        letter_count += len(paragraph_text)
                        start_paragraph += 1

                    # If after append the temporary text, the letter count will surpass 850, then don't append it, and end the process
                    else:
                        result.append("\n...")  # Just to make sure it's not cut ungracefully
                        break

                # Convert result to string and return it
                result = "\n".join(result)
                return result

            def show_suggestion(mod_page):
                """ If the page is not specific, show some suggestion of other keyword which might be more specific """

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
                           'Cookie statement']  # Keyword to be avoided

                links = mod_page.find_all('a')
                for link in links:
                    href = str(link.get("href"))
                    if "/wiki/" in (href[:6]):   # To eliminate wiktionary links
                        if link.string is not None:
                            if not (any(word in link.string for word in keyword)):

                                # If the link passed certain category test, (which more or less led to valid suggestion), append it
                                suggestion.append(link.string)

                # Return top 10 suggestion only
                suggestion = suggestion[:10]
                return suggestion

            def get_search_keyword():
                """ Function to get search keyword from text """

                # Find the index of apostrophe
                index_start = text.find("'")
                index_stop = text.rfind("'")+1

                # Determine whether 2 apostrophe are exist and the text exist
                text_available = (index_stop - index_start) >= 1
                if text_available:
                    keyword = original_text[index_start:index_stop]  # Use original text since some page has case sensitive
                    return keyword

            def get_search_language():
                """ Function to get search language from text """

                # General variable
                language = 'en'
                filtered_text = OtherUtil.filter_words(text)
                keyword = ["wiki"]

                # Search for language by using text before keyword scheme
                for i in range(0, len(filtered_text)):
                    if any(word in filtered_text[i] for word in keyword):
                        language = (filtered_text[i-1])
                        return language

                return language

            def request_page():
                """ Function to send weather user need detailed info about keyword. Send a confirmation to user """

                # Re-format the page url since line can't take <space> in uri links
                page_url_mod = page_url.replace(" ", "_")

                # Generate button template
                text = Lines.wiki_search("ask detail info")
                buttons_template = ButtonsTemplate(text=text, actions=[
                    URITemplateAction(label=Labels.confirmation("yes"), uri=str(page_url_mod))
                ])
                template_message = TemplateSendMessage(alt_text=text, template=buttons_template)

                # Send the template
                line_bot_api.push_message(address, template_message)

            def back_up_summary(keyword, language="en"):
                """ Function to run as back up of main function """

                report = []

                # Set page language
                wikipedia.set_lang(language)

                # Get page title
                back_up_wikipedia_page = wikipedia.page(keyword)
                report.append(back_up_wikipedia_page.title)
                report.append(" ")

                # Get page url
                page_url = back_up_wikipedia_page.url

                # Get page summary, cap to about 760 char
                back_up_wikipedia_summary = wikipedia.summary(keyword, chars=760)
                report.append(back_up_wikipedia_summary)

                return report, page_url

            # General variable
            report = []
            request_detailed_info = False
            cont = True
            mod_page = ""  # Just to escape 'variable might be referenced before assignment' warning which will never happened

            # Get keyword and language preferences
            keyword = get_search_keyword()
            language = get_search_language()

            # If no keyword found, send notification, and end the process
            if keyword is None:
                report.append(Lines.wiki_search("no keyword found"))
                cont = False

            # If keyword is found, try to open the wikipedia page
            if cont:
                # Try to open the page
                try:
                    keyword = keyword[1:-1]
                    page_url = "https://" + language + ".wikipedia.org/wiki/" + keyword
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                # If failed to open the page, send notice and end the process
                except:

                    # Last resort try to use wikipedia api (credit to : Jonathan Goldsmith)
                    try:
                        report, page_url = back_up_summary(keyword, language=language)
                        request_detailed_info = True

                    # If back up crawler still won't work, send notice and end the process
                    except:
                        report.append(Lines.wiki_search("page not found") % (language, keyword))
                        report.append(Lines.wiki_search("try different keyword / language"))
                        report.append("https://meta.wikimedia.org/wiki/List_of_Wikipedias")

                    cont = False

            # If the wiki page is available, try to get the title and paragraph
            if cont:
                title = getting_page_title(mod_page)

                # Check whether it's specific or not,
                if is_specific(mod_page):

                    # If it's specific page, send title and information about page
                    report.append(title)

                    # Check whether it has disambiguation or not, send extra header if yes
                    if has_disambiguation(mod_page):
                        report.append(Lines.wiki_search("has disambiguation"))

                    # If first paragraph is coordinate start from second paragraph instead
                    if first_paragraph_coordinate(mod_page):
                        report.append(get_paragraph(mod_page, 'second'))

                    # If first paragraph is usable
                    else:
                        report.append(get_paragraph(mod_page, 'first'))

                    request_detailed_info = True

                # If not send extra header, and send suggestion instead of information
                else:
                    report.append(Lines.wiki_search("not specific page - header") % keyword)
                    report.append(Lines.wiki_search("not specific page - content") % keyword)
                    suggestion = show_suggestion(mod_page)
                    suggestion = "\n".join(suggestion)
                    report.append(suggestion)

            # Send the final result to user
            report = "\n".join(report)
            line_bot_api.push_message(address, TextSendMessage(text=report))

            # Send prompt whether show detailed page or not
            if request_detailed_info:
                request_page()

        except Exception as exception_detail:
            function_name = "Wiki search"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def stalk_instagram():
        """ Function to stalk instagram account and return user profile and top 5 pic """

        try:
            def get_instagram_page_keyword():
                """ Function to return full instagram page link """

                # Find the index of apostrophe
                index_start = text.find("'") + 1
                index_stop = text.rfind("'")

                # Determine whether 2 apostrophe are exist and the text exist
                text_available = (index_stop - index_start) >= 1

                # If user (keyword) exist, crop it
                if text_available:
                    keyword = text[index_start:index_stop]
                    return keyword

                else:
                    return "keyword not found"

            def get_insta_raw_data(page_url):
                """ Function to crawl instagram page to get various data about someone """

                # Try to open instagram page
                try:
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                except:
                    report = Lines.general_lines("failed to open page") % page_url
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Parse the raw data, get the script part , select the longest one
                try:
                    rawdatas = mod_page.find_all("script")
                    temp = []
                    for x in rawdatas:
                        temp.append(str(x))
                    rawdatas = max(temp, key=len)

                    # Crop the pre-json part
                    text = rawdatas
                    index_start = text.find("{")
                    index_stop = text.rfind("}") + 1
                    rawdatas = str(text[index_start:index_stop])

                except:
                    report = Lines.general_lines("formatting error") % "instagram's page"
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Convert to JSON data
                json_rawdata = json.loads(rawdatas)

                return json_rawdata

            def get_insta_user_data(json_rawdata):
                """ Function to get insta user data """

                # Get user fullname
                try:
                    insta_fullname = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["full_name"]
                except:
                    insta_fullname = "no data"

                # Get user username
                try:
                    insta_username = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["username"]
                except:
                    insta_username = "no data"

                # Get user biography
                try:
                    insta_biography = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["biography"]
                except:
                    insta_biography = "no data"

                # Get user follower count
                try:
                    insta_follower = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["followed_by"]["count"]
                except:
                    insta_follower = "no data"

                # Get user following count
                try:
                    insta_following = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["follows"]["count"]
                except:
                    insta_following = "no data"

                # Get user privacy status
                try:
                    insta_private = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["is_private"]
                except:
                    insta_private = "no data"

                # Return all the data found
                return insta_fullname, insta_username, insta_biography, insta_follower, insta_following, insta_private

            def get_insta_media_data(json_rawdata):
                """ Function to get insta media data """

                # Try to get the medias data
                try:
                    insta_media = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]
                except:
                    report = Lines.general_lines("formatting error") % "posted-media's"
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Set default value
                insta_image_link_list = []
                insta_image_caption_list = []
                insta_image_like_list = []

                # Get top 5 image / video data
                for item in insta_media:
                    if len(insta_image_link_list) < 5:

                        # Get the media link
                        try:
                            insta_image = item["thumbnail_src"]
                            insta_image_link_list.append(insta_image)
                        except:
                            break

                        # Get the media caption
                        try:
                            insta_image_caption = str(item["caption"]).strip()
                            insta_image_caption_list.append(insta_image_caption)
                        except:
                            insta_image_caption_list.append("-")

                        # Get the media like count
                        try:
                            insta_image_like = item["likes"]["count"]
                            insta_image_like_list.append(insta_image_like)
                        except:
                            insta_image_like_list.append("0")

                    # If there's more than 5 item in image_link_list, stop it
                    else:
                        break

                return insta_image_link_list, insta_image_caption_list, insta_image_like_list

            def send_header():
                """ Function to send header , confirmation that stalking on the way """

                report = (Lines.stalk_instagram("header")).format(keyword)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_insta_user_info(insta_fullname, insta_username, insta_biography, insta_follower, insta_following):
                """ Function to send instagram page user information """

                # Generate report about user information
                report = [Lines.stalk_instagram("user information header")]
                try:
                    report.append(" ")
                    report.append("Fullname : " + str(insta_fullname))
                    report.append("Instagram username: " + str(insta_username))
                    report.append(" ")
                    report.append("Biography : " + str(insta_biography))
                    report.append(" ")
                    report.append("Follower : " + str(insta_follower))
                    report.append("Following : " + str(insta_following))
                except:
                    pass

                report = "\n".join(report)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_insta_user_pic(insta_image_link_list, insta_image_caption_list, insta_image_like_list):
                """ Function to send instagram page media (up to 5) """

                image_count = len(insta_image_link_list)

                carousel_text = []
                header_pic = []
                alt_text = ("Stalking " + keyword + "'s instagram...")
                # Generate and format the data used by carousel
                for i in range(0, image_count):

                    # Format image likes count
                    image_like_count = str(insta_image_like_list[i])+" ♥"

                    # Format image caption
                    if len(insta_image_caption_list[i]) > 45:
                        image_caption = str("\"" + insta_image_caption_list[i][:45] + "...\"")
                    else:
                        image_caption = str("\"" + insta_image_caption_list[i] + "\"")

                    # Join them together and append to carousel text
                    carousel_text.append(str(image_like_count) + "\n" + image_caption)

                    # Append image link to header pic
                    header_pic.append(insta_image_link_list[i])

                if image_count == 0:
                    report = Lines.stalk_instagram("picture count 0")
                    line_bot_api.push_message(address, TextSendMessage(text=report))

                # Else, send result in form of carousel
                else:
                    columns = []
                    for i in range(0, len(header_pic)):
                        carousel_column = CarouselColumn(text=carousel_text[i][:60], thumbnail_image_url=header_pic[i], actions=[
                                URITemplateAction(label='See detail..', uri=header_pic[i])])
                        columns.append(carousel_column)

                    carousel_template = CarouselTemplate(columns=columns)
                    template_message = TemplateSendMessage(alt_text=alt_text, template=carousel_template)
                    line_bot_api.push_message(address, template_message)

            cont = True
            json_rawdata = None

            # Get the full version link
            keyword = get_instagram_page_keyword()
            page_url = "https://www.instagram.com/" + keyword + "/"

            # If the keyword is not found, stop the process
            if keyword == "keyword not found":
                report = Lines.general_lines("search fail") % "instagram id"
                line_bot_api.push_message(address, TextSendMessage(text=report))
                cont = False

            # If full version link is available, try to get raw data
            if cont:
                send_header()
                json_rawdata = get_insta_raw_data(page_url)

                # If the data is unavailable, stop the process
                if json_rawdata is None:
                    report = Lines.general_lines("failed to open page") % str(keyword + "'s instagram")
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    cont = False

            # If the raw data is available, crawl user information and check if it's private or not
            if cont:
                # Get and send insta page user information
                insta_fullname, insta_username, insta_biography, insta_follower, insta_following, insta_private = get_insta_user_data(json_rawdata)
                send_insta_user_info(insta_fullname, insta_username, insta_biography, insta_follower, insta_following)

                if insta_private:
                    report = Lines.stalk_instagram("private")
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    cont = False

            # If it's not private, crawl top 5 pic and send it
            if cont:
                # Get and send insta page user media
                insta_image_link_list, insta_image_caption_list, insta_image_like_list = get_insta_media_data(json_rawdata)
                send_insta_user_pic(insta_image_link_list, insta_image_caption_list, insta_image_like_list)

        except Exception as exception_detail:
            function_name = "Stalk Instagram"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def hoax_or_fact():
        """ Function to check whether a part of text is truth or lie """

        try:

            def get_keyword():
                """ Function to crop keyword from text """
                # Find the index of apostrophe
                index_start = text.find("'") + 1
                index_stop = text.rfind("'")

                # Determine whether 2 apostrophe are exist and the text exist
                text_available = (index_stop - index_start) >= 1
                if text_available:
                    keyword = text[index_start:index_stop]
                    return keyword
                else:
                    return "keyword not found"

            def get_analyser_result(keyword):
                """ Function to return result from hoax analyser """

                page_url = 'https://hprimary.lelah.ga/analyze'
                # Try to open the page and input query to analyze
                try:
                    sess = requests.Session()
                    sess.options(page_url)
                    params = {'query': keyword}
                    s = sess.post(page_url, json=params)
                    clean_json = s.json()
                except:
                    report = Lines.general_lines("failed to open page") % page_url
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Try to re-format the raw data
                try:
                    conclusion = clean_json["conclusion"]
                    fact_point = clean_json["scores"][1]
                    hoax_point = clean_json["scores"][2]
                    unkw_point = clean_json["scores"][3]

                    # Count the percentage of hoax / truth / unknown...
                    percentage = max(fact_point, hoax_point, unkw_point) / (fact_point + hoax_point + unkw_point) * 100
                    percentage = str(percentage)[:4]
                    return conclusion, percentage

                except:
                    report = Lines.general_lines("formatting error") % "analyzer data"
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

            cont = True
            keyword = get_keyword()
            # Check whether keyword available
            if keyword == "keyword not found":
                report = Lines.general_lines("search fail") % 'query'
                line_bot_api.push_message(address, TextSendMessage(text=report))
                cont = False

            # If keyword is available
            if cont:
                conclusion, percentage = get_analyser_result(keyword)

                # Differentiate result base on conclusion
                if conclusion == "fact":
                    report = (Lines.hoax_or_fact("fact").format(percentage, keyword))
                elif conclusion == "hoax":
                    report = (Lines.hoax_or_fact("hoax").format(percentage, keyword))
                else:
                    report = Lines.hoax_or_fact("else")

                line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "Hoax analyser"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def play_music():
        """ Function to show list of music that can be played directly """

        try:

            def get_keyword():
                """ Function to return search keyword """

                # Find the index of apostrophe
                index_start = text.find("'") + 1
                index_stop = text.rfind("'")

                # Determine whether 2 apostrophe are exist and the text exist
                text_available = (index_stop - index_start) >= 1
                if text_available:
                    keyword = text[index_start:index_stop]
                    return keyword
                else:
                    return "keyword not found"

            def get_youtube_videos(keyword):
                """ Function to return a list of videos found on youtube matching search keyword """

                page_url = str("https://www.youtube.com/results?search_query=" + keyword + "&spf=navigate")

                # Try to open the page
                try:
                    super_raw_json = requests.get(page_url).json()
                    super_raw_content = super_raw_json[1]["body"]["content"]
                    mod_page = BeautifulSoup(super_raw_content, "html.parser")
                except:
                    report = Lines.general_lines("failed to open page") % page_url
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Try to parse the web for information, search key and listed videos
                try:
                    found_videos = []

                    # Use REGEX to get the youtube video id
                    for m in re.finditer('/watch\?v=', str(mod_page)):
                        index_start = m.start()
                        index_stop = m.end() + 11
                        youtube_link = "https://www.youtube.com" + str(mod_page)[index_start:index_stop]

                        found_videos.append(youtube_link)

                    # Remove duplicates and return the list and the search key
                    found_videos = set(found_videos)
                    return found_videos

                except:
                    report = Lines.general_lines("formatting error") % "youtube link list"
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

            def get_youtube_video_property(page_url):
                """ Return title and video duration of a youtube video """

                # Try to open the page
                try:
                    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                    con = urllib.request.urlopen(req)
                    page_source_code_text = con.read()
                    mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                except:
                    report = Lines.general_lines("failed to open page") % page_url
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    raise

                # Get the video title
                title = mod_page.find("title").text.strip()

                # Remove ' - youtube ' from title
                if "youtube" in title.lower():
                    index_stop = title.rfind(" - ")
                    title = title[:index_stop]

                # Get the video raw duration
                duration = mod_page.find("meta", {"itemprop": "duration"}).get("content")
                duration_minute = 0
                duration_second = 0

                # Crop the 'minute'
                index_start = duration.find("PT") + 2
                index_stop = duration.find("M")
                if (index_stop - index_start) >= 1:
                    duration_minute = str(duration[index_start:index_stop])

                # Crop the 'second'
                index_start = duration.find("M") + 1
                index_stop = duration.find("S")
                if (index_stop - index_start) >= 1:
                    duration_second = str(duration[index_start:index_stop])

                    # Add another '0' if it's one digit number
                    if len(duration_second) == 1:
                        duration_second = "0" + str(duration_second)

                return title, duration_minute, duration_second

            def get_direct_play_link(youtube_link):
                """ Function to return direct .mp3 link for youtube link """

                index_start = youtube_link.find("/watch?v=") + 9
                index_stop = index_start + 11
                video_id = youtube_link[index_start:index_stop]

                page_url = "http://o1.mp3you.tube:8080/convert/?vid=" + video_id
                try:
                    req = requests.get(page_url)
                    convert_data = req.json()
                    direct_play_link = str(convert_data["download_path"]).replace(" ", "%20")
                    return direct_play_link
                except:
                    pass

            def send_header(keyword):
                """ Function to send header (confirmation that request is under process) """

                report = (Lines.play_music("header")).format(keyword)
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_footer(count):
                """ Function to send footer to end the request, if not time out """

                if count > 1:
                    report = Lines.play_music("footer plural")
                else:
                    report = Lines.play_music("footer singular")
                line_bot_api.push_message(address, TextSendMessage(text=report))

            def send_detail_result(filtered_video_link, filtered_video_description, i):
                """ Function to send carousel of direct download link """

                # Generate and send button
                carousel_text = filtered_video_description
                buttons_template = ButtonsTemplate(text=carousel_text[i][:120], actions=[URITemplateAction(label='Play', uri=filtered_video_link[i])])
                template_message = TemplateSendMessage(alt_text="Playing music...", template=buttons_template)
                line_bot_api.push_message(address, template_message)

            cont = True

            # Just to escape 'variable might be referenced before assignment' warning which will never happened
            youtube_videos = []

            # Get keyword from text
            keyword = get_keyword()
            if keyword == "keyword not found":
                report = Lines.general_lines("search fail") % "keyword"
                line_bot_api.push_message(address, TextSendMessage(text=report))
                cont = False

            # If keyword is available, try to get list of youtube videos
            if cont:

                send_header(keyword)
                youtube_videos = get_youtube_videos(keyword)

                if len(youtube_videos) == 0:
                    report = (Lines.play_music("video not found")).format(keyword)
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    cont = False

            # If videos are available, try to filter it and get top 5 which are under 5 mins
            if cont:

                # Filter videos that is below 8 minutes (enable auto download)
                filtered_video_link = []
                filtered_video_description = []
                for youtube_link in youtube_videos:
                    video_title, video_duration_minute, video_duration_second = get_youtube_video_property(youtube_link)

                    # Include the video to filtered video list if it's below 8 mins
                    if int(video_duration_minute) < 8:

                        direct_download_link = get_direct_play_link(youtube_link)
                        video_duration = "[ " + video_duration_minute + ":" + video_duration_second + " ]"

                        # Append video direct link and also video default property
                        if direct_download_link is not None:
                            filtered_video_link.append(direct_download_link)
                            filtered_video_description.append(str(video_title + "\n" + str(video_duration)))

                            # Send it one by one ( to avoid run time error )
                            send_detail_result(filtered_video_link, filtered_video_description, i=(len(filtered_video_link)-1))

                    # Stop if it's already 3 videos
                    if len(filtered_video_link) >= 3:
                        break

                # If there's no video under 8 mins
                if len(filtered_video_link) == 0:
                    report = Lines.play_music("nothing to play")
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                else:
                    send_footer(count=len(filtered_video_link))

        except Exception as exception_detail:
            function_name = "Play music"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    """ ==========  8 August 2017 last update ============== """

    @staticmethod
    def summonerswar_wiki(cond="default"):

        try :
            def get_search_keyword():

                keyword = [' ', 'about', 'are', 'bad', 'build', 'good', 'how', 'hows', 'i', 'idea', 'info', 'information',
                           'infos', 'is', 'kato', 'me', 'meg', 'megumi', 'need', 'of', 'people', 'please', 'rating', 'ratings', 's',
                           'should', 'show', 'shows', 'skill', 'skills', 'stat', 'stats', 'summoner', 'summoners',
                           'summonerswar', 'sw', 'thethought', 'think', 'to', 'use', 'uses', 'war', 'what',
                           'whats', 'worth', 'worthed', 'you', 'your']

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
                print("ERROR DEF", e)
                report = Lines.summonerswar_wiki("random errors")
                line_bot_api.push_message(address, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "SW wiki"
            OtherUtil.random_error(function_name=function_name,exception_detail=exception_detail)

    @staticmethod
    def weather_forecast():

        try:
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

                return use_coordinate, cont

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
                    city_name = "Undefined"
                try:
                    city_weather_type = weather_data["weather"][0]['main']
                    city_weather_description = weather_data["weather"][0]['description']
                except:
                    city_weather_type = "Undefined"
                    city_weather_description = "Undefined"
                try:
                    city_temp = weather_data["main"]['temp']
                    city_temp_min = weather_data["main"]['temp_min']
                    city_temp_max = weather_data["main"]['temp_max']
                except:
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
                latitude, longitude = get_lat_long()
                use_coordinate, cont = is_lat_long_valid()  # create flags by validating latitude and longitude

            if cont:  # If either city id or lat long is available
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

    """====================== Sub Function List ============================="""

    @staticmethod
    def report_bug(event):
        """ Function to enable bugs report. Original text will be sent to Devs """

        # Get the user's id and user's name if possible
        try:
            user_id = event.source.user_id
            user = userlist[user_id]
        except:
            user = "Anonymous"

        # Send the report to Devs
        try:
            report = Lines.report_bug("report") % (original_text, user)
            for dev_user in Database.devlist:
                line_bot_api.push_message(dev_user, TextSendMessage(text=report))
            report = Lines.report_bug("success")

        except:
            report = Lines.report_bug("fail")

        line_bot_api.push_message(address, TextSendMessage(text=report))

    @staticmethod
    def join():
        """ Function that send first greeting when joined a chat room or group.
            Also send notification to devs """

        # Send greetings to group / room
        report = Lines.join("join")
        line_bot_api.push_message(address, TextSendMessage(text=report))

        # Send prompt to show megumi's manual
        report = Lines.show_manual("see manual?")
        ans_yes = Labels.confirmation("yes")
        ans_no = Labels.confirmation("no")
        command = "show megumi manual"
        confirm_template = ConfirmTemplate(text=report, actions=[
            PostbackTemplateAction(label=ans_yes, text=ans_yes, data=command),
            MessageTemplateAction(label=ans_no, text=ans_no)])
        template_message = TemplateSendMessage(alt_text=report, template=confirm_template)
        line_bot_api.push_message(address, template_message)

        # Send report to devs
        report = Lines.join("report") % str(address)
        for dev_user in Database.devlist:
            line_bot_api.push_message(dev_user, TextSendMessage(text=report))

    @staticmethod
    def leave(event):
        """ Function that send last greeting when leaving a chat room or group.
            Also send notification to devs """

        # If it's leaving a group
        if isinstance(event.source, SourceGroup):

            # Send last regards to group
            report = Lines.leave("leave")
            line_bot_api.push_message(address, TextSendMessage(text=report))
            report = Lines.leave("regards")
            line_bot_api.push_message(address, TextSendMessage(text=report))

            # Send notice to devs
            report = Lines.leave("report") % ('Group', address)
            for dev_user in Database.devlist:
                line_bot_api.push_message(dev_user, TextSendMessage(text=report))

            line_bot_api.leave_group(address)

        # If it's leaving a room
        elif isinstance(event.source, SourceRoom):

            # Send last regards to room
            report = Lines.leave("leave")
            line_bot_api.push_message(address, TextSendMessage(text=report))
            report = Lines.leave("regards")
            line_bot_api.push_message(address, TextSendMessage(text=report))

            # Send notice to devs
            report = Lines.leave("report") % ('Chat room', address)
            for dev_user in Database.devlist:
                line_bot_api.push_message(dev_user, TextSendMessage(text=report))

            line_bot_api.leave_room(address)

        else:
            report = Lines.leave("fail")
            line_bot_api.push_message(address, TextSendMessage(text=report))

    @staticmethod
    def tag_notifier(event):
        """ Function to send notice to certain user if their name is called """

        # Check if a message contain specific user determined keyword
        if any(word in text for word in Lines.jessin()):
            try:
                sender = line_bot_api.get_profile(event.source.user_id).display_name
            except:
                sender = "someone"

            report = Lines.tag_notifier() % (sender, original_text)
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    @staticmethod
    def false():
        """ Function to reply when the input text doesn't fall into any function category """
        reply = Lines.false()
        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    @staticmethod
    def added(event):
        """ Function to send first greeting when added.
            Send notice to devs """

        # Get the user's id and user's name
        try:
            user_id = event.source.user_id
            user = userlist[user_id]
        except:
            user_id = address
            user = "someone"

        # Send greetings when added
        report = Lines.added("added")
        line_bot_api.push_message(user_id, TextSendMessage(text=report))

        # Send prompt to show megumi's manual
        report = Lines.show_manual("see manual?")
        ans_yes = Labels.confirmation("yes")
        ans_no = Labels.confirmation("no")
        command = "show megumi manual"
        confirm_template = ConfirmTemplate(text=report, actions=[
            PostbackTemplateAction(label=ans_yes, text=ans_yes, data=command),
            MessageTemplateAction(label=ans_no, text=ans_no)])
        template_message = TemplateSendMessage(alt_text=report, template=confirm_template)
        line_bot_api.push_message(user_id, template_message)

        # Send notice when someone added
        report = Lines.added("report") % (user, user_id)
        for dev_user in Database.devlist:
            line_bot_api.push_message(dev_user, TextSendMessage(text=report))

    @staticmethod
    def removed(event):
        """ Function to send send notice to devs when someone block / un-follow """

        # Get the user's id and user's name
        try:
            user_id = event.source.user_id
            user = userlist[user_id]
        except:
            user = "someone"

        # Send notice to devs
        report = Lines.removed("report") % user
        for dev_user in Database.devlist:
            line_bot_api.push_message(dev_user, TextSendMessage(text=report))

    @staticmethod
    def dev_mode_set_tag_notifier():
        """ Function to set whether tag notifier is on or off """
        global tag_notifier_on

        # Turn on the notifier
        if any(word in text for word in ["on ", "enable "]):
            if tag_notifier_on is not True:
                tag_notifier_on = True
                reply = Lines.dev_mode_set_tag_notifier("on")

            # If the notifier already on
            else:
                reply = Lines.dev_mode_set_tag_notifier("same")

        # Turn on the notifier
        elif any(word in text for word in ["off ", "disable "]):
            if tag_notifier_on is True:
                tag_notifier_on = False
                reply = Lines.dev_mode_set_tag_notifier("off")

            # If the notifier already off
            else:
                reply = Lines.dev_mode_set_tag_notifier("same")

        else:
            reply = Lines.dev_mode_set_tag_notifier("fail")

        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    @staticmethod
    def dev_print_userlist():
        """ Function to print out userlist. Dev mode purpose only """
        global userlist_update_count

        # If there's no update yet
        if userlist_update_count == 0:
            reply = Lines.dev_mode_userlist("userlist not updated yet")

        # If there's an update
        else:
            try:
                print("=================================== NEW USER LIST ===================================\n")
                print(userlist)
                time.sleep(5)
                print("\n================================= END OF USER LIST =================================")
                reply = Lines.dev_mode_userlist("print userlist success") % userlist_update_count
                userlist_update_count = 0
            except:
                reply = Lines.dev_mode_userlist("print userlist failed")

        line_bot_api.reply_message(token, TextSendMessage(text=reply))

    @staticmethod
    def dev_authority_check(event, cond="default"):
        """ Function to check whether the user is dev.
        If dev mode is tried to be accessed in group or by non-dev, it will send report to dev.
         default = use event as parameter
         address = use address as parameter """

        try:
            # Get the user id and user name
            if cond == "address":
                user_id = event
            else:
                user_id = event.source.user_id
            user = userlist[user_id]

            # If the user is listed in Dev list
            if user_id in Database.devlist:
                return True

            # If the user is not listed, send rejection
            else:
                report = Lines.dev_mode_authority_check("reject")
                line_bot_api.push_message(address, TextSendMessage(text=report))
                report = Lines.dev_mode_authority_check("notify report") % user
                line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))
                return False

        # If Dev Mode tried to be accessed in group / room / failed
        except:
            user = "someone"
            report = Lines.dev_mode_authority_check("failed")
            line_bot_api.push_message(address, TextSendMessage(text=report))
            report = Lines.dev_mode_authority_check("notify report") % user
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))
            return False

    @staticmethod
    def dev_print_megumi_logger():
        """ Function to print log of input by user """

        try:

            report = Lines.dev_print_megumi_logger("header")
            for dev_user in Database.devlist:
                line_bot_api.push_message(dev_user, TextSendMessage(text=report))

            print("========================== NEW LOGGER : Rules ==========================\n")
            with open("Megumi_Logger_Rules.txt", "r") as megumi_logger:

                count_log = 0
                for item in megumi_logger:
                    print(item.strip())
                    count_log += 1

            time.sleep(5)
            print("\n========================== NEW LOGGER : AIAPI ==========================\n")
            with open("Megumi_Logger_AIAPI.txt", "r") as megumi_logger:

                for item in megumi_logger:
                    print(item.strip())
                    count_log += 1

            time.sleep(5)
            print("\n=========================== END OF LOGGER ===========================")

            report = (Lines.dev_print_megumi_logger("success")).format(count_log)
            for dev_user in Database.devlist:
                line_bot_api.push_message(dev_user, TextSendMessage(text=report))

        except Exception as exception_detail:
            function_name = "Dev mode print logger"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)

    @staticmethod
    def send_default_reply():
        """ Function to send default API.AI response for general chat """

        report = api_ai_response["result"]["fulfillment"]["speech"]
        line_bot_api.push_message(address, TextSendMessage(text=report))

    @staticmethod
    def show_manual(cond="default"):
        """ Function to send other function manuals """

        try:

            # If it's postback event
            if cond == "postback":
                requested_function = text[9:]

                # Get the manual data
                function_list = Database.functionlist
                function_name = ""
                for item in function_list:
                    if requested_function in item.lower():
                        function_name = item
                function_description = function_list[function_name]["description"]
                function_tips = function_list[function_name]["tips"]

                # Re-format the manuals
                report = "{}\n\nTips : {}".format(function_description, function_tips)

                # Send the manuals
                line_bot_api.push_message(address, TextSendMessage(text=report))

                # Generate prompt to show examples
                try:
                    function_examples = random.sample(set(function_list[function_name]["example"]), 3)

                    # Generate button to see example
                    report = Lines.show_manual("see example?")
                    buttons_template = ButtonsTemplate(text=report, actions=[
                        MessageTemplateAction(label='Try..', text=function_examples[0]),
                        MessageTemplateAction(label='Try..', text=function_examples[1]),
                        MessageTemplateAction(label='Try..', text=function_examples[2])
                    ])

                    # Send the confirmation
                    template_message = TemplateSendMessage(alt_text=report, template=buttons_template)
                    line_bot_api.push_message(address, template_message)

                # For Dev mode only, there's no available example
                except:
                    pass

            # Else send default manual
            else:

                def dev_mode_extension_check():
                    """ Function to check whether dev mode extension is enabled """

                    if all(word in text for word in ["dev", "mode"]):
                            dev_extension_user_check = Function.dev_authority_check(address, cond="address")
                            if dev_extension_user_check:
                                return True

                    return False

                # Base data to fill the manual
                title = Database.manual["title"]

                carousel_text = Database.manual["description"]

                # Format manual display here... Append new function here...
                function_list = Database.manual["function layout"]

                command = "Manual : "

                # Create default manual header
                report = Lines.show_manual("header")+"\n"+Lines.show_manual("tips")

                # Send header
                line_bot_api.push_message(address, TextSendMessage(text=report))

                # Generate default manual
                columns = []
                for i in range(0, len(title)):

                    # Create each carousel column content
                    actions = []
                    for j in range(0, 3):
                        action = PostbackTemplateAction(label=function_list[i][j], data=str(command + function_list[i][j]))
                        actions.append(action)

                    carousel_column = CarouselColumn(title=title[i], text=carousel_text[i][:60], actions=actions)
                    columns.append(carousel_column)

                # Get manual format layout and prepare to send
                layout_row = Database.manual["manual layout"]["row"]
                for i in range(0, layout_row):

                    # Gather manual format setting
                    row_format = Database.manual["manual layout"]["format"][i]
                    row_column_start = row_format["start"]
                    row_column_end = row_format["end"]

                    # Send default manual
                    carousel_template = CarouselTemplate(columns=columns[row_column_start:row_column_end])
                    template_message = TemplateSendMessage(alt_text="Megumi's manual", template=carousel_template)
                    line_bot_api.push_message(address, template_message)

                enable_dev_mode_extension = dev_mode_extension_check()
                if enable_dev_mode_extension:

                    # Gather manual format setting
                    row_column_start = Database.manual["manual layout"]["format"]["dev"]["start"]
                    row_column_end = Database.manual["manual layout"]["format"]["dev"]["end"]

                    # Send extension manual
                    carousel_template = CarouselTemplate(columns=columns[row_column_start:row_column_end])
                    template_message = TemplateSendMessage(alt_text="Megumi's manual - extension ", template=carousel_template)
                    line_bot_api.push_message(address, template_message)

        except Exception as exception_detail:
            function_name = "Show manual"
            OtherUtil.random_error(function_name=function_name, exception_detail=exception_detail)


class OtherUtil:

    @staticmethod
    def api_ai(api_ai_access_token, text):
        """ Function to send text to API.AI and receive JSON data of processed text """

        ai = apiai.ApiAI(api_ai_access_token)

        # Sending the information to API.AI
        request = ai.text_request()
        request.lang = 'en'  # optional, default value equal 'en'
        request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
        request.query = text

        # Receive the processed information in form of JSON file
        response = request.getresponse()
        response = str(BeautifulSoup(response, "html.parser"))
        end_json = response.rfind("}") + 1
        json_response = json.loads(response[:end_json])
        return json_response

    @staticmethod
    def remove_symbols(word, cond="default"):
        """ Function to remove symbols from text """

        # Several type of symbol list
        if cond == "default":
            symbols = "!@#$%^&*()+=-`~[]{}\|;:'/?.>,<\""
        elif cond == "date and time":
            symbols = "!@#$%^&*()+=`~[]{}\|;:'/?.>,<\""
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
    def random_error(function_name, exception_detail):
        """ Function to serve as last resort logger when unexpected error happened.
        It send the exception via line push to Dev """

        # First, print out the exception
        print("Error with :", function_name)
        print("-------------------- EXCEPTION DETAIL ---------------------")
        print(exception_detail)

        # Report to let group or other normal user know that something unexpected happened
        report = Lines.dev_mode_general_error("common")
        line_bot_api.push_message(address, TextSendMessage(text=report))

        # Send back up notification to Dev, to let Dev know that something unexpected happened
        report = (Lines.dev_mode_general_error("dev") % (function_name, exception_detail))
        for dev_user in Database.devlist:
            line_bot_api.push_message(dev_user, TextSendMessage(text=report))

    @staticmethod
    def megumi_logger(megumi_action, cond):
        """ Function to log every input by user """

        with open(str("Megumi_Logger_"+cond+".txt"), "a") as megumi_logger:
            megumi_logger.write(cond + "_" + megumi_action + " : " + original_text + "\n")

    @staticmethod
    def function_rules_based_mapping(event):
        """ Function to provide manual mapping of action if NLP API.AI fail to detect the intent """

        megumi_action = "Function_false"

        # List of Rule based action tree
        if any(word in text for word in ["what ", "show "]):

            if any(word in text for word in ["date", "time", "day "]):
                megumi_action = "Function_date_time"

            elif any(word in text for word in ["manual", "help"]):
                megumi_action = "Function_show_manual"

            elif any(word in text for word in ["weather", "forecast"]):
                megumi_action = "Function_weather_forecast"

            elif any(word in text for word in ["movie ", "movies", "film ", "films"]):

                if any(word in text for word in ["showing", "list", "playing", "schedule"]):
                    megumi_action = "Function_show_cinema_schedule"

            elif all(word in text for word in ["anime"]):

                if any(word in text for word in ["download", "link"]):
                    megumi_action = "Function_anime_download_link"

            elif any(word in text for word in ["is", "are", "info", "?", "about", "search"]):

                if any(word in text for word in ["sw", "summonerswar", "summoner"]):
                    megumi_action = "Function_summoners_war_wiki"

                elif all(word in text for word in ["itb"]):
                    megumi_action = "Function_itb_arc_database"

                elif any(word in text for word in ["mean", "wiki", "is", "are", "about"]):
                    megumi_action = "Function_wiki_search"

                elif any(word in text for word in ["in"]):
                    megumi_action = "Function_translate"

        elif any(word in text for word in ["how"]):

            if any(word in text for word in ["weather", "forecast"]):
                megumi_action = "Function_weather_forecast"

            elif any(word in text for word in ["say"]):
                megumi_action = "Function_translate"

            elif any(word in text for word in ["think", "about"]):
                megumi_action = "Function_hoax_analyser"

        elif all(word in text for word in ["who"]):

            if all(word in text for word in ["itb"]):
                megumi_action = "Function_itb_arc_database"

            elif any(word in text for word in ["is", "?"]):
                megumi_action = "Function_wiki_search"

        elif any(word in text for word in ["download ", "save "]):

            if any(word in text for word in ["youtube", "video"]):
                megumi_action = "Function_download_youtube"

            elif any(word in text for word in ["anime"]):
                megumi_action = "Function_anime_download_link"

        elif any(word in text for word in ["stalk", "instagram", "insta"]):
            megumi_action = "Function_stalk_instagram"

        elif all(word in text for word in ["pick ", "num"]):
            megumi_action = "Function_random_integer"

        elif any(word in text for word in ["choose ", "which one"]):
            megumi_action = "Function_choose_one"

        elif all(word in text for word in ["play"]):
            if any(word in text for word in ["music", "song"]):
                megumi_action = "Function_play_music"

        elif any(word in text for word in ["translate"]):
            megumi_action = "Function_translate"

        elif all(word in text for word in ["true", "?"]):
            megumi_action = "Function_hoax_analyser"

        elif any(word in text for word in ["say "]):
            megumi_action = "Function_echo"

        elif all(word in text for word in ["send ", "invite"]):
            megumi_action = "Function_send_invite"

        elif all(word in text for word in ["report", "bug"]):
            megumi_action = "Function_report_bug"

        elif any(word in text for word in ["please leave, megumi"]):
            megumi_action = "Function_leave"

        elif all(word in text for word in ["dev", "mode"]):

            if Function.dev_authority_check(event):

                if all(word in text for word in ["print", "userlist"]):
                    megumi_action = "Dev_mode_print_userlist"

                elif all(word in text for word in ["print", "log"]):
                    megumi_action = "Dev_mode_print_logger"

                elif any(word in text for word in ["turn ", "able", "tag notifier", "notif"]):
                    megumi_action = "Dev_mode_set_tag_notifier"

        return megumi_action

"""========================================== End of Function List ================================================"""

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
