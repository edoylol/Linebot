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

from argparse import ArgumentParser
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,LineBotApiError,
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,StickerSendMessage
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
# Megumi chat bot
"""  
channel_secret = '9d1e7500a205ddaec1c6f2ae0d190e6e'
channel_access_token = 'f/jBF6+aFLuvzEmI0NbPNWjfrsK3Kjwxzzl1XUeLun+3uRs6AbDEQGphezyssudufYiyiHBoLQWWjEBqTtV00P0jLOJuVlrEQly/Xjo7ZQXY0YMEoKm869aWpCnu9Jhog4zt4nb4DYB4zVMWApdjCQdB04t89/1O/w1cDnyilFU='
"""

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


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
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



@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    if "echo" in event.message.text.lower() :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )
    elif "rand" in event.message.text.lower():
        text = event.message.text.split(" ")
        reply = rand(int(text[1]),int(text[2]))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
    elif "push" in event.message.text.lower():
        try:
            line_bot_api.push_message("U77035fb1a3a4a460be5631c408526d0b", TextSendMessage(text='Hello World!'))
        except LineBotApiError as e:
            print(e.status_code)
            print(e.error.message)
            print(e.error.details)
        #sticker_message = StickerSendMessage(package_id='2',sticker_id='151')
        line_bot_api.reply_message(event.reply_token,TextSendMessage("..."))
    else :
        line_bot_api.reply_message(event.reply_token, TextSendMessage("..."))

def rand(min=1,max=5):
    a = random.randrange(min, max+1)
    b = random.randrange(min, max+1)
    c = random.randrange(min, max+1)
    d = random.randrange(min, max+1)
    e = random.randrange(min, max+1)

    rand = random.choice([a,b,c,d,e])
    return rand



if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)