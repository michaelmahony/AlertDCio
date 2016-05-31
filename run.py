__author__ = 'User1'
import requests
import time

def run():
    headers = {'User-Agent': 'Chrome 41.0.2228.0'}
    finished = False
    while(finished == False):
        response = requests.get('http://mighty-retreat-74693.herokuapp.com/', headers=headers, verify=False)
        print(response.text)
        time.sleep(60)

run()