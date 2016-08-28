import os
import bs4
import requests
import html
import tweepy
import time
import datetime
from business_logic import BaseConvert

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

