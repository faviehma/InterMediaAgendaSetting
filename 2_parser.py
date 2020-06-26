from bs4 import BeautifulSoup
import os
import datetime
import re
import json
import logging

#This parses all the articles for further analysis.

logger = logging.getLogger('parser')
hdlr = logging.FileHandler('C:\\Users\\fabia\\Documents\\GitHub\\Scraping\\ProcessedData\\final\\logging\\parser.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
logger.info("Start")

os.chdir("C:\\Users\\fabia\\Documents\\GitHub\\Scraping\\ProcessedData\\final\\Data\\raw_data")

publishers = ["spiegel","faz","stern","sz", "tagesschau","welt","zeit"]

def getListOfPages(publisher):
    startPages = []

    for x in os.listdir():
        if publisher in x.lower():
            startPages.append(x)

    return startPages

def defineTimeString(pageString):
    time=None
    time = datetime.datetime.strptime(pageString.split("_")[0],"%Y-%m-%d %H-%M-%S.%f")
    oldtime = time.strftime("%Y-%m-%d /%H")
    time += datetime.timedelta(hours=1)
    time = time.strftime("%Y-%m-%d /%H")
    return time, oldtime

def readOldFile(publisher):
    result={}
    try:
        with open("C:\\Users\\fabia\\Documents\\GitHub\\Scraping\\ProcessedData\\final\\Data\\"+publisher+".json", encoding="utf-8") as file:
            result = json.load(file)
            file.close()
        for time in result:
            if result[time]== None:
                print(time+" "+publisher)
                result.pop("time")

    except Exception as e:
        logger.info("Bei "+publisher+" gab es kein altes File.")
        logger.info(e)
    return result

def testForDataConsistency(link, text, title, pageString, article):
    result = True
    if not isinstance(link,str) or link =="":
        logger.info("Link is not String!! For Article "+ str(article)+" and Page "+ pageString+ " and Link "+ str(link))
        result = False
    if not isinstance(text,str):
        logger.info("Text is not String!! For Article "+ str(article)+" and Page "+ pageString+ " and Text "+ str(text))
        result = False
    if not isinstance(title,str) or title =="":
        logger.info("Title is not String!! For Article "+ str(article)+" and Page "+ pageString+ " and title "+ str(title))
        result= False
    return result

def testDuplicatesAndHoles(time, oldtime, keys, pageString):
    if(time in keys):
        return pageString
    elif(oldtime not in keys):
        logger.info("Hier fehlt eine Zeit: "+pageString)
    return None

def cookSoup(pageString):
    with open(pageString, encoding="utf-8")as file:
        page = file.read()
        file.close()
    soup = BeautifulSoup(page, features="lxml")
    return soup

def getSpiegelStartPage(soup, pageString):
    result={}

    ## Get Articles
    article_visible = soup.find("div", attrs={"class": "OffsetContainer sm:bg-shade-lightest md:bg-shade-lightest"}).findAll("article")
    position =1

    ##Walk over articles
    for a in article_visible:
        title=""
        link=""
        text=""


        if a.get("aria-label").startswith("Anzeige:"):
            continue
        ##GET LINK
        links = a.findAll("a")
        for linkcandidate in links:
            if linkcandidate.get("href").endswith("/"):
                if linkcandidate.get("href").startswith("https://sportdaten.spiegel.de/"):
                    link = linkcandidate.get("href")
                    break
                else:
                    continue
            else:
                link = linkcandidate.get("href")
                break
        if link == "":
            continue

        ## GET TITLE
        try:
            if a.find("header") != None:
                headlineparts = a.find("header").text.strip().split("\n")
            else:
                headlineparts = a.find("h2").text.strip().split("\n")

            validParts = []
            for part in headlineparts:
                if part.strip() == "" or part.startswith("Icon:") or part.startswith("mehr zum Thema") or part.startswith("Eine Kolumne von") \
                or part.startswith("Ein Kommentar von") or part == "Kommentare und Kolumnen" \
                or (headlineparts.index(part)== len(headlineparts)-1 and part.startswith("Von ")):
                    continue
                else:
                    validParts.append(part.strip())

            if validParts == []:
                title = a.find("h2").find("a").get("title")
            else:
                title = " ".join(set(validParts))
        except Exception as e:
            logger.info("Title Fehler bei Datei: "+str(pageString)+" Und bei Artikel: "+str(a.text))
            logger.info(e)
        ## GET TEXT
        try:
            if a.find("section")!= None and a.find("section").find("span") == None:
                text = a.find("section").text
            elif a.find("section")!= None and a.find("section").find("span") != None:
                text = a.find("section").find("span").text
            else:
                pass
        except Exception as e:
            logger.info("Text Fehler bei Datei: "+str(pageString)+" Und bei Artikel: "+str(a.text))
            logger.info(e)

        ## Test for consistency
        if not testForDataConsistency(link,text,title, pageString, a):
            logger.info("Problem bei Artikel "+str(a.text)+" und Datei "+ str(pageString))
            return None
        else:
            currentItem = {"title":title,"text":text,"link":link}
            if position>1 and currentItem == result[position-1]:
                continue
            else:
                result[position]={"title":title,"text":text,"link":link}
                position +=1

    return result

def getFAZStartPage(soup, pageString):
    result ={}

    ## Get Articles
    article = soup.findAll("article")
    position = 1

    ## Walk over articles
    for a in article:
        title = ""
        link =""
        text = ""

        ##pass irrelevant classes
        if "Favorite" in a.parent.get("class")[0] :
            continue
        if "TeaserCompact" in a.parent.get("class")[0] :
            if("Anzeige" in a.parent.parent.parent.parent.parent.parent.parent.find("div").find("span").text):
                continue
            elif("Empfehlung" in a.parent.parent.parent.parent.parent.parent.parent.find("div").find("span").text):
                continue
            else:
                pass
        if(a.parent.get("data-videoid") != None):
            continue
        if "mm-MmBox_MainVideo" in a.get("class"):
            continue
        if "TeaserCompact_ItemInner" in a.parent.get("class")[0]:
            continue


        ## GET TITLE
        for y in a.findAll("a"):
            if y.get("title") != None:
                title = y.get("title")
                break
            else:
                continue

        if title =="" and a.find("span", attrs={"class": "tsr-Base_HeadlineText"}) != None:
            title = a.find("h2", attrs={"class": "tsr-Base_Headline tsr-Base_Headline-md"}).text.replace(":", "").strip()
            link = "no link"
            print(title)


        ## pass title
        if title == "Die aktuelle Ausgabe: Das F.A.Z.-Magazin zum Download":
            continue

        ## GET LINK
        links = a.findAll("a")
        for linkcandidate in links:
            if(linkcandidate.get("href")==None):
                continue
            elif linkcandidate.get("href").endswith("/"):
                link = linkcandidate.get("href")
            else:
                link = linkcandidate.get("href")
                break

        if "Coronavirus stoppt Motorsport" in title and link =="":
            link ="no link"

        ## GET TEXT
        textcorpus = a.find("div",attrs={"class":"tsr-Base_Content"})
        if textcorpus != None:
            text = textcorpus.text.strip()
        else:
            textcorpus = a.find("p",attrs={"class":["tsr-Base_Content"]})
            if textcorpus != None:
                text = textcorpus.text.strip()
            else:
                pass

        ## Test for consistency
        if not testForDataConsistency(link, text, title, pageString, a):
            logger.info("Problem bei Artikel "+a.text+" und Datei "+ pageString)
            return None
        else:
            currentItem = {"title":title,"text":text,"link":link}
            if position>1 and currentItem == result[position-1]:
                continue
            else:
                result[position]={"title":title,"text":text,"link":link}
                position +=1

    return result

def getSternStartPage(soup, pageString):
    result={}
    ## Get Articles
    article = soup.findAll("div", attrs={"class":re.compile(".* o-teaser-article .*")})
    position =1

    ## Walk over articles
    for a in article:
        title=""
        link=""
        text=""

        #pass Ads
        if " ad-" in " ".join(a.get("class")):
            continue
        elif a.get("class") == "o-teaser o-teaser-article o-teaser-standard with_fallback with_ad".split(" "):
            continue
        elif a.find("iframe") != None:
            if a.find("iframe").get("src").startswith("https://liveticker.stern.de/"):
                continue
            elif a.find("iframe").get("src").startswith("https://ticker.stern.de"):
                continue
        elif a.text.strip()=="":
            continue
        badge = a.find("div",attrs={"class":"badge"})
        if(badge != None):
            if "präsentiert" in badge.text:
                continue

        ##GET LINK AND TITLE
        if a.find("a")!= None:
            title = a.find("a").get("title")
            link = a.find("a").get("href")
            if "/gutscheine/" in link:
                continue
            elif link == "https://bit.ly/SternPlayground":
                continue
            elif link.startswith("https://aktion.grunerundjahr.de/"):
                continue
            elif link == "https://www.stern.de/vergleich/":
                continue
            elif link == "/sternstimmen/":
                continue
            elif title == None:
                tmp = a.findAll("h3")
                title = ""
                for x in tmp:
                    title +=x.text.strip()+" "
        else:
            title = a.get("title")
            link = a.get("href")

        if link.startswith("https://www.tag-der-wahrheit.de/"):
            continue

        teasercorpus = a.find("div",attrs={"class":"teaser-copy"})
        if teasercorpus != None:
            text = teasercorpus.text.strip()
        else:
            pass

        ## Test for consistency
        if not testForDataConsistency(link, text, title, pageString, a):
            logger.info("Problem bei Artikel "+a.text+" und Datei "+ pageString)
            return None
        else:
            currentItem = {"title":title,"text":text,"link":link}
            if position>1 and currentItem == result[position-1]:
                continue
            else:
                result[position]={"title":title,"text":text,"link":link}
                position +=1
    return result

def getSZStartPage(soup, pageString):
    result={}

    ## Get Articles
    article = []
    article += soup.findAll("section")[0].findAll("a")
    article += soup.findAll("section")[2].findAll("a")
    position =1

    ## Walk over Articles
    for a in article:
        title=""
        link=""
        text=""

        ##pass some classes or non relevant articles
        if a.get("class")==["newspilot-best-of-module__list-element-link"]:
            continue
        if a.get("class")== ["newsscannermodule__link"]:
            continue
        if a.find("p") == None:
            continue
        elif a.find("p").text == "Leserdiskussion":
            continue

        ## GET LINK
        link = a.get("href")

        if link.startswith("https://www.sueddeutsche.de/gutscheine/"):
            continue
        elif link == "":
            link = "no link"

        ## GET TITLE
        if a.find("h3") == None and a.find("p", attrs={"class": "headline"}) == None and a.find("p", attrs={"class": re.compile(".*title.*")}) != None:
            title = a.find("p", attrs={"class": re.compile(".*title.*")}).text.strip()
        elif a.find("p", attrs={"class": "headline"}) == None and a.find("h3") != None:
            title = a.find("h3").text.strip().replace(" *"," ")
        elif a.find("p", attrs={"class": "headline"}) != None :
            title = a.find("p", attrs={"class": "headline"}).text
        else:
            print(a.text)

        overlinecorpus = a.find("div",attrs={"class":"sz-teaser__overline-title"})
        if overlinecorpus != None:
            title = overlinecorpus.text+" "+title

        onlinecorpus = a.find("p", attrs={"class":"sz-oneliner__title"})
        if onlinecorpus != None:
            title = title+" "+onlinecorpus.text.strip()

        ## GET TEXT
        textcorpus = a.find("p", attrs={"class":"sz-teaser__summary"})
        if textcorpus != None:
            text = textcorpus.text
        elif len(a.findAll("p"))==2:
            text = a.findAll("p")[1].text.strip()
            if text in title:
                text = ""
        ## Test for consistency
        if not testForDataConsistency(link, text, title, pageString, a):
            logger.info("Problem bei Artikel "+a.text+" und Datei "+ pageString)
            return None
        else:
            currentItem = {"title":title,"text":text,"link":link}
            if position>1 and currentItem == result[position-1]:
                continue
            else:
                result[position]={"title":title,"text":text,"link":link}
                position +=1

    return result

def gettagesschauStartPage(soup, pageString):
    result={}
    articlesToSkip = ["Weitere Blog-Beiträge","Weitere Galerien","Alle Videos","Live: tagesschau24", "100 Sekunden", "tagesschau 20 Uhr", "Letzte Sendung", "Wettervorhersage", "Regenradar", "Unwetter", "Das News-Update für Ihren Messenger", "Tagesschau-Nachrichten im Messenger", "Die Tagesschau vor 20 Jahren", "Neues aus dem ARD-Hauptstadtstudio", "Sieben-Tage-Überblick", "Seite auf Facebook", "Seite auf Instagram", "Seite auf Twitter", "Seite auf YouTube", "Podcast abonnieren", "RSS-Feed", "DAX", "Eurostoxx", "Dow Jones", "Nasdaq 100", "Teletext im Internet", "TV und Radio weltweit"]

    ##get all articles
    articles = soup.find("div", attrs={"id":"content"}).findAll("a")

    position = 1
    dachzeile = ""

    ## Walk over articles
    for a in articles:
        title=""
        link=""
        text=""

        ##GET LINK
        link = a.get("href")

        ##Skip some articles
        headlinecorpus = a.find("h4")

        if a.find("div", attrs={"class":"icon playvideo"}) != None:
            continue
        elif a.find("span", attrs={"class":"paarung"}) != None:
            continue
        elif a.text.strip()=="" or a.text.strip() in articlesToSkip:
            continue
        elif headlinecorpus != None and headlinecorpus.text.strip() in articlesToSkip:
            continue
        elif link == None:
            pass
        elif a.get("href").startswith("//wetter.tagesschau.de/"):
            continue
        elif a.get("href")in ["#","#goToHead", "http://www.tagesschau.de/regional/index.html", None]:
            continue
        elif "hiddenInView" in str(a.parent.parent.parent.get("class")):
            continue

        #reset header if article belongs to ressort
        ressortheader = a.parent.parent.parent.parent.find("h3")
        if ressortheader != None and ressortheader.get("class")==["ressort"]:
            dachzeile=""

        ## GET TITLE
        dachzeilencorpus = a.find("p",attrs={"class":"dachzeile"})
        if dachzeilencorpus != None:
            dachzeile = dachzeilencorpus.text.strip()

        if headlinecorpus != None:
            title = dachzeile +" "+ headlinecorpus.text.strip()
        else:
            splittedHeadline = a.text.split("|")
            datePattern = ".*, \d\d\.\d\d\.\d\d\d\d"

            if re.match(datePattern, splittedHeadline[0].strip()):
                title = dachzeile+" "+",".join(splittedHeadline[0].strip().split(",")[:-1]) #get title without date
            else:
                title = dachzeile+" "+splittedHeadline[0].strip()
        title = re.sub("(\n)+"," ",title).strip()

        ## GET TEXT
        textcorpus = a.find("p",attrs={"class":"teasertext"})
        if textcorpus != None:
            text = textcorpus.text
            text = text.split("|")[0].strip()

        ## Test for consistency
        if not testForDataConsistency(link,text,title, pageString, a):
            logger.info("Problem bei Artikel "+a.text+" und Datei "+ pageString)
            return None
        else:
            currentItem = {"title":title,"text":text,"link":link}
            if position>1 and currentItem == result[position-1]:
                continue
            else:
                result[position]={"title":title,"text":text,"link":link}
                position +=1
    return result

def getWeltStartPage(soup, pageString):
    result={}
    articleCategoriesToSkip =["most-read_", "meldungen","livetv", "mediathek", "bilderdestages", "newsticker"]


    ## Get Articles
    articles =soup.findAll("article")
    position = 1

    ## Walk over articles
    for a in articles:
        title=""
        link=""
        text=""

        ## Skip some articles
        childcorpuses = a.findAll("a")

        if len(childcorpuses) == 0:
            continue
        elif a.attrs.get("class")[1]=="c-teaser-oembed":
            continue
        elif a.get("data-document-id") == "207271097":
            continue
        elif childcorpuses[0].get("name") != None:
            if childcorpuses[0].get("name").split("_")[0] in articleCategoriesToSkip:
                continue
        elif len(childcorpuses)>1:
            if childcorpuses[1].get("name") != None:
                if childcorpuses[1].get("name").split("_")[0] in articleCategoriesToSkip:
                    continue
        ## GET Title and Link
        headlinecorpus = a.find("h4")

        if headlinecorpus== None:
            title = ""
            link=""
        else:
            headlineSPAN =headlinecorpus.find("span")
            if headlineSPAN == None:
                title = headlinecorpus.text
                link = headlinecorpus.findAll("a")[1].get("href")
            else:
                headlineSPANText = headlineSPAN.text.strip()
                headlineAs = headlinecorpus.findAll("a")
                if len(headlineAs) > 1:
                    title = (headlinecorpus.find("span").text.strip()+" "+headlinecorpus.findAll("a")[1].text.strip()).strip()
                    link = headlinecorpus.findAll("a")[1].get("href")
                else:
                    title = (headlinecorpus.find("span").text.strip()+" "+headlinecorpus.find("a").text.strip()).strip()
                    link = headlinecorpus.find("a").get("href")

        if link == "" and title == "":
            continue

        ## GET TEXT
        textcorpus = a.find("div", attrs={"data-qa":"Teaser.Intro"})
        if textcorpus != None:
            text = a.find("div", attrs={"data-qa":"Teaser.Intro"}).text.strip()


        ## Test for consistency
        if not testForDataConsistency(link,text,title, pageString, a):
            logger.info("Problem bei Artikel "+a.text+" und Datei "+ pageString)
            return None
        else:
            currentItem = {"title":title,"text":text,"link":link}
            if position>1 and currentItem == result[position-1]:
                continue
            else:
                result[position]={"title":title,"text":text,"link":link}
                position +=1
    return result

def getZeitStartPage(soup, pageString):
    result={}
    articleCategoriesToSkip = ["newsteaser","zon-teaser-printbox__content","teaser-printkiosk","teaser-buzzboard","teaser-buzz", "teaser-shop"]

    ##Get articles
    articles =soup.findAll("article")
    position = 1

    ##Walk over articles
    for a in articles:
        titlelist=[]
        title=""
        link=""
        text=""

        ##Skip some articles
        if a.attrs["class"][0] in articleCategoriesToSkip:
            continue
        elif a.find("span", attrs={"class":"zon-teaser-wide__title"}) != None:
            if a.find("span", attrs={"class":"zon-teaser-wide__title"}).text == "Virologen im täglichen Podcast":
                continue
        elif " ".join(a.attrs["class"]) == "zon-teaser-wide zg-teaser-youtube-wide":
            continue
        elif "".join(a.attrs["class"]).strip().endswith("--ad"):
            continue
        elif str(a.get("data-unique-id")).startswith("http://xml.zeit.de/spiele/"):
            continue

        ## GET TITLE
        headlinecorpus = a.find("h3")
        if headlinecorpus != None:
            titlelist = headlinecorpus.findAll("span")
        else:
            titlelist = a.find("h2").findAll("span")

        if len(titlelist) >2:
            title = titlelist[0].text.strip() +" "+titlelist[2].text.strip()
        elif len(titlelist)>1:
            title = titlelist[0].text.strip() +" "+titlelist[1].text.strip()
        else:
            title = a.find("a").get("title")

        title = title.replace("brand eins","").strip()

        ## GET LINK
        linkcorpus = a.find("a")
        if linkcorpus != None:
            link= linkcorpus.get("href")
        else:
            pass

        textcorpus = a.find("p",attrs={"class":re.compile("zon-teaser-[a-z]*__text")})
        if textcorpus != None:
            text = textcorpus.text.strip()

        ## Test for consistency
        if not testForDataConsistency(link,text,title, pageString, a):
            logger.info("Problem bei Artikel "+a.text+" und Datei "+ pageString)
            continue
        else:
            currentItem = {"title":title,"text":text,"link":link}
            if position>1 and currentItem == result[position-1]:
                continue
            else:
                result[position]={"title":title,"text":text,"link":link}
                position +=1
    return result

def startParsing(publishers):
    publisher2Function = {"spiegel":getSpiegelStartPage,"faz":getFAZStartPage,"stern":getSternStartPage,"sz":getSZStartPage, "tagesschau":gettagesschauStartPage,"welt":getWeltStartPage,"zeit":getZeitStartPage}

    start = datetime.datetime.strptime("2020-02-01/00:00","%Y-%m-%d/%H:%M")
    end = datetime.datetime.strptime("2020-04-01/00:00","%Y-%m-%d/%H:%M")

    for publisher in publishers:
        startPages = getListOfPages(publisher)
        rankings= readOldFile(publisher)
        duplicateTimes = []
        logger.info(publisher+" Parse gestartet. "+ str(len(startPages)-len(rankings))+ "Startseiten zu verarbeiten")

        for pageString in startPages:
            time, oldtime = defineTimeString(pageString)
            if not start<datetime.datetime.strptime(time,"%Y-%m-%d /%H")<end:
                continue

            response = testDuplicatesAndHoles(time, oldtime,rankings.keys(),pageString)
            if response !=None:
                duplicateTimes.append(response)
                continue

            soup = cookSoup(pageString)

            parsedPage=publisher2Function[publisher](soup,pageString)
            if parsedPage != None:
                rankings[time] = parsedPage
            else:
                continue


        logger.info("Diese Dateien sind schon geparsed: "+str(duplicateTimes))

        with open( "C:\\Users\\fabia\\Documents\\GitHub\\Scraping\\ProcessedData\\final\\Data\\"+publisher+".json", "w", encoding="utf-8")as file:
            json.dump(rankings,file)
            file.close()

startParsing(publishers)
