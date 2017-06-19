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

megumi = ['megumi', 'kato']

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

def get_receiver_addr(event):
    global address
    try:
        address = event.source.group_id
    except:
        address = event.source.user_id
    return address

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    global token,text
    text = event.message.text
    token = event.reply_token
    get_receiver_addr(event)


    if any(word in text.lower() for word in megumi):

        if "echo" in text.lower() : Function.echo()


        elif "rand" in text.lower():
            text = text.split(" ")
            reply = rand(int(text[1]),int(text[2]))
            line_bot_api.reply_message(token,TextSendMessage(text=reply))

        elif "push " in text.lower():
            try:
                 line_bot_api.push_message(address, TextSendMessage(text='Konichiwa ^^ !!'))
            except LineBotApiError as e:
                print("push error\n")
                print(e.status_code)
                print(e.error.message)
                print(e.error.details)

            line_bot_api.reply_message(token,TextSendMessage("push success ~ "))

        else :
            line_bot_api.reply_message(token, TextSendMessage("..."))

"""=====================================  List of Usable Function  =============================================="""

class Function :
    def rand(min=1,max=5):
        a = random.randrange(min, max+1)
        b = random.randrange(min, max+1)
        c = random.randrange(min, max+1)
        d = random.randrange(min, max+1)
        e = random.randrange(min, max+1)

        rand = random.choice([a,b,c,d,e])
        return rand

    def echo():
        line_bot_api.reply_message(token, TextSendMessage(text=text))

"""=============================================================================================================="""

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)