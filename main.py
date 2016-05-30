from flask import Flask, request, redirect
import tweepy
import twilio.twiml

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

    resp = twilio.twiml.Response()
    resp.message("Another test")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)

# auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
# auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
#
# api = tweepy.API(auth)
# api.update_status('')