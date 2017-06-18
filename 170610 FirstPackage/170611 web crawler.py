import Storage, random, urllib.request, string
from urllib import request

def download_image(url):
    file_name = filename()+".jpg"  # make full name with extension
    urllib.request.urlretrieve(url, file_name)

def download_image_range(urlhead,start,stop,urltail):
    file_name = filename()  # make full name with extension
    count = 0
    total = stop-start+1
    fail = 0
    for num in range (start, stop+1):
        modifiedurl = urlhead+str(num)+urltail
        file_name_set = file_name + "_" + str(num) + ".jpg"

        #print(modifiedurl)
        #print(file_name_set)

        print("downloading",count+1,"/",(total)) # UI to track progress
        try :
            urllib.request.urlretrieve(modifiedurl, file_name_set)
        except Exception:
            print("File number",num,"encountered error, continue downloading")
            fail = fail + 1
            total = total - 1
            continue
        count = count + 1

        if num is stop :
            print("Download process done",count,"pictures downloaded\n")
            if fail is not 0 :
                print(fail,"picture(s) failed to be downloaded")

def filename(size=26, chars = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    """ function to generate random string """
    return ''.join(random.choice(chars) for _ in range(size))

def download_csv (url):
    response = request.urlopen(url)
    csv = response.read()
    csv_str = str(csv)
    lines = csv_str.split("\\n")

    file_name = r'new.csv'
    fx = open(file_name, 'w')
    for line in lines:
        fx.write(line + "\n")

    fx.close()

