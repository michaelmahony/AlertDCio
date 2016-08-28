import datetime
import html
import os
import time

import bs4
import requests
import tweepy
from flask import Flask, redirect, render_template, flash
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy

from business_logic import BaseConvert
from business_logic import AlertParser

# C:\Users\User1\TweetDC\Scripts\Activate

CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
ACCESS_KEY = os.environ['TWITTER_ACCESS_KEY']
ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']

app = Flask(__name__)

app.secret_key = os.environ['APP_SECRET']

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
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
        self.date_time = datetime.datetime.now()
        self.base62id = BaseConvert.encode(self.id, "123456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ");

    def __repr__(self):
        return str(self.long_text)


# Initialize flask-admin
# admin = Admin(app, template_mode='bootstrap3')
# admin.add_view(ModelView(Tweet, db.session))

@app.route("/update_tweets_2016", methods=['GET', 'POST'])
# @login_required
def tweet():

    # Get the RSS feed from hsema
    parsed_list = AlertParser.scrape_alerts()

    # tweet_list will be rendered
    tweet_list = []

    for index, long_entry in enumerate(parsed_list):
        tweet_list.append({})

        # limit the long entry to 5000 chars
        long_entry = long_entry[0:4999]
        # Has the tweet already been sent?

        short_entry = long_entry[0:115]
        tweet_list[index]['short_text'] = short_entry


        missing = Tweet.query.filter_by(short_text=short_entry).first()


        if missing is not None:
            # Already tweeted, do nothing
            tweet_list[index]['new_tweet'] = False

        else:
            try:
                tweet_list[index]['new_tweet'] = True

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

                time.sleep(1)
            except:
                pass


    return render_template('update.html', tweet_list=tweet_list)







@app.route("/", methods=['GET', 'POST'])
def recentTweets():
    # Show the most recent ten alerts
    query = db.session.query(Tweet).order_by(Tweet.id.desc()).limit(10)
    results_list = [u.__dict__ for u in query.all()]

    for index, element in enumerate(results_list):
        print(element)
        results_list[index]['long_text'] = results_list[index]['long_text'].split('\n')

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
        # Split the long text at every new line character so that we can use jinja's join | safe method
        'long_text' : the_tweet.long_text.split('\n'),
        'base62id' : the_tweet.base62id,
    }

    print(tweet_detail)

    return render_template('tweet.html', tweet=tweet_detail)








if __name__ == "__main__":
    app.run(debug=False)
