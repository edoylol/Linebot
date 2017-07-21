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

lines = ["Here's the 2017 and 2016 anime list,..\nMaybe you need it..",
                 "I can only grab the links if the title is listed here..",
                 "Please check first whether your anime is listed or not",
                 "How about take a look at those list first?",
                 "Here's the list of all animes which has download links.."]

for x in lines :
    print(x, len(x))