"""
This file contains a simple script to request the update of the scraper.
It runs on a cron job on a remote server.
"""

__author__ = 'User1'
import requests
import time
import shelve
import datetime

def run():
    headers = {'User-Agent': 'Chrome 41.0.2228.0'}

    try:
        response = requests.get('http://mighty-retreat-74693.herokuapp.com/update_tweets_2016', headers=headers, verify=False)
        response = response.text.split("<br>")[-1]
        print(response)
        time.sleep(300)

    except:
        print("Unable to connect")
        time.sleep(30)


run()