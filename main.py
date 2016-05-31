from flask import Flask, request, redirect
import tweepy
import requests
import bs4
import html5lib
import shelve
import time

TWILIO_SID = "AC7df090b4f11ecf908a168fdceb92f852"
TWILIO_SECRET = "5e6c04bca18df9bdda58c9292ae77ee0"

CONSUMER_KEY ="FEuWmFAQ823t84qvzU75si5It"
CONSUMER_SECRET = "dYnFyUvZgJoWZtza8McSvzVUUCFVmUOVqwMRRWIeRDIMI1ZOAN"
ACCESS_KEY = "737332271301201920-fsM0ISlUk9cgwwmvNI0VnP2gAANzY3P"
ACCESS_SECRET = "TF6UuUst6gV02IYQ23oQPiDGecfmoj5Y0ucYXtZ9K39pf"

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""
    # msg = twilio.twiml.Body()
    # msg = request.values.get('Body', None)


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

    parsed_list = [x[0:139] for x in parsed_list]

    tweeted = False

    for index, element in enumerate(parsed_list):
        file = shelve.open("old_tweets.dat")
        if not 'old_tweets' in file:
            file['old_tweets'] = []

        if element in file['old_tweets']:
            # Already tweeted, do nothing
            print("Already tweeted this: " + element)
        else:
            parsed_list
            try:
                auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
                auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
                api = tweepy.API(auth)
                api.update_status(element)
                tweeted = True

                print("Tweeted: " + element)
                time.sleep(2)
            except:
                pass
            l = file['old_tweets']
            l.append(element)
            file['old_tweets'] = l
        file.close()



    if tweeted:
        return "Updated status"
    else:
        return "No update available"

    resp = twilio.twiml.Response()
    resp.message(msg)
    return str(resp)


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