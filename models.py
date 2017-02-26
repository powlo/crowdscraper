class Opportunity:
    def __init__(self, opportunity_id, source, title, summary, gbp_raised,
                 percent_raised, days_remaining, url):
        self.opportunity_id = opportunity_id
        self.source = source
        self.title = title
        self.summary = summary
        self.gbp_raised = gbp_raised
        self.percent_raised = percent_raised
        self.days_remaining = days_remaining
        self.url = url

    def save(self, db):
        db.opportunities.update_one(
            {
                "oportunity_id" : self.opportunity_id
            },
            {"$set" :
                {
                    "oportunity_id" : self.opportunity_id,
                    "title" : self.title,
                    "summary" : self.summary,
                    "gbp_raised" : self.gbp_raised,
                    "percent_raised" : self.percent_raised,
                    "days_remaining" : self.days_remaining,
                    "url" : self.url
                }
            },
            upsert=True
        )
