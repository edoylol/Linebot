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
        #line_bot_api.push_message(address, TextSendMessage(text=report))
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
        duration_minute = duration[index_start:index_stop]

    # Crop the 'second'
    index_start = duration.find("M") + 1
    index_stop = duration.find("S")
    if (index_stop - index_start) >= 1:
        duration_second = duration[index_start:index_stop]

    return title, duration_minute, duration_second







