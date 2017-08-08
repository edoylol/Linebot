import urllib,requests,random,time,os,urllib.request,io
import json
import unshortenit
import Database
import apiai
from bs4 import BeautifulSoup
from lines_collection import Lines, Labels, Picture

from datetime import timedelta
from datetime import datetime
from xml.etree import ElementTree

import wikipedia

class OtherUtil:

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
        if address != jessin_userid:
            report = (Lines.dev_mode_general_error("dev") % (function_name, exception_detail))
            line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

carousel_template = CarouselTemplate(columns=[
    CarouselColumn(title=title[0], text=carousel_text[0][:60], actions=[
        PostbackTemplateAction(label=function_list[0][0], data=str(command+function_list[0][0])),
        PostbackTemplateAction(label=function_list[0][1], data=str(command+function_list[0][1])),
        PostbackTemplateAction(label=function_list[0][2], data=str(command+function_list[0][2]))]),
    CarouselColumn(title=title[1], text=carousel_text[1][:60], actions=[
        PostbackTemplateAction(label=function_list[1][0], data=str(command+function_list[1][0])),
        PostbackTemplateAction(label=function_list[1][1], data=str(command+function_list[1][1])),
        PostbackTemplateAction(label=function_list[1][2], data=str(command+function_list[1][2]))]),
    CarouselColumn(title=title[2], text=carousel_text[2][:60], actions=[
        PostbackTemplateAction(label=function_list[2][0], data=str(command+function_list[2][0])),
        PostbackTemplateAction(label=function_list[2][1], data=str(command+function_list[2][1])),
        PostbackTemplateAction(label=function_list[2][2], data=str(command+function_list[2][2]))]),
    CarouselColumn(title=title[3], text=carousel_text[3][:60], actions=[
        PostbackTemplateAction(label=function_list[3][0], data=str(command+function_list[3][0])),
        PostbackTemplateAction(label=function_list[3][1], data=str(command+function_list[3][1])),
        PostbackTemplateAction(label=function_list[3][2], data=str(command+function_list[3][2]))]),
    CarouselColumn(title=title[4], text=carousel_text[4][:60], actions=[
        PostbackTemplateAction(label=function_list[4][0], data=str(command+function_list[4][0])),
        PostbackTemplateAction(label=function_list[4][1], data=str(command+function_list[4][1])),
        PostbackTemplateAction(label=function_list[4][2], data=str(command+function_list[4][2]))])
    ])

# Create carousel
columns = []
for i in range(0, len(title)):

    # Create each carousel column content
    actions = []
    for j in range(0, 3):
        action = PostbackTemplateAction(label=function_list[i][j], data=str(command+function_list[i][j]))
        actions.append(action)

    carousel_column = CarouselColumn(title=title[i], text=carousel_text[i][:60], actions=actions)
    columns.append(carousel_column)



