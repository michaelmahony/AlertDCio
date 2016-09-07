#AlertDC.io
### About

AlertDC was created in response to Washington, DC, Police's announcement
that they would no longer tweet breaking crime alerts, but instead send alerts
by text and email through the DC Alert system. There was quickly
a public outcry in response.

Within 24 hours of the announcement, I created AlertDC to fill the gap.

###Technologies Used
* Python 3.5
* Flask
* PostgreSQL
* Beautiful Soup 4
* TweePy Twitter API Wrapper
* Hosted on Heroku

###Methods
AlertDC contains two main components within one application.
#####Scraper
The scraper monitors a public RSS feed of the official DC Alert system. The page is loaded
periodically and any entries present are checked against a database of alerts that were
already tweeted. If the alert matches a previous alert, a tweet is not issued.

The scraper runs every time a specific page of the Flask application is requested. A Cron job
on a remote Linux server requests this page at regular intervals.

Splitting the Cron job and the application in this way allow the application to have more
reliable uptime while avoiding Heroku's additional monthly fees for Cron jobs.


#####Alert Hosting
The alerts are committed to a database unaltered and unabridged. During the process
of committing each alert to the database, a base 62 identifier is created from the
entry ID. This transformed ID is used as a URL parameter for hosted alerts.

In this way, more than 238,000 alerts can be hosted while limiting the URL parameter length
to three characters or fewer.

Each alert is hosted in its full form with an accompanying time stamp from when it was
collected by the app.


###App Evolution
#####MVP
The application was initially launched in it's MVP state. Crime alerts were tweeted and
(frequently) truncated if they reached more than 140 characters.

#####Hosted Alerts
Tweets are truncated at 117 characters in order to make room for a URL to
alertdc.io/t/{{base_62_id}}. The entire text of the tweet is made available here in a
mobile friendly layout.

#####Future Update
Alerts are issued from the official source with a Police District ID tied to each. Each
district corresponds to a geographic area within Washington, DC. The next step is to allow
alerts on AlertDC.io to be filtered by police district.