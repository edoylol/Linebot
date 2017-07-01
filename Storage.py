
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

# Linebot button template
"""
    title = ""
    text = ""
    header_pic = Picture.header("background")

    buttons_template = ButtonsTemplate(title=title, text=text, thumbnail_image_url=header_pic, actions=[
        PostbackTemplateAction(label='Count me in', data='confirmation invitation : yes'),
        PostbackTemplateAction(label='No thanks', data='confirmation invitation : no'),
        PostbackTemplateAction(label='Decide later', data='confirmation invitation : pending')
    ])
    template_message = TemplateSendMessage(alt_text=text, template=buttons_template)
    line_bot_api.push_message(address, template_message)

"""

# Beautiful soup
"""
table = BeautifulSoup(str(mod_page.findAll("div",{"class":"schedule-lists"})),"html.parser")
movies = BeautifulSoup(str(table.findAll("div",{"class" : "schedule-title"})), "html.parser")
"""

# Common check if text contain
""" 

any(word in text for word in [] 

"""


