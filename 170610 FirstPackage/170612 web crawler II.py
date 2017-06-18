import requests
from bs4 import BeautifulSoup

"""
    page_source_code = requests.get(url)
    page_source_code_text = page_source_code.text
    mod_page = BeautifulSoup(page_source_code_text,"html.parser")
    
"""
proxies = {
  'https': 'https://54.219.138.73:8083',
}

def crawl_spider(max_pages):
    fw = open('animelink.txt', 'w')
    page = 1
    rank = 1
    while page <= max_pages :
        try :
            limit = str((page-1) * 50)
            url = 'https://myanimelist.net/topanime.php?limit='+limit
            page_source_code = requests.get(url,proxies=proxies)
            page_source_code_text = page_source_code.text
            mod_page = BeautifulSoup(page_source_code_text,"html.parser")       # I wonder why...

            for link in mod_page.findAll('a',{'hoverinfo_trigger fl-l fs14 fw-b'}) :
                try :
                    # href = link.get('href')
                    # href_str = str(href)
                    title = str(link.string)

                    try :
                        fw.write('Rank '+ str(rank) +' : ')
                        fw.write(title+'\n')


                    except Exception :
                        print("file writing error occur")

                    print(title)
                except Exception :
                    print (" link get error occur")
                rank = rank + 1

        except Exception :
            print ("url error occur")
        page = page + 1

    fw.close()
    print("process done")

def get_single_anime_data(anime_url):
    page_source_code = requests.get(anime_url)
    page_source_code_text = page_source_code.text
    mod_page = BeautifulSoup(page_source_code_text, "html.parser")
    for element in mod_page.findAll('h1', {'class' : 'h1'}):

        for anime_name in mod_page.find('span',{'itemprop' : 'name'}):
            return anime_name.string


def crawl_spiderII(max_pages):
    """
    get the name of top listed anime with get_single_anime_data function
    """

    page = 1
    count = 1

    while page <= max_pages:
        try:
            limit = str((page - 1) * 50)
            url = 'https://myanimelist.net/topanime.php?limit=' + limit
            page_source_code = requests.get(url)
            page_source_code_text = page_source_code.text
            mod_page = BeautifulSoup(page_source_code_text, "html.parser")  # I wonder why...


            for link in mod_page.findAll('a', {'hoverinfo_trigger fl-l fs14 fw-b'}):
                try:
                    href = link.get('href')
                    # href_str = str(href)
                    # title = str(link.string)
                    print(href)
                    anime_name = str(get_single_anime_data(href))
                    print (str(count)+". : "+anime_name)

                except Exception:
                    print(" link get error occur")
                count = count + 1

        except Exception:
            print("url error occur")
        page = page + 1
    print("process done")


crawl_spiderII(1)