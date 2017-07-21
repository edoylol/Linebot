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

file_id = "YDXT8AUT"
hostid=900
result = []

page_url = "https://www.mirrorcreator.com/downlink.php?uid=" + file_id
post_data = dict(uid=file_id, hostid=hostid)  # 99 is for dropjify , uid is the file name also
req_post = requests.post(page_url, data=post_data)
page_source_code_text_post = req_post.text
mod_page = BeautifulSoup(page_source_code_text_post, "html.parser")
final_download_link = mod_page.find("a", {"target": "_blank"})
result.append("Ep. " + str(3) + " : " + final_download_link.get("href"))
print(result)