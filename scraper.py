#scraper.py

#TODO use a parser that will trigger javascript scroll.

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pymongo import MongoClient

client = MongoClient()
db = client.crowdscraper

CROWDCUBE_URL = 'https://www.crowdcube.com'
INVESTMENTS_PAGE = 'investments'

investments_url =  urljoin(CROWDCUBE_URL, INVESTMENTS_PAGE)

r = requests.get(investments_url)
soup = BeautifulSoup(r.text, 'html.parser')
cards = soup.select("div#cc-opportunities__listGrid section.cc-card")

print("There are {} cards.".format(len(cards)))

for card in cards:
    title = card.find("h3", {"class": "cc-card__heading"}).string.strip()
    summary = card.select_one("div.cc-card__content > p").string.strip()
    gbp_raised = card.find("dt", text="Raised").parent.find("dd").string.strip()
    percent_raised = card.select_one("div.cc-progressBar > span").string.strip()
    days_remaining = card.select_one("span.cc-card__daysleft").string.strip()
    url = card.select_one("a.cc-card__link").get('href')

    db.opportunities.insert_one({
        "title" : title,
        "summary" : summary,
        "gbp_raised" : gbp_raised,
        "percent_raised" : percent_raised,
        "days_remaining" : days_remaining,
        "url" : url
    })
    
    print("+++++++++++++++++++++++")
    print('Title: ', title)
    print('Summary: ', summary)
    print('Raised: ', gbp_raised)
    print('percent_raised: ', percent_raised)
    print('days_remaining: ', days_remaining)
    print('URL: ', url)
    print("-----------------------")
