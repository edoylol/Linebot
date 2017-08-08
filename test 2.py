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

import re


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

text = "'symphony clean bandit'"

def play_music():
    """ Function to show list of music that can be played directly """

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
            # line_bot_api.push_message(address, TextSendMessage(text=report))
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
            # line_bot_api.push_message(address, TextSendMessage(text=report))
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
            # line_bot_api.push_message(address, TextSendMessage(text=report))
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

    def send_header():
        """ Function to send header (confirmation that request is under process) """

        report = Lines.play_music("header")
        #line_bot_api.push_message(address, TextSendMessage(text=report))

    def send_detail_result(filtered_video_link, filtered_video_description):
        """ Function to send carousel of direct download link """

        carousel_text = filtered_video_description
        columns = []

        for i in range(0, len(filtered_video_link)):
            carousel_column = CarouselColumn(text=carousel_text[i][:60], actions=[URITemplateAction(label='Play', uri=filtered_video_link[i])])
            columns.append(carousel_column)

        carousel_template = CarouselTemplate(columns=columns)
        template_message = TemplateSendMessage(alt_text="Playing music..", template=carousel_template)
        line_bot_api.push_message(address, template_message)

    cont = True
    keyword = get_keyword()
    if keyword == "keyword not found":
        report = Lines.general_lines("search fail") % "keyword"
        # line_bot_api.push_message(address, TextSendMessage(text=report))
        cont = False

    # If keyword is available, try to get list of youtube videos
    if cont:

        send_header()
        youtube_videos = get_youtube_videos(keyword)

        if len(youtube_videos) == 0:
            report = Lines.play_music("video not found") % keyword
            # line_bot_api.push_message(address, TextSendMessage(text=report))
            cont = False

    # If videos are available, try to filter it and get top 5 which are under 5 mins
    if cont:

        # Filter videos that is below 5 minutes (enable auto download)
        filtered_video_link = []
        filtered_video_description = []
        for youtube_link in youtube_videos:
            video_title, video_duration_minute, video_duration_second = get_youtube_video_property(youtube_link)

            # Include the video to filtered video list if it's below 5 mins
            if int(video_duration_minute) < 5:
                direct_download_link = "http://mp3you.tube/get/?direct=" + youtube_link
                video_duration = "[ " + video_duration_minute + ":" + video_duration_second + " ]"

                # Append video direct link and also video default property
                filtered_video_link.append(youtube_link)
                filtered_video_description.append(str(video_title + "\n" + str(video_duration)))

            # Cap the result to max 5 videos (limit of carousel)
            if len(filtered_video_link) >= 5:
                break

        # If there's no video under 5 mins
        if len(filtered_video_link) == 0:
            report = Lines.play_music("nothing to play")
            #line_bot_api.push_message(address, TextSendMessage(text=report))
            cont = False

    if cont:
        send_detail_result(filtered_video_link, filtered_video_description)

