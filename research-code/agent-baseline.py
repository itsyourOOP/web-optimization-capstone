
from pyvirtualdisplay import Display
from selenium import webdriver
from threading import Thread
from random import shuffle
from time import sleep, time
from serial import Serial
from sys import exit
import os

class PowerMonitor:
      
  def __init__(self): 
    self._running = True
    self._values = []
  
  def terminate(self): 
    self._running = False

  def read_power(self):
    sd = Serial("/dev/ttyUSB0", 115200, timeout=1)
    sd.flushInput()
    sd.flushOutput()
    resp = str(sd.read(150))
    resp = resp.split('\\r\\n')
    power = float(resp[len(resp)//2].split(',')[2])
    sd.close()
    return power
  
  def save_values(self, filename):
    with open(filename, 'w') as fp:
      fp.write('\n'.join('%s %s' % x for x in self._values))

  def run(self): 
    while self._running: 
        self._values += [(time()*1000, self.read_power())]
        sleep(0.1)


def set_governor(cpu, gov):
  BASEDIR = "/sys/devices/system/cpu"
  fpath = os.path.join(BASEDIR, "cpu%i" % cpu, "cpufreq", "scaling_governor")
  print("Setting CPU " + str(cpu) + " to governor " + gov)
  try:
    open(fpath, "wb").write(gov.encode())
  except:
    print("!! ERROR !! could not write to cpufreq; use sudo")
    exit(1)


pages = {'google':'http://www.google.com/',
         'youtube':'http://www.youtube.com/',
         'amazon':'http://www.amazon.com/',
         'yahoo':'http://www.yahoo.com/',
         'reddit':'http://www.reddit.com',
         'ebay':'http://www.ebay.com',
         'bbc':'http://www.bbc.com', 
         'cnn':'http://www.cnn.com/',
         'nytimes':'http://www.nytimes.com',
         'craigslist':'http://www.craigslist.com/',
         'espn':'http://www.espn.com/',
         'msn':'http://www.msn.com/', 
         'slashdot':'http://www.slashdot.org/', 
      }


# baseline governor
set_governor(0, 'interactive')  # little 
set_governor(4, 'interactive')  # big

display = Display(visible=0, size=(800, 600))
display.start()

REPEAT = 5

load_times = {}

for k in range(REPEAT):

  # randomize pages
  rand_pages = list(pages.keys())
  shuffle(rand_pages)

  for p in rand_pages:

    # start chrome
    browser = webdriver.Chrome()

    # power monitor thread
    pm = PowerMonitor() 
    pm_t = Thread(target=pm.run, args=()) 
    pm_t.start() 

    # navigate to page
    print("Loading page:", pages[p])
    ts1 = time()
    browser.get(pages[p])
    ts2 = time()

    pm.save_values('power-%s-%d.txt' % (p, k))
    pm.terminate()    
    pm_t.join() 

    load_time = (ts2-ts1)*1000
    #print("Inter:", k, "Page:", p, "Load time:", (ts2-ts1)*1000)
    load_times.setdefault(p, []).append(load_time)

    browser.quit()

with open('page-load-times.txt', 'w') as fp:
  fp.write('\n'.join('%s %s' % x for x in load_times.items()))

display.stop()

os.system('killall chromedriver')
os.system('killall Xvfb')
os.system('killall chromium-browser')
