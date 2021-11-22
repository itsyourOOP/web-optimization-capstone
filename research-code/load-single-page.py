#!/usr/bin/python3

import PyChromeDevTools
import time
import sys
import requests

sites = {'amazon': 'http://tucunare.cs.pitt.edu:8080/amazon/www.amazon.com/index.html',
         'bbc': 'http://tucunare.cs.pitt.edu:8080/bbc/www.bbc.co.uk/index.html',
         'cnn': 'http://tucunare.cs.pitt.edu:8080/cnn/www.cnn.com/index.html',
         'craigslist': 'http://tucunare.cs.pitt.edu:8080/craigslist/newyork.craigslist.org/index.html',
         'ebay': 'http://tucunare.cs.pitt.edu:8080/ebay/www.ebay.com/index.html',
         # 'espn':'http://tucunare.cs.pitt.edu:8080/espn/espn.go.com/index.html',
         'google': 'http://tucunare.cs.pitt.edu:8080/google/www.google.com/index.html',
         'msn': 'http://tucunare.cs.pitt.edu:8080/msn/www.msn.com/index.html',
         'slashdot': 'http://tucunare.cs.pitt.edu:8080/slashdot/slashdot.org/index.html',
         'twitter': 'http://tucunare.cs.pitt.edu:8080/twitter/twitter.com/index.html',
         'youtube': 'http://tucunare.cs.pitt.edu:8080/youtube/www.youtube.com/watch07c3.html'
         }

try:
    page = str(sys.argv[1])
    print("Got page!")
except:
    print("Need page as paramater")
    sys.exit(1)

# check if web server is up and running
try:
    print("Time to check this page once again")
    resp = requests.get('http://tucunare.cs.pitt.edu:8080/')
except:
    print("cannot connect to web server")
    sys.exit(1)

if resp.status_code != 200:
    print("web server is not working")
    sys.exit(1)

chrome = PyChromeDevTools.ChromeInterface()
chrome.Network.enable()
chrome.Page.enable()

try:
    site = sites[page]
except:
    print("page not found")
    sys.exit(1)

# chrome.Page.navigate(url=site)

k = 10

for i in range(k):

    print("Starting navigation on page:", page)

    start_time = time.time() * 1000
    chrome.Page.navigate(url=site)
    chrome.wait_event("Page.loadEventFired", timeout=60)
    end_time = time.time() * 1000

    print("Iter:", i, "Page:", page, "Loading Time (ms):", int(end_time-start_time),
          "Start_time_ms:", int(start_time), "End_time_ms:", int(end_time))

    if i < k-1:
        time.sleep(2)
