import urllib,requests,random
from bs4 import BeautifulSoup

class OtherUtil:
    def remove_symbols(word):
        symbols = "1234567890!@#$%^&*()_+=-`~[]{]\|';:/?.>,<\""
        for i in range(0, len(symbols)):
            word = word.replace(symbols[i], "")  # strong syntax to remove symbols
        if len(word) > 0:
            return word

    def filter_words(text):
        split_text = text.split(" ")
        filtered_text = []
        for word in split_text:
            new_word = OtherUtil.remove_symbols(word)
            if new_word != None:
                filtered_text.append(new_word)
        return filtered_text

    def filter_keywords(text, keyword):
        while any(word in text for word in keyword):
            for word in text:
                if word in keyword:
                    text.remove(word)
        return text





page_url = "https://summonerswar.co/?s=(theo)"
req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
con = urllib.request.urlopen(req)
page_source_code_text = con.read()
mod_page = BeautifulSoup(page_source_code_text, "html.parser")
search_table = BeautifulSoup(str(mod_page.findAll("div", {"class": "loop list row"})), "html.parser")
links = search_table.find_all("a")
for link in links:
    title_text = link.text.strip().lower()
    link = link.get("href")
    if all(word in link for word in ['theo']) or all(word in title_text for word in ['theo']):
        print( link)

