
def show_cinema_movie_schedule():
    def get_cinema_list(search_keyword):
        if search_keyword == [] or search_keyword == [""]:
            report = Lines.show_cinema_movie_schedule("No keyword found")
            line_bot_api.push_message(address, TextSendMessage(text=report))
        else:
            cinemas_name = []
            cinemas_link = []
            page_url = "https://www.cgv.id/en/schedule/cinema/"
            try:
                req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
                con = urllib.request.urlopen(req)
                page_source_code_text = con.read()
                mod_page = BeautifulSoup(page_source_code_text, "html.parser")
            except:
                report = Lines.show_cinema_movie_schedule("failed to open the the page")
                line_bot_api.push_message(address, TextSendMessage(text=report))

            links = mod_page.findAll('a', {"class": "cinema_fav"})
            for link in links:
                cinema_name = link.string
                cinema_link = "https://www.cgv.id" + link.get("href")
                if all(word in cinema_name.lower() for word in search_keyword):
                    cinemas_name.append(cinema_name)
                    cinemas_link.append(cinema_link)

            cinemas = zip(cinema_name,cinema_link)
            return cinemas

    def get_movie_data(cinema):

        movielist = []
        desclist = []
        schedulelist = []

        req = urllib.request.Request(cinema, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        page_source_code_text = con.read()
        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
        schedule_table = str(mod_page.find("table", {"class": "table-theater-det"}))
        mod_schedule_table = BeautifulSoup(schedule_table, "html.parser")

        movies = movies_data.findAll("a")  # getting the movie name and desc
        for movie in movies:
            movie_name = movie.string
            movie_desc = "https://www.cgv.id" + movie.get("href")
            movielist.append(movie_name)
            desclist.append(movie_desc)

        schedules = mod_schedule_table.findAll("a", {"id": "load-schedule-time"})  # getting the movie schedule
        last_movie = ""
        for schedule in schedules:
            movie_title = schedule.get("movietitle")
            time = schedule.string
            if movie_title != last_movie:
                schedulelist.append("#")
                last_movie = movie_title
            if time != ", ":
                schedulelist.append(time)

        # re formatting the schedulelist
        schedulelist = " ".join(schedulelist)
        schedulelist = schedulelist.split("#")
        schedulelist.remove("")

        moviedata = zip(movielist, desclist, schedulelist)
        return moviedata


    def request_cinema_list():
        confirmation = Lines.show_cinema_movie_schedule("asking to show cinema list")
        buttons_template = ButtonsTemplate(text=confirmation, actions=[
            PostbackTemplateAction(label="Sure...", data='request cgv cinema list please', text='Sure...')])
        template_message = TemplateSendMessage(alt_text=confirmation, template=buttons_template)
        line_bot_api.push_message(address, template_message)

    keyword = ['are', 'at', 'can', 'cgv', 'film', 'help', 'is', 'kato', 'list', 'me', 'meg', 'megumi', 'movie',
               'movies', 'playing', 'please', 'pls', 'schedule', 'show', 'showing', 'what']

    search_keyword = OtherUtil.filter_words(text)
    search_keyword = OtherUtil.filter_keywords(search_keyword, keyword)

    cinemas = get_cinema_list(search_keyword) # return a list with [ cinema name , cinema url]

    found_cinema = []
    for cinema in cinemas :
        found_cinema.append(cinema[0])


    if len(found_cinema) <= 0 :
        reply = Lines.show_cinema_movie_schedule("No cinema found") % (", ".join(search_keyword))
        ask_for_request = True
    elif len(found_cinema) > 2:
        reply = Lines.show_cinema_movie_schedule("Too much cinemas") % (", ".join(search_keyword))
        ask_for_request = True
    else:
        try:
            reply = []
            reply.append(Lines.show_cinema_movie_schedule("header") % (", ".join(search_keyword)))
            for cinema in cinemas: # iterate the name only
                cinema_name = cinema[0]                 # cinema [0] is the cinema name
                moviedata = get_movie_data(cinema[1])   # cinema [1] is the cinema link
                reply.append(Lines.show_cinema_movie_schedule("cinema name") % cinema_name)
                for data in moviedata:
                    reply.append(data[0])  # movie title
                    reply.append(data[1])  # movie description
                    reply.append(data[2])  # movie schedule
                    reply.append("\n")

            reply.append(Lines.show_cinema_movie_schedule("footer"))
            reply = "\n".join(reply)
            ask_for_request = False
        except:
            reply = Lines.show_cinema_movie_schedule("failed to show movie data")

    line_bot_api.reply_message(token, TextSendMessage(text=reply))
    if ask_for_request:
        request_cinema_list()



def show_cinema_list():

        cinema_list = []
        page_url = "https://www.cgv.id/en/schedule/cinema/"

        req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        page_source_code_text = con.read()
        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
        cinemas = mod_page.findAll('a', {"class": "cinema_fav"})
        cinema_list.append(Lines.show_cinema_movie_schedule("show cinema list"))
        for cinema in cinemas:
            cinema = cinema.string
            cinema_list.append(cinema)

        report = "\n".join(sorted(cinema_list))
        if len(report) > 1800 :
            report1 = report[:1800]+"..."
            report2 = "..."+report[1801:]
            line_bot_api.push_message(address, TextSendMessage(text=report1))
            line_bot_api.push_message(address, TextSendMessage(text=report2))
        else :
            line_bot_api.push_message(address, TextSendMessage(text=report))


