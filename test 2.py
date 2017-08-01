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
        """ Function to get information about certain part of text, from Wikipedia """

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
        print(keyword,language)

        # If no keyword found, send notification, and end the process
        if keyword is None:
            report.append(Lines.wiki_search("no keyword found"))
            cont = False

        # If keyword is found, try to open the wikipedia page
        if cont:
            # Try to open the page
            try:
                report, page_url = back_up_summary(keyword, language=language)
                request_detailed_info = True


            except:
                report.append(Lines.wiki_search("page not found") % (language, keyword))
                report.append(Lines.wiki_search("try different keyword / language"))
                report.append("https://meta.wikimedia.org/wiki/List_of_Wikipedias")
            cont = False


        # Send the final result to user
        report = "\n".join(report)
        print(report)

        # Send prompt whether show detailed page or not
        if request_detailed_info:
            print("oke suckses")

text = "meg, search for 'ganymede (moon)'"
original_text = "meg, search for 'Ganymede (Moon)'"
wiki_search()