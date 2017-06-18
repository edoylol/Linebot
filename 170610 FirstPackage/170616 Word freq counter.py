import requests, operator, Storage
from bs4 import BeautifulSoup


def start(url):
    word_list=[]
    source_code = requests.get(url).text
    soup = BeautifulSoup(source_code,"html.parser")
    for links in soup.findAll('div',{"class":"text"}):
        string = links.string
        words = string.lower().split()
        for word in words :
            word_list.append(word)
    clean_word_list = clear_symbols(word_list)
    dic = word_dictionary(clean_word_list)
    for key , value in dic :
        print(key,value)

def clear_symbols(word_list):
    new_list = []
    for word in word_list :
        symbols = "1234567890!@#$%^&*()_+=-`~[]{]\|;:'/?.>,<\""
        for i in range(0,len(symbols)):
            word = word.replace(symbols[i],"")      #strong syntax to remove symbols
        if len(word) > 0 :
            #print(word)
            new_list.append(word)
    return new_list

def word_dictionary(clean_word_list):
    word_count = {}
    for word in clean_word_list :
        if word in word_count :
            word_count[word] = word_count[word] + 1
        else :
            word_count[word] = 1

    # key & itemgetter is what you wanna sort by (0 for key, 1 for value)
    return sorted(word_count.items(),key=operator.itemgetter(1))

def bbcwordcount(url="http://www.bbc.com/news"):
    word_list = {}
    try :
        source_code = requests.get(url).text
        soup = BeautifulSoup(source_code, "html.parser")
    except :
        print("parsing error")

    try :
        for links in soup.findAll('a', {"class": "gs-c-promo-heading nw-o-link-split__anchor gs-o-faux-block-link__overlay-link gel-pica-bold"}):
            href = ("http://www.bbc.com"+links.get('href'))
            #print(href)
            try :
                newspage = requests.get(href).text
                newspage_soup = BeautifulSoup(newspage, "html.parser")

            except :
                print("opening news page error")
                break
            finally:
                print("process still going")

            for news in newspage_soup.findAll('p'):
                string = news.string
                if string is not None:
                    words = string.lower().split()
                    for word in words:
                        word = Storage.remove_symbols(word)  # at this step, the word is clean already
                        if word is not None:
                            # print(word)
                            if word in word_list:
                                word_list[word] += 1
                            else:
                                word_list[word] = 1
    except :
        print("getting news link error")


    try :

        #for key, value in sorted(word_list.items(), key=operator.itemgetter(1)):  <alternative syntax>
        for value, key in sorted(zip(word_list.values(), word_list.keys())):
            print(key,"appeared", value,"time(s)")
    except :
        print("Printing error")
    finally:
        print("Process done")

bbcwordcount("http://www.bbc.com/news")
#start("https://myanimelist.net/news")


