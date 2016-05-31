__author__ = 'User1'
import requests
import time
import shelve
import datetime

def run():
    headers = {'User-Agent': 'Chrome 41.0.2228.0'}
    finished = False
    while(finished == False):
        response = requests.get('http://mighty-retreat-74693.herokuapp.com/', headers=headers, verify=False)
        print(response.text)
        time.sleep(60)

        file = shelve.open('last_synced')
        file['last_synced'] = str(datetime.datetime.now())
        file.close()


run()