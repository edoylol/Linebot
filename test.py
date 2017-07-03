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





def summonerswar_wiki(cond="default"):

    def get_search_keyword():

        keyword = [' ', 'about', 'are', 'bad', 'build', 'good', 'how', 'hows', 'i', 'idea', 'info', 'infos', 'is',
                   'kato', 'me', 'meg', 'megumi', 'people', 'rating', 'ratings', 's', 'should', 'show', 'shows',
                   'skill', 'skills', 'stat', 'stats', 'summoner', 'summoners', 'summonerswar', 'sw', 'think',
                   'thought', 'to', 'use', 'uses', 'war', 'what', 'whats', 'worth', 'worthed', 'you', 'your'
                   ]

        text = random.choice(text)
        text = OtherUtil.filter_words(text, "sw wiki")
        text = OtherUtil.filter_keywords(text, keyword)


        return text

    def get_page(cond):
        if cond == "default" :
            keyword = get_search_keyword()
            if len(search_keyword) > 1:
                search_keyword = "%20".join(keyword)
            else :
                search_keyword = keyword

            page_url = "https://summonerswar.co/?s=" + search_keyword
            req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
            con = urllib.request.urlopen(req)
            page_source_code_text = con.read()
            mod_page = BeautifulSoup(page_source_code_text, "html.parser")
            links = mod_page.find_all("a", {"class": "layer-link"})
            for link in links:
                link = link.get("href")
                if all(word in link for word in keyword):
                    return link

        elif cond == "postback" :
            found_index = [i for i, x in enumerate(text) if x == '*']
            index_start = found_index[0] + 1
            index_end = found_index[1]
            link = (text[index_start:index_end])
            return link

    def get_name(mod_page):
        name = mod_page.find("h1",{"class":"main-title"})
        return name.text.strip()

    def get_overview(mod_page):
        overview = mod_page.find_all("span",{"class":"detail-content"})
        grade = overview[0].text.strip()
        mons_type = overview[1].text.strip()
        usage = overview[4].text.strip()
        return grade,mons_type,usage

    def get_stats(mod_page,nb):
        table = mod_page.findAll("table")
        stats = []
        maxed_stat = []

        for row in table :
            datas = row.find_all("td")
            for data in datas :
                data = data.text.strip()
                stats.append(data)

        if nb == 5 :
            important_indexs = [(0,19),(5,24),(10,29),(31,43),(32,44),(33,45),(34,46),(35,47)] # nat 5
        elif nb == 4 :
            important_indexs = [(0,27),(7,34),(14,41),(43,55),(44,56),(45,57),(46,58),(47,59)] # nat 4
        elif nb == 3 :
            important_indexs = [(0,35),(9,44),(18,53),(55,67),(56,68),(57,69),(58,70),(59,71)] # nat 3
        elif nb == 2 :
            important_indexs = [(0,43),(11,54),(22,65),(67,79),(68,80),(69,81),(70,82),(71,83)] # nat 2

        for (a,b) in important_indexs :
            stat = (stats[a],stats[b])
            maxed_stat.append(stat)

        return maxed_stat

    def get_rating(mod_page):
        rating_category = mod_page.find_all("div",{"class":"col-md-6 col-xs-6"})
        rating_admin = mod_page.find_all("div",{"class":"ratings-panel editor-rating"})
        rating_users = mod_page.find_all("div",{"class":"ratings-panel user-rating"})
        ratings = [("RATING","page's","users's")]       # WORK ON THIS PART TO GIVE BETTER DIALOGUE


        for i in range(1,len(rating_category)) :
            category = str(rating_category[i].text.strip())
            by_admin = str(rating_admin[i-1].text.strip())
            by_user = str(rating_users[i-1].text.strip())
            rating = (category, by_admin, by_user)
            ratings.append(rating)
        return ratings

    def get_skills(mod_page):
        skills = []

        """ getting the skill desc part """
        skills_data = BeautifulSoup(str(mod_page.find_all("div", {"id": "content-anchor-inner"})),
                                    "html.parser")  # actually get skills and review
        skills_desc = skills_data.find_all("p")
        skill_desc_list = []
        keyword = ["Skill 1:", "Skill 2:", "Skill 3:", "Leader Skill:"]
        for skill in skills_desc:
            skill = skill.text.strip()
            if any(word in skill for word in keyword):
                skill_desc_list.append(skill)

        """ getting the skills up part """
        skills_level = skills_data.find_all("ul")
        skill_upgrade_list = []
        for skill in skills_level:
            skill = skill.text.strip()
            skill_upgrade_list.append(skill)

        """ combining both of them """
        for i in range(0, len(skill_desc_list)):
            skill = (skill_desc_list[i],skill_upgrade_list[i])
            skills.append(skill)

        return skills

    def get_procons(mod_page):
        mod_page = BeautifulSoup(str(mod_page.find_all("div",{"class":"col-wrapper"})), "html.parser")
        arguments = mod_page.find_all("p")
        procons = []
        for argument in arguments :
            argument = argument.text.strip()
            procons.append(argument)
        return procons

    report = []

    if cond == "default":
        page_url = get_page()
    else :
        page_url = get_page("postback")

    req = urllib.request.Request(page_url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    page_source_code_text = con.read()
    mod_page = BeautifulSoup(page_source_code_text, "html.parser")

    name = get_name(mod_page)
    grade, mons_type, usage = get_overview(mod_page)


    if cond == "default":
        title = "Summonerswar Wiki"
        text = name + " " + grade+"\n\n"+Lines.summonerswar_wiki("send button header")
        header_pic = "https://43ch47qsavx2jcvnr30057vk-wpengine.netdna-ssl.com/wp-content/uploads/2015/01/logo-sticky.png"

        buttons_template = ButtonsTemplate(title=title, text=text, thumbnail_image_url=header_pic, actions=[
            PostbackTemplateAction(label='Overview', data=('summoners_war_wiki_overview *'+page_url+'*')),
            PostbackTemplateAction(label='Ratings', data=('summoners_war_wiki_ratings *'+page_url+'*')),
            PostbackTemplateAction(label='Stats', data=('summoners_war_wiki_stats *'+page_url+'*')),
            PostbackTemplateAction(label='Skills', data=('summoners_war_wiki_skills *'+page_url+'*'))

        ])

        template_message = TemplateSendMessage(alt_text=text, template=buttons_template)
        line_bot_api.push_message(address, template_message)

        text = Lines.summonerswar_wiki("ask detailed page")
        buttons_template = ButtonsTemplate(text=text, actions=[
            URITemplateAction(label=Labes.confirmation("yes"), uri=page_url)])

        template_message = TemplateSendMessage(alt_text=text, template=buttons_template)
        line_bot_api.push_message(address, template_message)



    else :

        report.append(name + " " + grade)

        if cond == "overview" :

            procons = get_procons(mod_page)
            pros = procons[0]
            cons = procons[1]

            report.append("It's a %s type monster, which excels in %s" %(mons_type,usage)) # WORK ON THIS PART TO GIVE BETTER DIALOGUE
            report.append("")
            report.append("good points")  # WORK ON THIS PART TO GIVE BETTER DIALOGUE
            report.append(pros)
            report.append("")
            report.append("bad points") # WORK ON THIS PART TO GIVE BETTER DIALOGUE
            report.append(cons)

        elif cond == "show stats" :
            report.append("")
            report.append("Lv 40 awakened base stats : ")  # WORK ON THIS PART TO GIVE BETTER DIALOGUE

            nb = len(grade)
            stats = get_stats(mod_page,nb)
            for (stat_type,stat_value) in stats :
                stat = '{:<10}  {:<4}'.format(stat_type, stat_value)
                report.append(stat)

        elif cond == "show ratings" :
            report.append("")
            ratings = get_rating(mod_page)
            for (categ,adm,users) in ratings :
                rating = '{:<18}  {:<8}  {:<12}'.format(categ, adm, users)
                report.append(rating)

        elif cond == "show skills" :
            report.append("")
            report.append("SKILLS : ") # WORK ON THIS PART TO GIVE BETTER DIALOGUE

            skills = get_skills(mod_page)
            for (desc,skillup) in skills :
                report.append(desc)
                report.append("")
                report.append(skillup)
                report.append("")

        report = "\n".join(report)
        line_bot_api.push_message(address, TextSendMessage(text=report))



