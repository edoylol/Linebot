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
        except:
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
    print(report)

text = "'hatsune miku'"


print(" ----------------  JESSIN API ---------------------")

tic = time.clock()
wiki_search()
toc = time.clock()
print("Time elapsed:",(toc - tic),"second(s)")

print(" ----------------  WIKIPEDIA API ---------------------")

tic = time.clock()
summary = wikipedia.summary(text[1:-1], sentences= 1)
print(summary)
toc = time.clock()
print("Time elapsed:",(toc - tic),"second(s)")





