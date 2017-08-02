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


def stalk_instagram():
    """ Function to stalk instagram account and return user profile and top 5 pic """

    def get_instagram_page_keyword():
        """ Function to return full instagram page link """

        # Find the index of apostrophe
        index_start = text.find("'") + 1
        index_stop = text.rfind("'")

        # Determine whether 2 apostrophe are exist and the text exist
        text_available = (index_stop - index_start) >= 1

        # If user (keyword) exist, crop it
        if text_available:
            keyword = text[index_start:index_stop]
            return keyword

        else:
            return "keyword not found"

    def get_insta_raw_data(page_url):
        """ Function to crawl instagram page to get various data about someone """

        # Try to open instagram page
        try:
            req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
            con = urllib.request.urlopen(req)
            page_source_code_text = con.read()
            mod_page = BeautifulSoup(page_source_code_text, "html.parser")

        except:
            report = Lines.general_lines("failed to open page") % page_url
            line_bot_api.push_message(address, TextSendMessage(text=report))
            raise

        # Parse the raw data, get the script part , select the longest one
        try:
            rawdatas = mod_page.find_all("script")
            temp = []
            for x in rawdatas:
                temp.append(str(x))
            rawdatas = max(temp, key=len)

            # Crop the pre-json part
            text = rawdatas
            index_start = text.find("{")
            index_stop = text.rfind("}") + 1
            rawdatas = str(text[index_start:index_stop])

        except:
            report = Lines.general_lines("formatting error") % "instagram's page"
            line_bot_api.push_message(address, TextSendMessage(text=report))
            raise

        # Convert to JSON data
        json_rawdata = json.loads(rawdatas)

        return json_rawdata

    def get_insta_user_data(json_rawdata):
        """ Function to get insta user data """

        # Get user fullname
        try:
            insta_fullname = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["full_name"]
        except:
            insta_fullname = "no data"

        # Get user username
        try:
            insta_username = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["username"]
        except:
            insta_username = "no data"

        # Get user biography
        try:
            insta_biography = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["biography"]
        except:
            insta_biography = "no data"

        # Get user follower count
        try:
            insta_follower = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["followed_by"]["count"]
        except:
            insta_follower = "no data"

        # Get user following count
        try:
            insta_following = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["follows"]["count"]
        except:
            insta_following = "no data"

        # Get user privacy status
        try:
            insta_private = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["is_private"]
        except:
            insta_private = "no data"

        # Return all the data found
        return insta_fullname, insta_username, insta_biography, insta_follower, insta_following, insta_private

    def get_insta_media_data(json_rawdata):
        """ Function to get insta media data """

        # Try to get the medias data
        try:
            insta_media = json_rawdata["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]
        except:
            report = Lines.general_lines("formatting error") % "posted-media's"
            line_bot_api.push_message(address, TextSendMessage(text=report))
            raise

        # Set default value
        insta_image_link_list = []
        insta_image_caption_list = []
        insta_image_like_list = []

        # Get top 5 image / video data
        for item in insta_media:
            if len(insta_image_link_list) < 5:

                # Get the media link
                try:
                    insta_image = item["thumbnail_src"]
                    insta_image_link_list.append(insta_image)
                except:
                    break

                # Get the media caption
                try:
                    insta_image_caption = item["caption"]
                    insta_image_caption_list.append(insta_image_caption)
                except:
                    insta_image_caption_list.append("-")

                # Get the media like count
                try:
                    insta_image_like = item["likes"]["count"]
                    insta_image_like_list.append(insta_image_like)
                except:
                    insta_image_like_list.append("-")

            # If there's more than 5 item in image_link_list, stop it
            else:
                break

        return insta_image_link_list, insta_image_caption_list, insta_image_like_list

    def send_header():
        """ Function to send header , confirmation that stalking on the way """

        report = (Lines.stalk_instagram("header")).format(keyword)
        line_bot_api.push_message(address, TextSendMessage(text=report))

    def send_insta_user_info(insta_fullname, insta_username, insta_biography, insta_follower, insta_following):
        """ Function to send instagram page user information """

        # Generate report about user information
        report = [Lines.stalk_instagram("user information header")]
        try:
            report.append("Fullname : " + insta_fullname)
            report.append("Instagram username: " + insta_username)
            report.append("Biography : " + insta_biography)
            report.append("Follower : " + insta_follower)
            report.append("Following : " + insta_following)
        except:
            pass

        report = "\n".join(report)
        line_bot_api.push_message(address, TextSendMessage(text=report))

    def send_insta_user_pic(insta_image_link_list, insta_image_caption_list, insta_image_like_list):
        """ Function to send instagram page media (up to 5) """

        image_count = len(insta_image_link_list)

        carousel_text = []
        header_pic = []
        alt_text = ("Stalking "+keyword+"'s instagram...")
        # Generate and format the data used by carousel
        for i in range(0, image_count):

            # Format image caption
            if len(insta_image_caption_list[i]) > 40:
                image_caption = "\""+insta_image_caption_list[i][:40]+"...\""
            else:
                image_caption = "\""+insta_image_caption_list[i]+"\""

            # Format image likes count
            image_like_count = "Liked : "+insta_image_like_list[i]

            # Join them together and append to carousel text
            carousel_text.append(str(image_caption+"\n"+image_like_count))

            # Append image link to header pic
            header_pic.append(insta_image_link_list[i])

        if image_count == 0:
            report = Lines.stalk_instagram("picture count 0")
            line_bot_api.push_message(address, TextSendMessage(text=report))

        elif image_count == 1:

        elif image_count == 2:
            pass
        elif image_count == 3:
            pass
        elif image_count == 4:
            pass
        elif image_count == 5:
            pass

        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text=carousel_text[0][:60], thumbnail_image_url=header_pic[0], actions=[
                URITemplateAction(label='See detail..', uri=header_pic[0])]),
            CarouselColumn(text=carousel_text[1][:60], thumbnail_image_url=header_pic[1], actions=[
                URITemplateAction(label='See detail..', uri=header_pic[1])]),
            CarouselColumn(text=carousel_text[2][:60], thumbnail_image_url=header_pic[2], actions=[
                URITemplateAction(label='See detail..', uri=header_pic[2])]),
            CarouselColumn(text=carousel_text[3][:60], thumbnail_image_url=header_pic[3], actions=[
                URITemplateAction(label='See detail..', uri=header_pic[3])]),
            CarouselColumn(text=carousel_text[4][:60], thumbnail_image_url=header_pic[4], actions=[
                URITemplateAction(label='See detail..', uri=header_pic[4])]),
        ])

        template_message = TemplateSendMessage(alt_text=alt_text, template=carousel_template)
        line_bot_api.push_message(address, template_message)



    cont = True
    json_rawdata = None

    # Get the full version link
    keyword = get_instagram_page_keyword()
    page_url = "https://www.instagram.com/"+keyword+"/"

    # If the keyword is not found, stop the process
    if page_url == "keyword not found":

        report = Lines.general_lines("search fail") % "instagram id"
        line_bot_api.push_message(address, TextSendMessage(text=report))
        cont = False

    # If full version link is available, try to get raw data
    if cont:
        send_header()
        json_rawdata = get_insta_raw_data(page_url)

        # If the data is unavailable, stop the process
        if json_rawdata is None:
            report = Lines.general_lines("failed to open page") % str(keyword+"'s instagram")
            line_bot_api.push_message(address, TextSendMessage(text=report))
            cont = False

    # If the raw data is available, crawl user information and check if it's private or not
    if cont:
        # Get and send insta page user information
        insta_fullname, insta_username, insta_biography, insta_follower, insta_following, insta_private = get_insta_user_data(json_rawdata)
        send_insta_user_info(insta_fullname, insta_username, insta_biography, insta_follower, insta_following)

        if insta_private:
            report = Lines.stalk_instagram("private")
            line_bot_api.push_message(address, TextSendMessage(text=report))
            cont = False

    # If it's not private, crawl top 5 pic and send it
    if cont:
        # Get and send insta page user media
        insta_image_link_list, insta_image_caption_list, insta_image_like_list = get_insta_media_data(json_rawdata)
        send_insta_user_pic(insta_image_link_list, insta_image_caption_list, insta_image_like_list)








text = "'brigittatifanny'"
#text = "'sylviecendana'"
#text = "'n_godjali'"
text = "'felixmartin'"
stalk_instagram()
