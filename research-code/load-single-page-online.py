#!/usr/bin/python3

import PyChromeDevTools
import time
import sys
import requests

sites = {'amazon': 'http://www.amazon.com/',
         'bbc': 'http://www.bbc.com',
         'cnn': 'http://www.cnn.com/',
         'nytimes': 'http://www.nytimes.com',
         'craigslist': 'http://www.craigslist.com/',
         'ebay': 'http://www.ebay.com',
         'espn': 'http://www.espn.com/',
         'google': 'http://www.google.com/',
         'msn': 'http://www.msn.com/',
         'slashdot': 'http://www.slashdot.org/',
         'twitter': 'http://www.twitter.com/',
         'youtube': 'http://www.youtube.com/'
         }

try:
    page = str(sys.argv[1])
except:
    print("Need page as paramater")
    sys.exit(1)

# check if web server is up and running
# try:
#     # resp = requests.get('http://tucunare.cs.pitt.edu:8080/')
# except:
#     print("cannot connect to web server")
#     sys.exit(1)

if resp.status_code != 200:
    print("web server is not working")
    sys.exit(1)

chrome = PyChromeDevTools.ChromeInterface()
chrome.Network.enable()
chrome.Page.enable()

k = 5

for i in range(k):

    site = 'http://www.'+page+'.com/'

    start_time = time.time()

    print("Starting navigation on site:", site)
    return_value = chrome.Page.navigate(url=site)
    chrome.wait_event("Page.loadEventFired", timeout=60)

    end_time = time.time()
    #print("Return Value:", return_value)
    print("Page:", page, "Loading Time:", end_time-start_time)

    if i < k-1:
        time.sleep(10)
