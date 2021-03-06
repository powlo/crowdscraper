"""
Program to scrape investment opportunity
data from investment websites crowdcube and kickstarter
"""
import time

from pymongo import MongoClient

from providers import crowdcube, kickstarter
from utils import days_to_seconds

def main():
    mongo_client = MongoClient(serverSelectionTimeoutMS=2)
    db = mongo_client.crowdscraper

    CROWDCUBE_URL = "https://www.crowdcube.com/investments"
    KICKSTARTER_URL = "http://www.kickstarter.com/discover/advanced"
    KICKSTARTER_PARAMS = {"category_id": 1,
                          "sort":"end_date",
                          "format":"json"}

    page = crowdcube.fetch(CROWDCUBE_URL)
    opportunities = crowdcube.scrape(page)

    kick_opps = []

    #Get 100 funding opportunities from kickstarter
    while len(kick_opps) < 100:
        try:
            KICKSTARTER_PARAMS['page'] = str(int(KICKSTARTER_PARAMS["page"])+1)
        except KeyError:
            KICKSTARTER_PARAMS['page'] = "1"
        old_count = len(kick_opps)
        page = kickstarter.fetch(KICKSTARTER_URL, KICKSTARTER_PARAMS)
        kick_opps.extend(kickstarter.scrape_json(page))

        #If number of opps doesn't change then something went wrong
        if len(kick_opps) == old_count:
            break

    opportunities.extend(kick_opps)

    for opp in opportunities:
        opp.save(db)

    #Now examine the data in the db to get total raised.
    ten_days_from_now = time.time() + days_to_seconds(10)
    cursor = db.opportunities.aggregate([
        {"$match" : {"deadline" : {"$gt" : ten_days_from_now}}},
        {"$group": {"_id": None, "total_raised": {"$sum": "$gbp_raised"}, "count": {"$sum": 1}}}
    ])

    results = cursor.next()

    total_raised_str = "£{:,.2f} has been raised on {} opportunities with at least 10 days remaining."

    print(total_raised_str.format(results["total_raised"], results["count"]))

if __name__ == '__main__':
    main()
