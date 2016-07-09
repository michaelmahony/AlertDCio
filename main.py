import os

from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from pprint import pprint

import html
import tweepy
import requests
import bs4
import shelve
import time
import datetime
from datetime import timezone, timedelta
import pytz
import BaseConvert

# C:\Users\User1\TweetDC\Scripts\Activate

TWILIO_SID = "AC7df090b4f11ecf908a168fdceb92f852"
TWILIO_SECRET = "5e6c04bca18df9bdda58c9292ae77ee0"

CONSUMER_KEY ="FEuWmFAQ823t84qvzU75si5It"
CONSUMER_SECRET = "dYnFyUvZgJoWZtza8McSvzVUUCFVmUOVqwMRRWIeRDIMI1ZOAN"
ACCESS_KEY = "737332271301201920-fsM0ISlUk9cgwwmvNI0VnP2gAANzY3P"
ACCESS_SECRET = "TF6UuUst6gV02IYQ23oQPiDGecfmoj5Y0ucYXtZ9K39pf"

app = Flask(__name__)

app.secret_key = 'jsfajgpoiahgpioand;lmnspofihwpifha[oksdfjaposihfPIUFHPOIKJfpaoshf'

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://aycfvofyykjlpb:jcKi1FKYzalEXc2kO6xM3e2S4w@ec2-54-235-125-38.compute-1.amazonaws.com:5432/dcnp19lrmuogfm'
db = SQLAlchemy(app)

# Define database modelst
# DB model for flask-security
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')),
                       )


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create a user to test with
# @app.before_first_request
# def create_user():
#     db.create_all()
#     user_datastore.create_user(email='mmahony1@umbc.edu', password='axega137004')
#     db.session.commit()


# DB model for the tweets
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_text = db.Column(db.String(5000))
    short_text = db.Column(db.String(140))
    date_time = db.Column(db.DateTime)
    base62id = db.Column(db.String(10))

    def __init__(self, long_text, short_text):
        self.long_text = long_text
        self.short_text = short_text

        utctime = datetime.datetime.utcnow()
        utctz = pytz.utc
        utctime = utctz.localize(utctime)
        easttz = pytz.timezone('US/Eastern')
        easttime = utctime.astimezone(easttz)


        self.date_time = easttime
        self.base62id = BaseConvert.encode(self.id, "123456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ");

    def __repr__(self):
        return str(self.long_text)


# # Initialize flask-admin
# admin = Admin(app, template_mode='bootstrap3')
# admin.add_view(ModelView(Tweet, db.session))

@app.route("/update_tweets_2016", methods=['GET', 'POST'])
# @login_required
def tweet():

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
        # limit the long entry to 5000 chars
        long_entry = long_entry[0:4999]
        # Has the tweet already been sent?

        short_entry = long_entry[0:115]
        missing = Tweet.query.filter_by(short_text=short_entry).first()
        if missing is not None:
            # Already tweeted, do nothing
            response += "Already tweeted this: " + short_entry +"<br>"

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

                # An unfortunate consequence of the ID generation scheme is that the insertion needs to take place
                #   before we can generate the base62id, and thus before the tweet can be issued.
                #   This makes me uneasy given the risk of the tweet failing.

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





    response += "\n"

    if tweeted:
        response += "Issued tweet"
    else:
        response += "No update "

    return response

@app.route("/", methods=['GET', 'POST'])
def recentTweets():
    query = db.session.query(Tweet).order_by(Tweet.id.desc()).limit(10)
    results_list = [u.__dict__ for u in query.all()]

    return render_template('index.html', tweet_list=results_list)


@app.route("/t/<base62id>")
def tweetView(base62id):
    # Get the tweet
    # the_tweet = db.session.query(Tweet).filter_by(base62id=base62id).first()
    the_tweet = Tweet.query.filter_by(base62id=base62id).first()

    if the_tweet == None:
        # Alert not found, redirect
        flash('Alert not found. Redirecting.') # Doesn't work??
        return redirect('/')

    tweet_detail = {
        'date_time' : the_tweet.date_time,
        'long_text' : the_tweet.long_text,
        'base62id' : the_tweet.base62id,
    }

    print(tweet_detail)

    return render_template('tweet.html', tweet=tweet_detail)








if __name__ == "__main__":
    app.run(debug=False)
