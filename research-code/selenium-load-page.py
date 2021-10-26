
from pyvirtualdisplay import Display
from selenium import webdriver
import time
from threading import Thread

def load_page(page_url):
  browser.get(page_url)

display = Display(visible=0, size=(800, 600))
display.start()

browser = webdriver.Chrome()

ts1 = time.time()

t = Thread(target=load_page, args=("http://www.google.com",))
t.start()

while True:
  #print("Still loading...")
  if not t.is_alive(): break

ts2 = time.time()

print((ts2-ts1)*1000)

#time.sleep(120)

dom_count = len(browser.find_elements_by_xpath(".//*"))

print("Tittle:", browser.title)
print("dom_count:", dom_count)

browser.quit()

display.stop()


