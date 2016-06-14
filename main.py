import os

from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import html
import tweepy
import requests
import bs4
import shelve
import time
import datetime

# C:\Users\User1\TweetDC\Scripts\Activate

TWILIO_SID = "AC7df090b4f11ecf908a168fdceb92f852"
TWILIO_SECRET = "5e6c04bca18df9bdda58c9292ae77ee0"

CONSUMER_KEY ="FEuWmFAQ823t84qvzU75si5It"
CONSUMER_SECRET = "dYnFyUvZgJoWZtza8McSvzVUUCFVmUOVqwMRRWIeRDIMI1ZOAN"
ACCESS_KEY = "737332271301201920-fsM0ISlUk9cgwwmvNI0VnP2gAANzY3P"
ACCESS_SECRET = "TF6UuUst6gV02IYQ23oQPiDGecfmoj5Y0ucYXtZ9K39pf"

app = Flask(__name__)


# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://aycfvofyykjlpb:jcKi1FKYzalEXc2kO6xM3e2S4w@ec2-54-235-125-38.compute-1.amazonaws.com:5432/dcnp19lrmuogfm'
db = SQLAlchemy(app)

# Define database models
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_text = db.Column(db.String(1000))
    short_text = db.Column(db.String(140))

    def __init__(self, long_text, short_text):
        self.long_text = long_text
        self.short_text = short_text

    def __repr__(self):
        return str(self.long_text)

# Initialize flask-admin
admin = Admin(app, template_mode='bootstrap3')
admin.add_view(ModelView(Tweet, db.session))

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():

    print ('Called')


    try:
        headers = {'User-Agent': 'Chrome 41.0.2228.0'}
        response = requests.get('http://trainingtrack.hsema.dc.gov/NRss/RssFeed/AlertDCList?showlink=n&type=iframe&id=912370&hash=36b986985ed3f06443ebb13a0ef1b4ff', headers=headers, verify=False)
    except:
        return "Failed during request of rss feed"

    data = response.text

    soup = bs4.BeautifulSoup(data, "html5lib")
    entries = soup.findAll("td", {"class": "head"})
    parsed_list = []

    for index, entry in enumerate(entries):
        parsed_list.append(entry.text)
        try:
            parsed_list[index] = "\n".join(parsed_list[index].split("\n")[3:])
            parsed_list[index] = parsed_list[index].strip()
            parsed_list[index] = parsed_list[index].split("Alert:", 1)[-1]
        except:
            pass

    # Remove empty elements
    parsed_list = [x for x in parsed_list if x != ""]

    # Unescape HTML
    parsed_list = [html.unescape(x) for x in parsed_list]

    tweeted = False

    response = ""

    for index, long_entry in enumerate(parsed_list):
        # Has the tweet already been sent?

        short_entry = long_entry[0:139]
        missing = Tweet.query.filter_by(short_text=short_entry).first()
        if missing is not None:
            # Already tweeted, do nothing
            response += "Already tweeted this: " + short_entry +"<br>"

        else:
            try:
                auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
                auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
                api = tweepy.API(auth)
                api.update_status(short_entry)
                tweeted = True

                response += "Tweeted: " + short_entry + "<br>"
                time.sleep(2)
            except:
                pass
            # Add the new tweet to the database
            tweet = Tweet(long_entry, short_entry)
            db.session.add(tweet)

    # Save the new database state
    db.session.commit()


    if tweeted:
        response += "Issued tweet"
    else:
        response += "No update "

    return response





# def scrape():
    # response = requests.get('http://hsema.dc.gov/node/848452')
    #
    # soup = bs4.BeautifulSoup(response.text)
    # msgs = soup.select('table')
    #
    # print(msgs)
    # print("Hello")



if __name__ == "__main__":
    app.run(debug=True)

# auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
# auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
#
# api = tweepy.API(auth)
# api.update_status('')