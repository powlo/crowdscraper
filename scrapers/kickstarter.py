import json
import requests

from models import Opportunity

#Fetches page contents from a kickstarter url
def fetch(url, params):
    r = requests.get(url, params=params)
    return r.text

#Scrapes opportunities from the given page
def scrape_json(page):
    opportunities = []
    projects = json.loads(page)['projects']
    for project in projects:
        opp = Opportunity(
            opportunity_id=project['id'],
            source="Kickstarter",
            title=project["name"],
            summary=project["blurb"],
            gbp_raised=int(float(project["usd_pledged"])),
            percent_raised=int(float(project["pledged"]/project["goal"]*100)),
            days_remaining=5,
            url=project["urls"]["web"]["project"]
        )
        opportunities.append(opp)

    return opportunities
