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

with open('text.txt','r') as f :
    page_source_code_text = f.readlines()
    page_source_code_text = "".join(page_source_code_text)
    mod_page = BeautifulSoup(page_source_code_text, "html.parser")
    first_mod = BeautifulSoup(str(mod_page.findAll("div", {"class": "_39k5 _5s6c"})), "html.parser")
    second_mod = BeautifulSoup(str(first_mod.findAll("ul", {"class": "_5a_q _5yj1"})), "html.parser")
    lists = second_mod.find_all("a")

    result = []
    result.append("{")
    for list in lists:
        text = list.get("href")
        title = list.text.strip()
        index_start = text.find("pasted.co")
        index_stop = text.find("&h=")
        pasted_link = text[index_start:index_stop]
        pasted_link = "http://" + pasted_link.replace("%2F", "/")
        result.append("\""+title.lower()+"\":\""+pasted_link+"\",")
    result.append("}")
    result = "\n".join(result)
    print(result)