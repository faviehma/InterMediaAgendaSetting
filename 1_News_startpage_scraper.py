import requests
import datetime
import logging
import time

# This is a scraper ment to be running 24/7 on a server

#setup a logger
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('news_scraper.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def scraper():
    logger.info("Started Scraping at"+str(datetime.datetime.now()))

    sources = {"Spiegel":"https://www.spiegel.de/", "FAZ":"https://www.faz.net/aktuell/", "Stern":"https://www.stern.de/", "SZ":"https://www.sueddeutsche.de/","tagesschau":"https://www.tagesschau.de/", "Welt":"https://www.welt.de/","Zeit": "https://www.zeit.de/index"}

    for x in sources:
        url = sources[x]
        try:
            http = requests.get(url, timeout=10)
            logger.info(http.status_code)
        except Exception as e:
            logger.info("Could not get request because"+str(e))
            time.sleep(5)
            http = requests.get(url, timeout=1)
            logger.info(http.status_code)
        with open("data//"+str(datetime.datetime.now()).replace(":","-")+"_"+x+".html", 'w', encoding = "utf-8") as file:
            file.write(http.text)
    logger.info("Finished Scraping at"+str(datetime.datetime.now()))



starttime = time.mktime(datetime.datetime(2020,1,27,00,00,0).timetuple())
while True:
    try:
        scraper()

    except Exception as e:
        logger.info("FATAL ERROR COULDNT RUN SCRIPT AT"+str(datetime.datetime.now()))
        logger.info(str(e))

    time.sleep(3600.0 - ((time.time() - starttime) % 3600.0))
