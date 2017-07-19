import urllib,requests,random,time,os,urllib.request
import json
from bs4 import BeautifulSoup
from gtts import gTTS

class OtherUtil:
    def remove_symbols(word,cond="default"):
        if cond == "default" :
            symbols = "!@#$%^&*()+=-`~[]{]\|;:'/?.>,<\""
        elif cond == "for wiki search" :
            symbols = "!@#$%^&*+=-`~[]{]\|;:/?.>,<\""
        elif cond == "sw wiki":
            symbols = "1234567890!@#$%^&*()_+=-`~[]{]\|';:/?.>,<\""

        for i in range(0, len(symbols)):
            word = word.replace(symbols[i], "")  # strong syntax to remove symbols
        if len(word) > 0:
            return word

    def filter_words(text,cond="default"):
        split_text = text.split(" ")
        filtered_text = []
        for word in split_text:
            new_word = OtherUtil.remove_symbols(word,cond)
            if new_word != None:
                filtered_text.append(new_word)
        return filtered_text

    def filter_keywords(text, keyword):
        while any(word in text for word in keyword):
            for word in text:
                if word in keyword:
                    text.remove(word)
        return text

text = "meg, show me information about itb student '16516387'"

def itb_arc_database():

    def get_keyword ():

        index_start = text.find("'")
        index_end = text.rfind("'")
        keyword = text[index_start:index_end]

        return keyword

    def get_category () :
        is_default_category = False

        if any(word in text for word in ["student","students","stud","std","stds","studnt","stdnt"])  :
            category = "student"
        elif any(word in text for word in ["lecturer","lecture","prof","professor","lctrer","lctr","dr"])  :
            category = "lecturer"
        elif any(word in text for word in ["major","faculty","fclty","fclt","mjr","maj","fac","fac"]) :
            category = "major"
        else :
            category = "student"
            is_default_category = True

        return category,is_default_category

    def get_student_info():

        if search_result_count > 10 :
            max_data = 10
        else :
            max_data = search_result_count

        for i in range(0,max_data):
            student_name = ARC_ITB_api_data['result'][i]['fullname']
            student_nim = ARC_ITB_api_data['result'][i]['nim']
            student_major = ARC_ITB_api_data['result'][i]['major']['title']
            student_faculty = ARC_ITB_api_data['result'][i]['major']['faculty']['title']
            student_major_year = ARC_ITB_api_data['result'][i]['year']

            search_result.append("NIM : "+str(student_nim))
            search_result.append(student_name)
            search_result.append(student_major+" [ "+str(student_major_year)+" ]")
            search_result.append(student_faculty)
            search_result.append(" ")

        search_result.append(Lines.itb_arc_database("footer"))

    def get_lecturer_info():

        if search_result_count > 10:
            max_data = 10
        else:
            max_data = search_result_count

        for i in range(0, max_data):
            lecturer_name = ARC_ITB_api_data['result'][i]['fullname']
            lecturer_nip = ARC_ITB_api_data['result'][i]['nip']

            search_result.append(lecturer_name)
            search_result.append("NIP : "+str(lecturer_nip))
            search_result.append(" ")
        search_result.append(Lines.itb_arc_database("footer"))

    def get_major_info():

        if search_result_count > 10:
            max_data = 10
        else:
            max_data = search_result_count

        for i in range(0, max_data):
            major_name = ARC_ITB_api_data['result'][i]['title']
            major_code = ARC_ITB_api_data['result'][i]['code']
            major_faculty = ARC_ITB_api_data['result'][i]['faculty']['title']

            search_result.append("[ "+str(major_code)+" ] " + major_name)
            search_result.append(major_faculty)
            search_result.append(" ")
        search_result.append(Lines.itb_arc_database("footer"))

    def send_header():
        report = []

        report.append(Lines.itb_arc_database("header") % itb_keyword)
        if is_default_category :
            report.append(" ")
            report.append(Lines.itb_arc_database("default category"))

        report = "\n".join(report)
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def send_result_count():
        report = []

        report.append(" ")
        if search_result_count > 1 :
            report.append(Lines.itb_arc_database("count result plural") % str(search_result_count))
            if search_result_count > 10 :
                report.append(" ")
                report.append(Lines.itb_arc_database("only send top 10"))
        elif search_result_count == 1 :
            report.append(Lines.itb_arc_database("count result one"))
        else :
            report.append(Lines.itb_arc_database("not found"))

        report = "\n".join(report)
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    def send_detail_info():
        report = "\n".join(search_result)
        line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))

    itb_keyword = get_keyword()
    search_category,is_default_category = get_category()

    ARC_api_call = "https://nim.arc.itb.ac.id/api//search/"+search_category+"/?keyword="+itb_keyword+"&page=1&count=30"
    ARC_ITB_api_data = requests.get(ARC_api_call).json()
    search_result = []

    search_result_count = ARC_ITB_api_data['totalCount']

    send_header()
    send_result_count()

    if search_result_count > 0 :
        if search_category == "student" :
            get_student_info()
        elif search_category == "lecturer" :
            get_lecturer_info()
        elif search_category == "major" :
            get_major_info()

        send_detail_info()


itb_arc_database()
