import urllib,requests,random,time,os,urllib.request,io
import json
import unshortenit
import Database
from bs4 import BeautifulSoup
from lines_collection import Lines, Labels, Picture

from datetime import timedelta
from datetime import datetime
from xml.etree import ElementTree

Lines = Lines()

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

class AzureAuthClient(object):
    """
    Provides a client for obtaining an OAuth token from the authentication service
    for Microsoft Translator in Azure Cognitive Services.
    """

    def __init__(self, client_secret):
        """
        :param client_secret: Client secret.
        """

        self.client_secret = client_secret
        # token field is used to store the last token obtained from the token service
        # the cached token is re-used until the time specified in reuse_token_until.
        self.token = None
        self.reuse_token_until = None

    def get_access_token(self):
        '''
        Returns an access token for the specified subscription.
        This method uses a cache to limit the number of requests to the token service.
        A fresh token can be re-used during its lifetime of 10 minutes. After a successful
        request to the token service, this method caches the access token. Subsequent
        invocations of the method return the cached token for the next 5 minutes. After
        5 minutes, a new token is fetched from the token service and the cache is updated.
        '''

        if (self.token is None) or (datetime.utcnow() > self.reuse_token_until):

            token_service_url = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'

            request_headers = {'Ocp-Apim-Subscription-Key': self.client_secret}

            response = requests.post(token_service_url, headers=request_headers)
            response.raise_for_status()

            self.token = response.content
            self.reuse_token_until = datetime.utcnow() + timedelta(minutes=5)

        return self.token

def GetTextTranslation(finalToken,textToTranslate,fromLangCode,toLangCode):

    # Call to Microsoft Translator Service
    headers = {"Authorization ": finalToken}
    translateUrl = "http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&from={}&to={}".format(textToTranslate,fromLangCode, toLangCode)

    translationData = requests.get(translateUrl, headers = headers)
    # parse xml return values
    translation = ElementTree.fromstring(translationData.text.encode('utf-8'))

    # display translation
    return translation.text

def get_text ():
    if "'" in text :
        index_start = text.find("'")+1
        index_stop = text.rfind("'")
        keyword = text[index_start:index_stop]
        return keyword
    return ""

def get_language(cond):
    # remove the text to translate, to minimize errors
    index_start = text.find("'")+1
    index_stop = text.rfind("'")
    crop_text = text.replace(text[index_start:index_stop],'')

    keyword = ['', ' ', '?', 'about', 'are', 'at', 'be', 'do', 'does', 'for', 'gonna', 'have',
               'how', "how's", 'information', 'is', 'it', 'kato', 'kato,', 'like', 'me',
               'meg', 'meg,', 'megumi', 'megumi,', 'now', 'please', 'pls', 'show', 'the', 'think',
               'this', 'what', "what's", 'whats', 'will', 'you']

    filtered_text = OtherUtil.filter_words(crop_text)
    filtered_text = OtherUtil.filter_keywords(filtered_text, keyword)

    if cond == "from" :
        specific_keyword = ['from', 'fr']
    elif cond == "to" :
        specific_keyword = ['in', 'to']

    found = False
    try :
        for i in range(0,len(filtered_text)+1):
            if filtered_text[i] in specific_keyword :
                language = (filtered_text[i + 1])
                found = True
                return language, found
    except :
        pass

    return "",found

def get_available_language():
    page_url = "https://msdn.microsoft.com/en-us/library/hh456380.aspx"
    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    page_source_code_text = con.read()
    mod_page = BeautifulSoup(page_source_code_text, "html.parser")
    code_table = mod_page.find_all("td", {"data-th": "Language Code"})
    name_table = mod_page.find_all("td", {"data-th": "English Name"})

    language_table = {}
    # create dictionary of language available
    for i in range(0, len(code_table)):
        language_code = code_table[i].text.strip()
        language_name = name_table[i].text.strip()
        language_table[language_name] = language_code

    return language_table

def get_language_code (available_language,keyword):

    if keyword != "" :

        for key in available_language: # if the keyword is already in form of code
            if keyword in available_language[key].lower():
                return available_language[key]

        for key in available_language : # else if the keyword is in form of name
            if keyword in key.lower() :
                return available_language[key]

    return ""

cont = True # create continue-flag
result = []
text = "meg, translate 'watch this' to english"
textToTranslate = get_text()

# if the text is not available
if textToTranslate == "":
    cont = False
    result.append(Lines.translate_text("text to translate not found"))

# if text to translate is available
if cont:
    available_language = get_available_language()

    # extract from-to language from the text
    from_lang,is_from_lang_found = get_language("from")
    to_lang,is_to_lang_found = get_language("to")

    # if destination language is found
    if is_to_lang_found:
        from_lang_code = get_language_code(available_language,from_lang)
        to_lang_code = get_language_code(available_language,to_lang)

    # destination language not found
    else:
        cont = False
        result.append(Lines.translate_text("destination language not found"))

# if the destination language is found
if cont:

    # if destination language is available
    if to_lang_code != '':
        azure_keys = ['1c3ea2f61de74a4f8d3bdcbe4cce7316','20039c3da1074c9bba90ebd7600f1381']
        client_secret = random.choice(azure_keys)
        auth_client = AzureAuthClient(client_secret)
        raw_bearer_token = str(auth_client.get_access_token())
        bearer_token = 'Bearer ' + raw_bearer_token[2:-1]
        translated_text = GetTextTranslation(bearer_token,textToTranslate,from_lang_code,to_lang_code)

    # destination language not available
    else:
        cont = False
        result.append(Lines.translate_text("destination language not available") % to_lang)

# if the destination language is available
if cont:
    result.append(Lines.translate_text("send translated").format(textToTranslate,to_lang,translated_text))

report = "\n".join(result)
print(report)