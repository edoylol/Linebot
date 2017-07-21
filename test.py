import urllib,requests,random,time,os,urllib.request,io
import json
import unshortenit
import Database
from bs4 import BeautifulSoup

class OtherUtil:
    def remove_symbols(word,cond="default"):
        if cond == "default" :
            symbols = "!@#$%^&*()+=-`~[]{}\|;:'/?.>,<\""
        elif cond == "for wiki search" :
            symbols = "!@#$%^&*+=-`~[]{}\|;:/?.>,<\""
        elif cond == "sw wiki":
            symbols = "1234567890!@#$%^&*()_+=-`~[]{}\|';:/?.>,<\""

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


def get_file_id(link):
    mirror_creator_keyword = "https://www.mirrorcreator.com/files/"
    index_start = link.find(mirror_creator_keyword) + len(mirror_creator_keyword)
    index_stop = index_start + 8
    file_id = link[index_start:index_stop]
    return str(file_id)

anime_pasted_link = "http://pasted.co/ecfe642a"

page_url = anime_pasted_link + "/new.php"
req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
con = urllib.request.urlopen(req)
page_source_code_text = con.read()
mod_page = BeautifulSoup(page_source_code_text, "html.parser")
datas = mod_page.find("textarea", {"class": "pastebox rounded"})
primary_download_link_list = datas.text.split("\n")  # get the list of links

temp_list = []
for element in primary_download_link_list :
    if "http" in element :
        temp_list.append(element)

primary_download_link_list = temp_list
del temp_list

