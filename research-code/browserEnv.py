from pyvirtualdisplay import Display
from selenium import webdriver
from threading import Thread
from random import shuffle, choice
from time import sleep, time
from serial import Serial
from sys import exit
from itertools import combinations, product
import os
import perfmon
import signal
import struct

agent_running = True
def signal_handler(sig, frame):
  global agent_running
  print('exiting...')
  agent_running = False
signal.signal(signal.SIGINT, signal_handler)


class PowerMonitor:

  INTERVAL = 0.15
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

  def last_sample(self):
    if self._values: return self._values[-1]
    return None

  #def last_k_sample(self, k):
  #  return self._values[-k:]

  def dump_values(self, filename):
    with open(filename, 'w') as fp:
      fp.write('\n'.join('%s %s' % x for x in self._values))

  def report_energy(self):
    return sum([v[1] for v in self._values]) / (1.0/self.INTERVAL)

  def run(self):
    while self._running:
      self._values += [(time()*1000, self.read_power())]
      sleep(self.INTERVAL)


class PerfMonitor:

  # pmu events to monitor
  EVENTS=("PERF_COUNT_HW_CPU_CYCLES","PERF_COUNT_HW_INSTRUCTIONS","PERF_COUNT_HW_CACHE_REFERENCES",
          "PERF_COUNT_HW_CACHE_MISSES","PERF_COUNT_HW_BRANCH_MISSES","PERF_COUNT_HW_BUS_CYCLES")
  INTERVAL = 0.15

  def __init__(self, pid):
    self._running = True
    self._values = []
    self._session = perfmon.PerThreadSession(pid, self.EVENTS)
    self._session.start()

  def terminate(self):
    self._running = False

  def _read_counts(self):
    # read the counts
    counts = {}
    for i in range(0, len(self.EVENTS)):
      count = struct.unpack("L", self._session.read(i))[0]
      counts[self.EVENTS[i]] = count
      #print("""%s\t%lu""" % (events[i], count))
    return counts

  def last_sample(self):
    if self._values: return self._values[-1]
    return None

  #def last_k_sample(self, k):
  #  return self._values[-k:]

  def dump_values(self, filename):
    with open(filename, 'w') as fp:
      fp.write('\n'.join('%s %s' % x for x in self._values))

  def run(self):
    counts = self._read_counts()
    while self._running:
      sleep(self.INTERVAL)

      prev_counts = counts
      counts = self._read_counts()

      # timestamp in ms
      ts_ms = int(time() * 1000)

      event_sample = []
      for e in self.EVENTS:
        #print("""%s\t%lu""" % (e, counts[e] - prev_counts[e]))
        event_sample += [(ts_ms, e, counts[e] - prev_counts[e])]

      self._values += [(event_sample)]

class CoreManagement:

  # CPU sets/masks
  LITTLE_IDX = 0
  BIG_IDX = 4
  MAX_LITTLES = 4
  MAX_BIGS = 2
  LITTLES = "0123"
  BIGS = "45"
  BASEDIR = "/sys/devices/system/cpu"

  def __init__(self, pid):
    self._pid = pid
    self._little_masks = [set(map(int, list(combinations(self.LITTLES, k))[0])) for k in range(1,len(self.LITTLES)+1)]
    self._big_masks = [set(map(int, list(combinations(self.BIGS, k))[0])) for k in range(1,len(self.BIGS)+1)]

    # tuple (# bigs, # littles)
    self._mappings = list(product(tuple(range(self.MAX_BIGS+1)), tuple(range(self.MAX_LITTLES+1))))
    self._mappings.remove((0,0)) # not valid config

    # freq: int frequency in Hz
    #little_freqs = [408000, 600000, 816000, 1008000, 1200000, 1416000, 1512000]
    #big_freqs = [408000, 600000, 816000, 1008000, 1200000, 1416000, 1608000, 1800000, 2016000]
    self._little_freqs = [int(i) for i in open('/sys/devices/system/cpu/cpu%d/cpufreq/scaling_available_frequencies' % (self.LITTLE_IDX)).read().split(' ')[:-1]]
    self._big_freqs = [int(i) for i in open('/sys/devices/system/cpu/cpu%d/cpufreq/scaling_available_frequencies' % (self.BIG_IDX)).read().split(' ')[:-1]]

  def get_little_freqs(self):
    return self._little_freqs

  def get_big_freqs(self):
    return self._big_freqs

  def get_mappings(self):
    return self._mappings

  def set_governor(self, cpu, gov):
    fpath = os.path.join(self.BASEDIR, "cpu%i" % cpu, "cpufreq", "scaling_governor")
    try:
      open(fpath, "wb").write(gov.encode())
    except:
      return False
    return True

  def set_little_governor(self, gov):
    return self.set_governor(self.LITTLE_IDX, gov)

  def set_big_governor(self, gov):
    return self.set_governor(self.BIG_IDX, gov)

  def set_freq(self, cpu, freq):
    fpath = os.path.join(self.BASEDIR, "cpu%i" % cpu, "cpufreq", "scaling_setspeed")
    try:
      open(fpath, "wb").write(str(freq).encode())
    except:
      return False
    return True

  def set_big_freq(self, freq):
      return self.set_freq(self.BIG_IDX, freq)

  def set_little_freq(self, freq):
      return self.set_freq(self.LITTLE_IDX, freq)

  def set_affinity(self, pid, cpus):
    pid_list = [int(i) for i in os.popen("pstree -tp %d | grep -oP '\(\K([0-9]+)'" % (pid)).read().split('\n')[:-1]]
    for p in pid_list:
      try:
        os.sched_setaffinity(p, cpus)
      except:
        #print("could not set affinity of process:", p, "to cpus", cpus)
        pass

  def set_config(self, num_big, num_little, speed_big, speed_little):
    mapping_list = self._big_masks[num_big-1].union(self._little_masks[num_little-1])
    self.set_affinity(self._pid, mapping_list)
    #print("Setting CPU affinity mask ("+str(config_mask)+") for pid % s" % renderer_pid)
    # check if success (may skip this!)
    #affinity = os.sched_getaffinity(renderer_pid)
    #if affinity != config_mask:
    #    print("Error while setting CPU affinity")

    big_cpu = next(iter(self._big_masks[num_big-1]))
    little_cpu = next(iter(self._little_masks[num_little-1]))

    self.set_big_freq(speed_big)
    self.set_little_freq(speed_little)

