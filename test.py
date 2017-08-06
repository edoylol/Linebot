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

text = "sdfasdf'nadya rianty will love me back'sdfas"

def hoax_or_fact():
    """ Function to check whether a part of text is truth or lie """

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
            r = sess.options(page_url)
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