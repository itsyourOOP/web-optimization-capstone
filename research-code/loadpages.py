#!/usr/bin/python3

import PyChromeDevTools
import time
import sys
import requests

sites = ['http://tucunare.cs.pitt.edu:8080/amazon/www.amazon.com/index.html',
	'http://tucunare.cs.pitt.edu:8080/bbc/www.bbc.co.uk/index.html', 
    	'http://tucunare.cs.pitt.edu:8080/cnn/www.cnn.com/index.html', 
        'http://tucunare.cs.pitt.edu:8080/craigslist/newyork.craigslist.org/index.html', 
    	'http://tucunare.cs.pitt.edu:8080/ebay/www.ebay.com/index.html',
        #'http://tucunare.cs.pitt.edu:8080/espn/espn.go.com/index.html',
    	'http://tucunare.cs.pitt.edu:8080/google/www.google.com/index.html',
        'http://tucunare.cs.pitt.edu:8080/msn/www.msn.com/index.html', 
    	'http://tucunare.cs.pitt.edu:8080/slashdot/slashdot.org/index.html', 
        'http://tucunare.cs.pitt.edu:8080/twitter/twitter.com/index.html', 
	'http://tucunare.cs.pitt.edu:8080/youtube/www.youtube.com/watch07c3.html'
]


# check if web server is up and running
try:
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

k = 3

for site in sites*k:

  page = site.split('/')[3]

  start_time=time.time()

  print("Starting navigation on page:", page)
  chrome.Page.navigate(url=site)
  chrome.wait_event("Page.loadEventFired", timeout=60)

  end_time=time.time()

  print("Page:", page, "Loading Time:", end_time-start_time)

  time.sleep(10)

