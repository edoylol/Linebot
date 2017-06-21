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

from function_collection import Function, OtherUtil
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
Function = Function()
OtherUtil = OtherUtil()

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
        Function.tag_notifier(event)

@handler.add(JoinEvent)
def handle_join(event):
    global token,jessin_userid
    jessin_userid = "U77035fb1a3a4a460be5631c408526d0b"
    token = event.reply_token
    get_receiver_addr(event)

    Function.join()


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)

