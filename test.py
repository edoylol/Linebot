import urllib,requests,random,time,os,urllib.request
import json
from bs4 import BeautifulSoup
from gtts import gTTS

class OtherUtil:
    def remove_symbols(word,cond="default"):
        if cond == "default" :
            symbols = "!@#$%^&*()+=-`~[]{]\|;:'/?.>,<\""
        elif cond == "for wiki search" :
            symbols = "!@#$%^&*+=-`~[]{]\|;:/?.>,<\""
        elif cond == "sw wiki":
            symbols = "1234567890!@#$%^&*()_+=-`~[]{]\|';:/?.>,<\""

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

def weather_forcast():
    owm_key_list = [
        "4d7355141b9838b1ac5799247095f61d","48d8f519014923226491c62098640295","32efe2580b5ec0d2767e55a9c2d581d1",
        "79f9585bf82fb571946ce4b0f1101665","30128b74832097ef3ed57c642d56ebe8","eb1b1af47cbca59d0b17c729071d1088",
        "aaae7f35207db74b0bde707b2ff54c81","adcb9836b69d955ec042ffc8d6300feb","a16c1867404a31a617abb68f86ffbedc"
        ]
    open_weather_map_key = random.choice(owm_key_list)

    def get_search_keyword():
        keyword = ['', ' ', '?', 'about', 'afternoon', 'are', 'area', 'around', 'at', 'be', 'city', 'cold', 'cond', 'condition',
                   'do', 'does', 'forecast', 'going', 'gonna', 'have', 'hot', 'how', 'in', 'information', 'is', 'it',
                   'kato', 'kato,', 'like', 'look', 'looks', 'me', 'meg', 'meg,', 'megumi', 'megumi,', 'morning',
                   'near','nearby', 'now', 'please', 'rain', 'said', 'show', 'sky', 'sunny', 'the', 'think', 'this',
                   'to', 'today', 'tomorrow', 'tonight', 'weather', 'weathers', 'what', "what's", 'whats', 'will', 'you']

        filtered_text = OtherUtil.filter_words(text)
        filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

        return filtered_text

    def get_lat_long():
        geo_text = text[text.find("(") + 1: text.find(")")]  # getting the coordinate only
        lat_start = geo_text.find("(") + 1
        lat_end = geo_text.find(",")
        long_start = geo_text.find(",") + 1
        long_end = geo_text.find(")")
        latitude = geo_text[lat_start:lat_end].strip()
        longitude = geo_text[long_start:long_end].strip()
        return latitude,longitude

    def get_city_id(keyword, database="citylist.json"):
        city_id_list = []
        city_name_list = []

        if keyword == []:  # default location is Bandung
            city_id_list.append(1650357)

        else:
            with open(database, encoding='utf8') as city_list:
                data = json.load(city_list)
                found = False
                for city in keyword :
                    for item in data:
                        if city.lower() in item['name'].lower():
                            city_id_list.append(item['id'])
                            city_name_list.append(item['name'])
                            found = True
                        else:
                            pass
                if not (found):
                    city_id_list.append("not_found")

        return city_id_list,city_name_list

    def request_type():

        if "forecast" in text.lower() :
            req_type = "forecast"
        else :
            req_type = "weather"

        return req_type


    text = "meg, show me weather around (12.99,123.42)"

    """ basic flags """
    cont = True
    use_coordinate = False
    use_city_id = False

    """ getting keyword and city id based on text """
    keyword = get_search_keyword()
    city_id_list,city_name_list = get_city_id(keyword)
    city_id = city_id_list[0]
    request_type = request_type()

    # If there is at least one city which id match the keyword given,
    if city_id != "not_found" : use_city_id = True


    # Wrong keyword or the city is not available, thus try to use geo location
    else :
        if all(word in text for word in ['(', ')', ',']): # try to use geo location
            latitude, longitude = get_lat_long()
            try :
                float(latitude)
                float(longitude)
                use_coordinate = True   # flag if coordinate is usable
            except:
                print("lat long not available")
                print("CITY NOT FOUND")
                cont = False
        else :
            print("CITY NOT FOUND")
            cont = False

    """ if either city id or lat long is available """
    if cont :
        owm_call_head = "http://api.openweathermap.org/data/2.5/"+request_type
        owm_call_tail = "&units=metric&appid="+str(open_weather_map_key)

        if use_city_id :
            owm_weather_call = owm_call_head+"?id="+str(city_id)+owm_call_tail
        elif use_coordinate :
            owm_weather_call = owm_call_head+"?lat="+str(latitude)+"&lon="+str(longitude)+owm_call_tail

        weather_data = requests.get(owm_weather_call).json()

        # only get the condition right now ( 1 data each )
        if request_type == "weather" :

            try :
                city_name = weather_data["name"]
            except :
                print("can't get city name (weather)")
                city_name = "Undefined"

            try :
                city_weather_type = weather_data["weather"][0]['main']
                city_weather_description = weather_data["weather"][0]['description']
            except :
                print("can't get weather data (weather)")
                city_weather_type = "Undefined"
                city_weather_description = "Undefined"
            try :
                city_temp = weather_data["main"]['temp']
                city_temp_min = weather_data["main"]['temp_min']
                city_temp_max = weather_data["main"]['temp_max']
            except :
                print("can't get temp data (weather)")
                city_temp = "Undefined"
                city_temp_min = "Undefined"
                city_temp_max = "Undefined"
            try :
                city_pressure = weather_data["main"]['pressure']
                city_humidity = weather_data["main"]['humidity']
            except :
                print("can't get other data (weather)")
                city_pressure = "Undefined"
                city_humidity = "Undefined"

        # get 5 conditions every 3 hours ( data stored as list )
        elif request_type == "forecast" :
            try :
                city_name = weather_data['city']['name']
                city_country = weather_data['city']['country']
            except :
                print("can't get city name (forecast)")
                city_name = "Undefined"
                city_country = " "

            city_weather_type = []
            city_weather_description = []
            city_temp = []
            city_temp_min = []
            city_temp_max = []
            city_pressure = []
            city_humidity = []
            city_date = []

            for i in range(0, 5): # 5 is the max number of carousels allowed by line
                try: city_weather_type.append(weather_data['list'][i]['weather'][0]['main'])
                except:
                    city_date.append(" ")
                try: city_weather_description.append(weather_data['list'][i]['weather'][0]['description'])
                except:
                    city_date.append(" ")
                try: city_temp.append(weather_data['list'][i]['main']['temp'])
                except:
                    city_date.append(" ")
                try: city_temp_min.append(weather_data['list'][i]['main']['temp_min'])
                except:
                    city_date.append(" ")
                try: city_temp_max.append(weather_data['list'][i]['main']['temp_max'])
                except:
                    city_date.append(" ")
                try: city_pressure.append(weather_data['list'][i]['main']['pressure'])
                except:
                    city_date.append(" ")
                try: city_humidity.append(weather_data['list'][i]['main']['humidity'])
                except:
                    city_date.append(" ")
                try: city_date.append(weather_data['list'][i]['dt_txt'])
                except:
                    city_date.append(" ")

        """ displaying result section, move into weather / forecast section later """

        try :
            if len(city_id_list) > 2 :
                print("There are some other cities with similar name, such as :")
                for name in city_name_list :
                    print(name)
                print()
            elif len(city_name_list) == 2 :
                print("There is another city with similar name : ",city_name_list[1])
                print()

            print("city name :",city_name)
            print("current weather :",city_weather_type,"(",city_weather_description,")")
            print("Temperature :",city_temp,"vary from",city_temp_min,"to",city_temp_max,"degree(s) (celcius)")
            print("humidity :",city_humidity,"pressure :",city_pressure)
        except :
            print("failed to show data")

