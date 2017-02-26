import re
import time
import sys

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from bs4 import BeautifulSoup
from models import Opportunity

#Fetches page contents from a crowdcube url
#Uses selenium to allow for ajax content requests
def fetch(url):
    #Abort if driver spinup creates exception
    try:
        driver = webdriver.Chrome()
    except WebDriverException as e:
        print(e.msg)
        sys.exit(1)

    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    page = driver.page_source
    driver.close()
    return page

#Scrapes opportunities from the given page
def scrape(page):
    opportunities = []
    soup = BeautifulSoup(page, 'html.parser')
    cards = soup.select("div#cc-opportunities__listGrid section.cc-card")

    for card in cards:
        days_string = card.select_one("span.cc-card__daysleft").string.strip()
        opp = Opportunity(
            opportunity_id=card.get("data-opportunity-id"),
            source="Crowdcube",
            title=card.get("data-opportunity-name"),
            summary=card.select_one("div.cc-card__content > p").string.strip(),
            gbp_raised=int(card.get("data-opportunity-raised")),
            percent_raised=int(card.get("data-opportunity-progress")),
            days_remaining=int(re.findall(r"\d+", days_string)[0]),
            url=card.select_one("a.cc-card__link").get('href')
        )
        opportunities.append(opp)

    return opportunities
