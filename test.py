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
        print(report)

        # Send back up notification to Dev, to let Dev know that something unexpected happened
        if True:
            report = (Lines.dev_mode_general_error("dev") % (function_name, exception_detail))
            print(report)


def show_cinema_movie_schedule():
        """ Function to show list of movies playing at certain cinemas.
         Usage example : Meg, can you show me citylink xxi movie schedule ? """

        cont = True

        # If the cinema is not specified, send notification, stop process
        if not (any(word in text for word in ["xxi", "cgv"])):
            report = Lines.show_cinema_movie_schedule("specify the company")
            print(report)
            cont = False

        # If the cinema is specified either xxi or cgv
        if cont:

            # The cinema is one of the XXI cinemas
            if "xxi" in text:

                def get_cinema_keyword():
                    """ Function to get cinema's name keyword from text """

                    keyword = ['are', 'at', 'can', 'film', 'help', 'is', 'kato', 'list', 'me', 'meg', 'megumi',
                               'movie', 'movies', 'playing', 'please', 'pls', 'schedule', 'show',
                               'showing', 'you', 'xxi', 'what']
                    search_keyword = OtherUtil.filter_words(text)
                    search_keyword = OtherUtil.filter_keywords(search_keyword, keyword)

                    return search_keyword

                def get_cinema_list(search_keyword):
                    """ Function to return available cinema list """

                    cinemas = []
                    page_url = "http://www.21cineplex.com/theaters"

                    # Open the XXI page
                    try:
                        print(" try to open theaters page")
                        req = requests.get(page_url, proxies={"https": "115.166.118.83: 8080"})
                        print(" open theaters page success")
                        page_source_code_text = req.content
                        mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                    # Failed to open the XXI page
                    except Exception:
                        report = Lines.show_cinema_movie_schedule("failed to open the the page")
                        print(report)
                        raise

                    # Get the cinema's link that fulfil the keyword
                    links = mod_page.findAll('a')
                    for link in links:
                        cinema_link = link.get("href")
                        if all(word in cinema_link for word in
                               (["http://www.21cineplex.com/theater/bioskop"] + search_keyword)):
                            cinemas.append(cinema_link)

                    # Just in case there are duplicate link, remove the duplicates
                    if len(cinemas) > 1:
                        cinemas = set(cinemas)

                    print("\n", cinemas)
                    return cinemas

                def get_movie_data(cinema):
                    """ Function to return the movie's data, in form of (movie, description, schedule) """

                    # Default variable
                    movielist = []
                    desclist = []
                    schedulelist = []

                    # Open the page to parse
                    try:
                        req = urllib.request.Request(cinema, headers={'User-Agent': "Magic Browser"})
                        print(" open theaters page sucess")
                        con = urllib.request.urlopen(req)
                        page_source_code_text = con.read()
                        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
                        mod_schedule_table = BeautifulSoup(
                            str(mod_page.find("table", {"class": "table-theater-det"})), "html.parser")

                        print("\n",mod_schedule_table)

                    # If failed to open the page
                    except Exception:
                        report = Lines.show_cinema_movie_schedule("failed to open the the page")
                        print(report)
                        raise

                    # Finding all movie's title, description, and showtime
                    try:
                        # Get the movie's title and description
                        movies = mod_schedule_table.findAll('a')
                        for movie in movies:

                            # Get the title
                            title = movie.string
                            if title is not None:
                                movielist.append(title)

                                # Get the description (nb: put here to limit number of desc <= number of title)
                                movie_description = movie.get("href")

                                # If the description is already existed before, don't append it again
                                if movie_description in desclist:
                                    desclist.append("  ")
                                else:
                                    desclist.append(movie_description)

                        # Get movie's showtime
                        showtimes = mod_schedule_table.findAll("td", {"align": "right"})
                        for showtime in showtimes:
                            schedulelist.append(showtime.string)

                    except Exception:
                        report = Lines.show_cinema_movie_schedule("failed to get movie data")
                        print(report)
                        raise

                    moviedata = zip(movielist, desclist, schedulelist)
                    return moviedata

                def get_cinema_name(cinema_link):
                    """ Function to get cinema name """

                    # Get the cinema name
                    index_start = cinema_link.find("-") + 1
                    index_end = cinema_link.find(",")
                    cinema_name = cinema_link[index_start:index_end]
                    cinema_name = cinema_name.replace("-", " ")

                    # Special case TSM
                    if cinema_name == "tsm xxi":
                        if cinema_link == "http://www.21cineplex.com/theater/bioskop-tsm-xxi,186,BDGBSM.htm":
                            cinema_name = "tsm xxi (Bandung)"
                        elif cinema_link == "http://www.21cineplex.com/theater/bioskop-tsm-xxi,335,UPGTSM.htm":
                            cinema_name = "tsm xxi (Makassar)"

                    return cinema_name

                def request_cinema_list():
                    """ Function to send confirmation whether send request cinema list or not """

                    # Generate button template
                    confirmation = Lines.show_cinema_movie_schedule("asking to show cinema list")
                    print(confirmation)
                    """
                    buttons_template = ButtonsTemplate(text=confirmation, actions=[
                        PostbackTemplateAction(label="Sure...", data='request xxi cinema list please',
                                               text='Sure...')])
                    template_message = TemplateSendMessage(alt_text=confirmation, template=buttons_template)

                    # Send the template
                    line_bot_api.push_message(address, template_message)"""

                search_keyword = get_cinema_keyword()

                # If the cinema keyword is unspecified
                if search_keyword == [] or search_keyword == [""]:
                    report = Lines.show_cinema_movie_schedule("No keyword found")
                    print(report)
                    ask_for_request = True

                # If keyword is found
                else:
                    cinemas = get_cinema_list(search_keyword)

                    # Process the cinemas found
                    if len(cinemas) <= 0:
                        report = Lines.show_cinema_movie_schedule("No cinema found") % (", ".join(search_keyword))
                        ask_for_request = True

                    elif len(cinemas) > 2:
                        report = Lines.show_cinema_movie_schedule("Too many cinemas") % (", ".join(search_keyword))
                        ask_for_request = True

                    # If there is one (or 2 at most) cinema(s) found, then process it
                    else:

                        # Generate header for every type of reply
                        report = [Lines.show_cinema_movie_schedule("header") % str(", ".join(search_keyword))]

                        # Re-formatting data before sending
                        try:

                            # Getting data from every cinemas which fulfil keywords
                            for cinema in cinemas:

                                # Gather the data and re-format it
                                cinema_name = get_cinema_name(cinema)
                                movie_data = get_movie_data(cinema)
                                report.append(Lines.show_cinema_movie_schedule("cinema name") % cinema_name)

                                for data in movie_data:
                                    report.append(data[0])  # movie title
                                    report.append(data[1])  # movie description
                                    report.append(data[2])  # movie schedule
                                    report.append("\n")

                            report.append(Lines.show_cinema_movie_schedule("footer"))
                            report = "\n".join(report)

                            ask_for_request = False

                        # If there's unexpected error related to formatting
                        except Exception:
                            report = Lines.show_cinema_movie_schedule("failed to show movie data")
                            print(report)
                            raise

                    # Send report for every conditions
                    print(report)

                # If there's some problem with cinema's name, ask to send cinema list
                if ask_for_request:
                    request_cinema_list()

            # The cinema is one of the CGV cinemas
            elif "cgv" in text:

                def get_cinema_list(search_keyword):
                    """ Function to return available cinema list """

                    cinemas_name = []
                    cinemas_link = []
                    page_url = "https://www.cgv.id/en/schedule/cinema/"

                    # Open the web page to parse data
                    try:
                        req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                        con = urllib.request.urlopen(req)
                        page_source_code_text = con.read()
                        mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                    # Failed to open the page
                    except Exception:
                        report = Lines.show_cinema_movie_schedule("failed to open the the page")
                        print(report)
                        raise

                    # Parse the web page to find cinema name and link
                    links = mod_page.findAll('a', {"class": "cinema_fav"})
                    for link in links:
                        cinema_name = link.string
                        cinema_link = "https://www.cgv.id" + link.get("href")

                        # If there's cinema's name which fulfil the search keyword, append it to list
                        if all(word in cinema_name.lower() for word in search_keyword):
                            cinemas_name.append(cinema_name)
                            cinemas_link.append(cinema_link)

                    cinemas = zip(cinemas_name, cinemas_link)
                    return cinemas

                def get_movie_data(cinema):
                    """ Function to return the movie's data, in form of (movie, description, schedule) """

                    # Initializing general variable
                    movielist = []
                    desclist = []
                    schedulelist = []

                    # Open the web page to parse data
                    try:
                        req = urllib.request.Request(cinema, headers={'User-Agent': "Magic Browser"})
                        con = urllib.request.urlopen(req)
                        page_source_code_text = con.read()
                        mod_page = BeautifulSoup(page_source_code_text, "html.parser")

                    # If failed to open the page
                    except Exception:
                        report = Lines.show_cinema_movie_schedule("failed to open the the page")
                        line_bot_api.push_message(address, TextSendMessage(text=report))
                        raise

                    # Gather the data
                    try:
                        # Get the raw data
                        mod_schedule_table = BeautifulSoup(
                            str(mod_page.findAll("div", {"class": "schedule-lists"})), "html.parser")
                        movies_data = BeautifulSoup(
                            str(mod_schedule_table.findAll("div", {"class": "schedule-title"})), "html.parser")
                        movies = movies_data.findAll("a")

                        # Get the movie's name and description
                        for movie in movies:
                            movie_name = movie.string
                            movie_desc = "https://www.cgv.id" + movie.get("href")
                            movielist.append(movie_name)
                            desclist.append(movie_desc)

                    # If failed to get the data
                    except Exception:
                        report = Lines.show_cinema_movie_schedule("failed to get movie data")
                        line_bot_api.push_message(address, TextSendMessage(text=report))
                        raise

                    # Get the movie's schedule
                    schedules = mod_schedule_table.findAll("a", {"id": "load-schedule-time"})
                    last_movie = ""  # Iteration of the last processed movie
                    for schedule in schedules:
                        movie_title = schedule.get("movietitle")
                        time = schedule.string

                        # Determine whether current movie is different from the last one or not
                        if movie_title != last_movie:
                            schedulelist.append("#")
                            last_movie = movie_title

                        # If the showtime is available
                        if time != ", ":
                            schedulelist.append(time)

                    # Re-formatting the schedulelist
                    schedulelist = " ".join(schedulelist)
                    schedulelist = schedulelist.split("#")

                    # Try to remove empty space in schedule list
                    try:
                        schedulelist.remove("")
                    except Exception:
                        pass

                    moviedata = zip(movielist, desclist, schedulelist)
                    return moviedata

                def request_cinema_list():
                    """ Function to ask whether to show cinema list or not """

                    # Generate the button template
                    confirmation = Lines.show_cinema_movie_schedule("asking to show cinema list")
                    buttons_template = ButtonsTemplate(text=confirmation, actions=[
                        PostbackTemplateAction(label="Sure...", data='request cgv cinema list please',
                                               text='Sure...')])
                    template_message = TemplateSendMessage(alt_text=confirmation, template=buttons_template)
                    line_bot_api.push_message(address, template_message)

                # First filter of keywords and default text filter
                keyword = ['are', 'at', 'can', 'cgv', 'film', 'help', 'is', 'kato', 'list', 'me',
                           'meg', 'megumi', 'movie', 'movies', 'playing', 'please', 'pls',
                           'schedule', 'show', 'showing', 'what']
                search_keyword = OtherUtil.filter_words(text)
                search_keyword = OtherUtil.filter_keywords(search_keyword, keyword)

                # If keyword is unspecified
                if search_keyword == [] or search_keyword == [""]:
                    report = Lines.show_cinema_movie_schedule("No keyword found")
                    line_bot_api.push_message(address, TextSendMessage(text=report))
                    ask_for_request = True

                # If keyword is found
                else:
                    # Get cinema's name and cinema's url in a list
                    cinemas = get_cinema_list(search_keyword)

                    # Re-format the cinema's name and cinema's link before append to main cinemas data
                    found_cinema_name = []
                    found_cinema_link = []
                    for cinema in cinemas:
                        found_cinema_name.append(cinema[0])
                        found_cinema_link.append(cinema[1])

                    found_cinema = zip(found_cinema_name, found_cinema_link)

                    # Process the cinemas found
                    if len(found_cinema_name) <= 0:
                        report = Lines.show_cinema_movie_schedule("No cinema found") % (", ".join(search_keyword))
                        ask_for_request = True
                    elif len(found_cinema_name) > 2:
                        report = Lines.show_cinema_movie_schedule("Too many cinemas") % (", ".join(search_keyword))
                        ask_for_request = True

                    # If there is one (or 2 at most) cinema(s) found, then process it
                    else:

                        # Generate header for every type of reply
                        report = [Lines.show_cinema_movie_schedule("header") % str(", ".join(search_keyword))]

                        # Re-formatting data before sending
                        try:

                            # Gather the data and re-format it
                            for cinema in found_cinema:
                                cinema_name = cinema[0]  # cinema [0] is the cinema name
                                moviedata = get_movie_data(cinema[1])  # cinema [1] is the cinema link
                                report.append(Lines.show_cinema_movie_schedule("cinema name") % cinema_name)
                                for data in moviedata:
                                    report.append(data[0])  # movie title
                                    report.append(data[1])  # movie description
                                    report.append(data[2])  # movie schedule
                                    report.append("\n")

                            # Send the report to user
                            report.append(Lines.show_cinema_movie_schedule("footer"))
                            report = "\n".join(report)
                            ask_for_request = False

                        # If there's unexpected error related to formatting
                        except Exception:
                            report = Lines.show_cinema_movie_schedule("failed to show movie data")
                            line_bot_api.push_message(address, TextSendMessage(text=report))
                            raise

                    # Send report for every conditions
                    line_bot_api.push_message(address, TextSendMessage(text=report))

                # If there's some problem with cinema's name, ask to send cinema list
                if ask_for_request:
                    request_cinema_list()



text = "meg show xxi festival citylink movie schedule"
show_cinema_movie_schedule()
