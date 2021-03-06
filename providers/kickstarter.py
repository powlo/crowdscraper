"""Functions for fetching and parsign data from kickstarter"""

import json
import requests

from models import Opportunity

USD_TO_GBP = 0.8

#Fetches page contents from a kickstarter url
def fetch(url, params):
    """function to fetch data from kickstarter"""

    r = requests.get(url, params=params)
    return r.text

#Scrapes opportunities from the given page
def scrape_json(page):
    """function to scrape opportunities from kickstarter json"""

    opportunities = []
    projects = json.loads(page)['projects']
    for project in projects:
        opp = Opportunity(
            opportunity_id=project['id'],
            source="Kickstarter",
            title=project["name"],
            summary=project["blurb"],
            gbp_raised=int(float(project["usd_pledged"])*USD_TO_GBP),
            percent_raised=int(float(project["pledged"]/project["goal"]*100)),
            deadline=int(project["deadline"]),
            url=project["urls"]["web"]["project"]
        )
        opportunities.append(opp)

    return opportunities