class browserEnv():
    def __init__(self, action_interval):
        self.action_interval = action_interval

        if os.popen("pidof chromium-browser").read():
          print("Another Chromium is running. Please kill it before running the agent.")
          exit(1)

        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

        opt = webdriver.ChromeOptions()
        #opt.add_argument("--headless")
        #opt.add_argument("--disable-xss-auditor")
        #opt.add_argument("--disable-web-security")
        opt.add_argument("--disable-gpu")
        opt.add_argument("--no-sandbox")
        opt.add_argument("--no-zygote")
        opt.add_argument("--window-size=800,600")
        #opt.add_argument("--disable-dev-shm-usage")
        #opt.add_argument("--allow-running-insecure-content")
        #opt.add_argument("--disable-setuid-sandbox")
        #opt.add_argument("--disable-webgl")
        #opt.add_argument("--disable-popup-blocking")

        # start chrome
        self.browser = webdriver.Chrome(options=opt)
        print("Starting Chrome...")
        sleep(5)
        self.browser.get("http://www.cs.pitt.edu")
        sleep(5)
        self.pid = int(os.popen("pidof chromium-browser").read())
        print("Chrome PID:", self.pid)
        #os.system("taskset -a -cp 4-5 " + pid)

        self.pages  = {'google':'http://www.google.com/',
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

        self.perf_mon = PerfMonitor(self.pid)
        self.power_mon = PowerMonitor()
        self.core_man = CoreManagement(self.pid)
        self.core_man.set_little_governor("userspace")
        self.core_man.set_big_governor("userspace")

    def get_possible_actions(self):
        # select action (random CPU affinity + frequency)
        core_mappings = core_man.get_mappings()
        little_freqs = core_man.get_little_freqs()
        big_freqs = core_man.get_big_freqs()

        return core_mappings, little_freqs, big_freqs

    def rollout(self, page_name, agent):

        observations = []
        actions = []
        reward = []

        # perf monitor thread
        perf_t = Thread(target = self.perf_mon.run, args=())
        perf_t.start()

        # power monitor thread
        power_t = Thread(target = self.power_mon.run, args=())
        power_t.start()

        # initial configuration
        cur_config = (2, 4, 1200000, 1200000)
        self.core_man.set_config(cur_config[0], cur_config[1], cur_config[2], cur_config[3])

        def load_page(browser, page_url):
          browser.get(page_url)

        loader_t = Thread(target=load_page, args=(self.browser, self.pages[page_name],))
        loader_t.start()

        start = time()
        while loader_t.is_alive():
          # observation
          perf_sample = perf_mon.last_sample()
          if perf_sample is None:
            sleep(0.1)
            perf_sample = perf_mon.last_sample()
          observations.append((perf_sample, cur_config))

          # perform action
          action = agent.get_action(observations[-1])
          self.core_man.set_config(action[0], action[1], action[2], action[3])
          actions += [action]

          # wait for the effect
          sleep(self.action_interval)

          # immeditate reward
          power_sample = power_mon.last_sample()
          if power_sample is None:
            time(0.1)
            power_sample = power_mon.last_sample()
          reward += [-power_sample[1]]

        end = time()
        loader_t.join()
        
        # final reward
        reward += [(power_mon.report_energy(), (end-start))]

        perf_t.join()
        power_t.join()
        sleep(5)

        return observations, actions, reward


    def close(self):
        perf_mon.terminate()
        power_mon.terminate()

        self.browser.quit()
        self.display.stop()

        sleep(2)

        os.system('killall chromedriver')
        os.system('killall Xvfb')
        os.system('killall chromium-browser')

class randomAgent:
    def __init__(self, action_info):
        self.core_mappings = action_info[0]
        self.big_freqs = action_info[1]
        self.little_freqs = action_info[2]

    def get_action(obs):
        rand_mapping = choice(self.core_mappings)
        rand_big_freq = choice(self.big_freqs)
        rand_little_freq = choice(self.little_freqs)
        return (rand_mapping[0], rand_mapping[1], rand_big_freq, rand_little_freq)


#mock training loop

env = browserEnv(0.2)
agent = randomAgent(env.get_possible_actions)

for page_name in env.pages.keys():
    obs, act, rew = env.gen_rollout(page_name, agent)

env.close()
