import urllib,requests,random
from bs4 import BeautifulSoup

class OtherUtil:
    def remove_symbols(word):
        symbols = "!@#$%^&*()+=-`~[]{]\|;:/?.>,<\""
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


def getting_page_title(mod_page) :
    try :
        first_heading = mod_page.findAll("h1",{"id":"firstHeading"})
        page_title = first_heading[0].string
        return page_title
    except :
        return "page title doesn't exist"

def is_specific(mod_page):
    content = str(mod_page.find_all('p'))
    keyword = ["commonly refers to","may also refer to","may refer to"]

    if any(word in content for word in keyword):
        return False
    else :
        return True

def has_disambiguation(mod_page):
    content = str(mod_page.find_all('a',{"class":"mw-disambig"}))
    keyword = ["disambiguation"]

    if any(word in content for word in keyword):
        return True
    else :
        return False

def first_paragraph_coordinate(mod_page):
    content = str(mod_page.find('p'))
    keyword = ["coordinate"]

    if any(word in content for word in keyword):
        return True
    else :
        return False

def get_paragraph(mod_page,cond='first'):

    def filter_paragraph_contents(content,start_sym='<',end_sym='>'):
        isfilter = (start_sym or end_sym) in content
        while isfilter :
            start_index = content.find(start_sym)
            stop_index = content.find(end_sym)+1
            content = content.replace(str(content[start_index:stop_index]),"")
            isfilter = (start_sym or end_sym) in content
        return content
    if cond == 'first' :
        content = mod_page.find('p')
    elif cond == 'second' :
        content = mod_page.find_all('p')[1]
    content = filter_paragraph_contents(str(content), '<', '>')
    content = filter_paragraph_contents(str(content), '[', ']')
    return content

def show_suggestion(mod_page) :
    suggestion = []
    keyword = ['All pages beginning with ', 'disambiguation', 'Categories', 'Disambiguation',
               'Place name disambiguation ', 'All article disambiguation ', 'All disambiguation ', 'Talk',
               'Contributions', 'Article', 'Talk', 'Read', 'Main page', 'Contents', 'Featured content',
               'Current events', 'Random article', 'Donate to Wikipedia', 'Help', 'About Wikipedia', 'Community portal',
               'Recent changes', 'Contact page', 'What links here', 'Related changes', 'Upload file', 'Special pages',
               'Wikidata item', 'Wikispecies', 'Cebuano', 'Čeština', 'Deutsch', 'Eesti', 'Español', 'Français',
               '한국어', 'Italiano', 'עברית', 'Latviešu', 'Magyar', 'Nederlands', '日本語', 'Norsk bokmål', 'پښتو',
               'Polski', 'Português', 'Русский', 'Simple English', 'Slovenščina', 'Српски / srpski',
               'Srpskohrvatski / српскохрватски', 'Suomi', 'Svenska', 'Türkçe', 'Українська', 'اردو', 'Volapük',
               'Edit links', 'Creative Commons Attribution-ShareAlike License', 'Terms of Use', 'Privacy Policy',
               'Privacy policy', 'About Wikipedia', 'Disclaimers', 'Contact Wikipedia', 'Developers', 'Cookie statement']

    links = mod_page.find_all('a')

    for link in links :
        href = str(link.get("href"))
        if "/wiki/" in (href[:6]) : # to eliminate wiktionary links
            if link.string is not None :
                if not (any(word in link.string for word in keyword)):
                    suggestion.append(link.string)
    suggestion = suggestion[:10]
    return suggestion

def get_search_keyword():

    split_text = OtherUtil.filter_words(text)
    keyword = []
    for word in split_text :
        if "'" in word :
            keyword.append(word)

    if keyword == []:
        return
    else:
        keyword = " ".join(keyword)
        keyword.replace(" ","_")
        return keyword

def get_search_language():

    try :
        split_text = OtherUtil.filter_words(text)
        index_now = 0
        for word in split_text :
            if word == "wiki" :
                index_found = index_now - 1
                break
            index_now = index_now + 1
        language = split_text[index_found]

    except :
        language = 'en' # default search language

    return language

text = "meg, find me information 'orion constellation' intel en wiki"

keyword = get_search_keyword()
language = get_search_language()


if keyword != None : 
    try :
        keyword = keyword[1:-1]
        page_url = "https://"+language+".wikipedia.org/wiki/"+keyword
        req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        page_source_code_text = con.read()
        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
        exist = True
    except :
        print(language+" wikipedia does not have an article about '"+keyword+"'")
        exist = False
    
    if exist :
        title = getting_page_title(mod_page)
        if is_specific(mod_page) :
            print(title)
            if has_disambiguation(mod_page):
                print("(this page has disambiguation)")
                print()
            else:
                pass
    
            if first_paragraph_coordinate(mod_page):
                print(get_paragraph(mod_page,'second'))
                print("\nFor more detailed info :",page_url)
            else:
                print(get_paragraph(mod_page,'first'))
                print("\nFor more detailed info :", page_url)
        else :
            print("'"+title+"\' is not a specific keyword,..")
            print("Here's some list of \'"+title+"\' people usually search for : \n")
            suggestion = show_suggestion(mod_page)
            suggestion = "\n".join(suggestion)
            print(suggestion)

else :
    print("no keyword found")








