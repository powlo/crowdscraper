#scraper.py
import sys

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from urllib.parse import urljoin
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from scrapers import crowdcube

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

investments_url = urljoin(CROWDCUBE_URL, INVESTMENTS_PAGE)

page = crowdcube.fetch(investments_url, driver)
crowd_opps = crowdcube.scrape(page)

for opp in crowd_opps:
    opp.save(db)

#Now examine the data in the db to get total raised.
cursor = db.opportunities.aggregate([
    {"$match" : { "days_remaining" : { "$gt" : 10}}},
    {"$group": {"_id": None, "total_raised": {"$sum": "$gbp_raised"}, "count": {"$sum": 1}}}
])

results = cursor.next()

total_raised_str = "£{:,.2f} has been raised on {} opportunities with at least 10 days remaining."

print(total_raised_str.format(results["total_raised"], results["count"]))
