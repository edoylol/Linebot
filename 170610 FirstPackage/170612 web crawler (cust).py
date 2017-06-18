import requests , urllib, urllib.request, Storage
from bs4 import BeautifulSoup


proxies = {
  'https': '94.177.237.165:1189',
}


def download_image(url):
    file_name = Storage.randname() + ".jpg"  # make full name with extension
    try :
        urllib.request.urlretrieve(url, file_name)
        print ("download success")
    except Exception :
        print ("download fail")

def anh18_download(page_url):
    count = 0
    try :
        page_source_code = requests.get(page_url)
        page_source_code_text = page_source_code.text
        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
        #print(mod_page)
        for pic_src in mod_page.findAll('img'):

            try :
                pic_link = pic_src.get('src')
                if "bp.blogspot.com" in pic_link :
                    print (pic_link)
                    try :
                        download_image(pic_link)
                        count = count + 1
                    except Exception:
                        print("Picture download fail >>", pic_link)
                        continue
            except Exception :
                print ("some error occur")
        print("Process done", count, "picture downloaded")
    except Exception :
        print ("failed to parse the page")
def m3dmgame_download(page_url):

    #for i in range(2,max) :
    try :
        page_source_code = requests.get(page_url)
        page_source_code_text = page_source_code.text
        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
        #print(mod_page)
        count = 0
        for pic_src in mod_page.findAll('img'):
            #print(pic_src)
            try :
                pic_link = pic_src.get('src')
                if 'lit.jpg' in pic_link :
                    print(pic_link)
                    download_image(pic_link)

            except Exception :
                print ("some error occur")

    except Exception :
        print ("failed to parse the page")
def DeepBlueSky_download(page_url,start=0):
    try:
        req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        page_source_code_text = con.read()
        #page_source_code = requests.get(page_url)
        #page_source_code_text = page_source_code.text

        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
        #print(mod_page)
        failc = 0
        succ = 0
        for pic_src in mod_page.findAll('img',{'height':'1023'}):
            # print(pic_src)
            try:

                pic_link = pic_src.get('src')
                #print(pic_link)
                file_name = pic_src.get('filename')   # make full name with extension
                if int(file_name[:3]) >= start :  # starting file number
                    try:
                        urllib.request.urlretrieve(pic_link, file_name)
                        print(file_name,"download success")
                        succ = succ + 1
                    except Exception:
                        print("download fail")
                        failc = failc + 1

            except Exception:
                print("some error occur")
    except Exception:
        print("failed to parse the page")
    print("process completed,",succ,"downloaded,",failc,"failed")

def ge_crawl_spider(max_pages,page = 1): # this one crawl main page links

    #fw = open("temp.txt",'w')

    while page <= max_pages :
        url = 'https://e-hentai.org/g/629726/b7496825fd/?p=' + str((page - 1))

        try :
            page_source_code = requests.get(url)
            page_source_code_text = page_source_code.text
            mod_page = BeautifulSoup(page_source_code_text,"html.parser")
            print(mod_page)
            for link in mod_page.findAll('a') :
                try :
                    href = link.get('href')
                    href_str = str(href)
                    if 'https://e-hentai.org/s/' in href_str :
                        print(href_str)
                        get_ge_pic_data(href_str)

                        """
                        try :
                            fw.write(href_str+'\n')
                        except Exception :
                            print("write fail")
                        """

                    else :
                        continue

                except Exception :
                    print ("crawling link error occur")

        except Exception :
            print ("failed to parse the page")
        page = page + 1

    #fw.close()
    print("process done")

def get_ge_pic_data(page_url):
    try :

        page_source_code = requests.get(page_url)
        page_source_code_text = page_source_code.text
        mod_page = BeautifulSoup(page_source_code_text, "html.parser")
        print(mod_page)
        for pic_src in mod_page.findAll('img'):
            #print(pic_src)
            try :
                pic_link = pic_src.get('src')
                if '.jpg' in pic_link :
                    print(pic_link)
                    download_image(pic_link)

            except Exception :
                print ("some error occur")
    except Exception :
        print ("failed to parse the page")



#get_ge_pic_data("https://e-hentai.org/s/795b231de9/629726-282")
#ge_crawl_spider(1)

download_image("https://i.stack.imgur.com/oHpHx.jpg")



""" last update =  able to get pic link, still trying to download pic """

""" Ready to use command : 

anh18_download(page_url)
m3dmgame_download(page_url)
DeepBlueSky_download(page_url,start=0)

"""