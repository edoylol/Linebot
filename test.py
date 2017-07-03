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

stats = [('HP','11535'),('ATK','747'),('CRI RATE%','15')]
for (stat_type,stat_value) in stats:
    stat = '{:<15}  {:>6}'.format(stat_type, stat_value)
    print(stat)

search_keyword = "camilla"

page_url = "https://summonerswar.co/water-valkyrja-camilla/"
req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
con = urllib.request.urlopen(req)
page_source_code_text = con.read()
mod_page = BeautifulSoup(page_source_code_text, "html.parser")
images = mod_page.find_all("img")
for image in images :
    image_src = image.get("src")
    if search_keyword in image_src.lower() :
        print(image_src)