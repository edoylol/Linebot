
# getting crawler default template
"""
page_url =
req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
con = urllib.request.urlopen(req)
page_source_code_text = con.read()
mod_page = BeautifulSoup(page_source_code_text, "html.parser")
"""

# Linebot error catch
"""
except LineBotApiError as e:
    print("")
    print(e.status_code)
    print(e.error.message)
    print(e.error.details)
"""

# Linebot confirmation template
"""
ans_yes = Labels.confirmation("yes")
ans_no = Labels.confirmation("no")
command = "\nMegumi dev mode print userlist"
confirm_template = ConfirmTemplate(text=report, actions=[
    MessageTemplateAction(label=ans_yes, text=(ans_yes+command)),
    MessageTemplateAction(label=ans_no, text=ans_no)])
template_message = TemplateSendMessage(alt_text=report, template=confirm_template)
line_bot_api.push_message(jessin_userid, template_message)

"""

# Linebot push template
"""
line_bot_api.push_message(jessin_userid, TextSendMessage(text=report))
"""

# Linebot button template
"""
    title = ""
    button_text = ""
    header_pic = Picture.header("background")

    buttons_template = ButtonsTemplate(title=title, text=button_text, thumbnail_image_url=header_pic, actions=[
        PostbackTemplateAction(label='Count me in', data='confirmation invitation : yes'),
        PostbackTemplateAction(label='No thanks', data='confirmation invitation : no'),
        PostbackTemplateAction(label='Decide later', data='confirmation invitation : pending')
    ])
    template_message = TemplateSendMessage(alt_text=button_text, template=buttons_template)
    line_bot_api.push_message(address, template_message)

"""

# Beautiful soup
"""
table = BeautifulSoup(str(mod_page.findAll("div",{"class":"schedule-lists"})),"html.parser")
movies = BeautifulSoup(str(table.findAll("div",{"class" : "schedule-title"})), "html.parser")
"""

# Common check if text contain
""" 

any(word in text for word in []) 

"""

# Google text to speech
"""
read_text = 'I wonder if where I can use this feature '
language = "en"
filename = "c:\code\linebot\megumi\\nanasaki\\recording.m4a"
tts = gTTS(text=read_text, lang=language)
tts.save(filename)
os.system(filename)
"""

# Code timer
"""
    tic = time.clock()
    # the code that is going to be timed
    toc = time.clock()
    print("Time elapsed:",(toc - tic),"second(s)")
"""

# RegEx
"""
IDENTIFIERS : 
\d any number
\D anything but a number 
\s space
\S anything but a space
\w any character
\W anythin but a character
.  any character, except new line
\b the whitespace around words
\. a period

MODIFIERS:
{1,3} we're expecting 1-3 \d{1-3}
+ Match 1 or more
? Match 0 or 1
* Match 0 or more
$ Match the end of a string
^ Match the beginning of a string
| either or ,,, for example : \d{1-3 | \w{1-3}  (looking for digit with len 1-3 or word with len 1-3)
[] range or "variance" ,,, for example [1-5] means the things to look for is one of '1','2','3','4','5'
{x} expecting 'x' amount

WHITESPACE CHARACTERS:
\n new line
\s space
\t tab
\e escape
\f form feed
\r return

DONT FORGET TO ESCAPE THIS SYMBOL :
. + * ? [ ] $ ^ ( ) { } | \

"""