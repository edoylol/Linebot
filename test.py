import urllib,requests,random,time,os,urllib.request,io
import json
import unshortenit
import Database
from bs4 import BeautifulSoup
from lines_collection import Lines, Labels, Picture

from datetime import timedelta
from datetime import datetime
from xml.etree import ElementTree
import math
Lines = Lines()


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


page_url = "http://www69.zippyshare.com/v/DuGHrENZ/file.html"
try:
    req = urllib.request.Request(page_url, headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"})
    con = urllib.request.urlopen(req)
    page_source_code_text = con.read()
    mod_page = BeautifulSoup(page_source_code_text, "html.parser")
except:
    report = Lines.general_lines("failed to open page") % page_url

text = page_url
index_stop = text.rfind(".com/")+4
keyword = text[:index_stop]

download_link = mod_page.find("a", {"id": "dlbutton"})
print(download_link)
print("/d/DuGHrENZ/6263/%5bCCM%5d_Kakegurui_-_04.mp4" in mod_page)
