#scraper.py
import sys
import re
import time

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from urllib.parse import urljoin
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

#Abort if driver spinup creates exception
try:
    driver = webdriver.Chrome()
except WebDriverException as e:
    print(e.msg)
    sys.exit(1)

client = MongoClient(serverSelectionTimeoutMS=2)
db = client.crowdscraper

CROWDCUBE_URL = 'https://www.crowdcube.com'
INVESTMENTS_PAGE = 'investments'

investments_url =  urljoin(CROWDCUBE_URL, INVESTMENTS_PAGE)

driver.get(investments_url)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)
cards = driver.find_elements_by_class_name("cc-card")
html_page = driver.page_source
driver.close()
soup = BeautifulSoup(html_page, 'html.parser')
cards = soup.select("div#cc-opportunities__listGrid section.cc-card")

print("There are {} cards.".format(len(cards)))

for card in cards:
    opportunity_id = card.get("data-opportunity-id")
    title = card.get("data-opportunity-name")
    summary = card.select_one("div.cc-card__content > p").string.strip()
    gbp_raised = int(card.get("data-opportunity-raised"))
    percent_raised = int(card.get("data-opportunity-progress"))
    days_string = card.select_one("span.cc-card__daysleft").string.strip()
    days_remaining = int(re.findall("\d+", days_string)[0])
    url = card.select_one("a.cc-card__link").get('href')

    try:
        db.opportunities.update_one(
        {
            "oportunity_id" : opportunity_id
        },
        {   "$set" :
            {
                "oportunity_id" : opportunity_id,
                "title" : title,
                "summary" : summary,
                "gbp_raised" : gbp_raised,
                "percent_raised" : percent_raised,
                "days_remaining" : days_remaining,
                "url" : url
            }
        },
            upsert=True
        )
    except ServerSelectionTimeoutError as e:
        print(e)
        client.close()
        sys.exit(1)
    print("+++++++++++++++++++++++")
    print('Title: ', title)
    print('Summary: ', summary)
    print('Raised: ', gbp_raised)
    print('percent_raised: ', percent_raised)
    print('days_remaining: ', days_remaining)
    print('URL: ', url)
    print("-----------------------")

cursor = db.opportunities.aggregate([
    {"$match" : { "days_remaining" : { "$gt" : 10}}},
    {"$group": {"_id": None, "total_raised": {"$sum": "$gbp_raised"}, "count": {"$sum": 1}}}
] )

results = cursor.next()

total_raised_str = "£{:,.2f} has been raised on {} opportunities with at least 10 days remaining."

print(total_raised_str.format(results["total_raised"], results["count"]))
