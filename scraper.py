#scraper.py

#TODO use a parser that will trigger javascript scroll.

import requests
import re
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
    opportunity_id = card.get("data-opportunity-id")
    title = card.get("data-opportunity-name")
    summary = card.select_one("div.cc-card__content > p").string.strip()
    gbp_raised = int(card.get("data-opportunity-raised"))
    percent_raised = int(card.get("data-opportunity-progress"))
    days_string = card.select_one("span.cc-card__daysleft").string.strip()
    days_remaining = int(re.findall("\d+", days_string)[0])
    url = card.select_one("a.cc-card__link").get('href')

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
    {"$group": {"_id": None, "total_raised": {"$sum": "$gbp_raised"}}}
] )

results = cursor.next()

print("Total amount raised on opportunities with at least 10 days remaining:")
print('£{:,.2f}'.format(results["total_raised"]))
