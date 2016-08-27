import os
import bs4
import requests
import html
import tweepy
import time
import datetime
from business_logic import BaseConvert



CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
ACCESS_KEY = os.environ['TWITTER_ACCESS_KEY']
ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']

def scrape_alerts():
    # Get the feed from hsema
    try:
        headers = {'User-Agent': 'Chrome 41.0.2228.0'}
        response = requests.get(
            'http://trainingtrack.hsema.dc.gov/NRss/RssFeed/AlertDCList?showlink=n&type=iframe&id=912370&hash=36b986985ed3f06443ebb13a0ef1b4ff',
            headers=headers, verify=False)
    except:
        return "Failed during request of rss feed"

    data = response.text

    # Parse the HTML. The results that we want are within a table
    soup = bs4.BeautifulSoup(data, "html5lib")
    entries = soup.findAll("td", {"class": "head"})

    # A list of full alerts
    parsed_list = []

    # For each alert
    for index, entry in enumerate(entries):
        parsed_list.append(entry.text)
        try:
            # The portion of the alert before the first three line breaks does not need to be tweeted.
            # Remove other extraneous white space and the leading 'Alert:'
            parsed_list[index] = "\n".join(parsed_list[index].split("\n")[3:])
            parsed_list[index] = parsed_list[index].strip()
            parsed_list[index] = parsed_list[index].split("Alert:", 1)[-1]
        except:
            pass

    # Because of the way the table is formatted, every other entry will be an empty string.
    # Remove empty elements
    parsed_list = [x for x in parsed_list if x != ""]

    # Unescape HTML
    parsed_list = [html.unescape(x) for x in parsed_list]

    return parsed_list

def tweet_alerts(alert_list):
    tweeted = False

    response = ""

    for index, long_entry in enumerate(alert_list):
        # Limit the long entry to 5000 chars, short entry to 116 chars
        long_entry = long_entry[0:4999]
        short_entry = long_entry[0:115]

        # Check if the tweet has already been issued
        if Tweet.query.filter_by(short_text=short_entry).first() is not None:
            response += ""

        # If not, issue the tweet and add it to the DB
        else:
            try:
                # Add the new tweet to the database
                tweet = Tweet(long_entry, short_entry)
                db.session.add(tweet)

                # Because the ID is not generated until the entry is inserted, we must edit the entry to add
                #   the base62id
                last = db.session.query(Tweet).order_by(Tweet.id.desc()).first()
                base62id = BaseConvert.encode(last.id, "123456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ")
                last.base62id = base62id

                # Save the new database state
                db.session.commit()

                alert_url = " alertdc.io/t/" + base62id
                short_entry += alert_url

                # Send tweet
                auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
                auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
                api = tweepy.API(auth)
                api.update_status(short_entry)
                tweeted = True

                response += "Tweeted: " + short_entry + "<br>"
                time.sleep(1)


            except:
                pass

    return response