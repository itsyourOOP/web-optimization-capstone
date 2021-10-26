
import os
import optparse
import random
import errno
import struct
import sys
sys.path.append('/usr/local/lib/python3.8/dist-packages/perfmon')
import perfmon
import time
import collections
import threading
import signal
import queue
from itertools import combinations, product

running = True
def signal_handler(sig, frame):
    global running 
    print('exiting...')
    running = False
    
signal.signal(signal.SIGINT, signal_handler)

# find renderer PID
pids = os.popen('pidof chrome').read().split()
renderer_pid = None
for p in pids:
    cmdline = open('/proc/%s/cmdline' % (p)).read()
    if 'renderer' in cmdline:
        renderer_pid = int(p)
        break

if not renderer_pid:
  print('renderer PID not found. check if chrome is running.')
  sys.exit(1)

print('renderer_pid:', renderer_pid)

# perf counter queue
queue = queue.Queue(5000)


def perf_counter():

  # pmu events to monitor
  events=("PERF_COUNT_HW_CPU_CYCLES","PERF_COUNT_HW_INSTRUCTIONS","PERF_COUNT_HW_CACHE_REFERENCES", "PERF_COUNT_HW_CACHE_MISSES","PERF_COUNT_HW_BRANCH_MISSES","PERF_COUNT_HW_BUS_CYCLES")

  s = perfmon.PerThreadSession(renderer_pid, events)
  s.start()

  def read_counts():
    # read the counts
    counts = {}
    for i in range(0, len(events)):
      count = struct.unpack("L", s.read(i))[0]
      counts[events[i]] = count
      #print("""%s\t%lu""" % (events[i], count))
    return counts

  counts = read_counts()

  while running:

    time.sleep(0.1)

    prev_counts = counts 
    counts = read_counts()

    # timestamp in ms
    ts_ms = int(time.time() * 1000) 

    event_sample = []
    for e in events:
      #print("""%s\t%lu""" % (e, counts[e] - prev_counts[e]))
      event_sample += [(ts_ms, e, counts[e] - prev_counts[e])]  
    
    queue.put(event_sample)


def agent():

  # CPU sets/masks
  littles = "0123"
  bigs = "45"
  little_masks = [set(map(int, list(combinations(littles, k))[0])) for k in range(1,len(littles)+1)]
  big_masks = [set(map(int, list(combinations(bigs, k))[0])) for k in range(1,len(bigs)+1)]
 
  # tuple (# bigs, # littles)
  configs = list(product((0,1,2), (0,1,2,3,4)))
  configs.remove((0,0))
  
  # freq: int frequency in Hz
  #little_freqs = [408000, 600000, 816000, 1008000, 1200000, 1416000, 1512000]
  #big_freqs = [408000, 600000, 816000, 1008000, 1200000, 1416000, 1608000, 1800000, 2016000]
  little_freqs = [int(i) for i in open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies').read().split(' ')[:-1]]
  big_freqs = [int(i) for i in open('/sys/devices/system/cpu/cpu4/cpufreq/scaling_available_frequencies').read().split(' ')[:-1]]

  def set_freq(cpu, freq):
    BASEDIR = "/sys/devices/system/cpu"
    fpath = os.path.join(BASEDIR, "cpu%i" % cpu, "cpufreq", "scaling_setspeed")
    print("Setting CPU " + str(cpu) + " to frequency (Hz) " + str(freq))
    try:
      open(fpath, "wb").write(str(freq).encode())
    except:
      print("!! ERROR !! could not write to change freq")

  def set_config(num_big, num_little, speed_big, speed_little):
    config_mask = big_masks[num_big-1].union(little_masks[num_little-1])
    os.sched_setaffinity(renderer_pid, config_mask)
    print("Setting CPU affinity mask ("+str(config_mask)+") for pid % s" % renderer_pid)
    # check if success (may skip this!)
    affinity = os.sched_getaffinity(renderer_pid)
    if affinity != config_mask:
        print("Error while setting CPU affinity")

    big_cpu = next(iter(big_masks[num_big-1]))
    little_cpu = next(iter(little_masks[num_little-1]))

    set_freq(big_cpu, speed_big)
    set_freq(little_cpu, speed_little)

  while running:

    # read perf counters from monitor queue
    sample = queue.get()
    queue.task_done()
    print('sample:', sample)

    # select random CPU affinity + frequency
    conf = random.choice(configs)
    rand_big_freq = random.choice(big_freqs)
    rand_little_freq = random.choice(little_freqs)

    # set config (affinity+freq)
    set_config(conf[0], conf[1], rand_big_freq, rand_little_freq)


    time.sleep(1)


    
monitor_thread = threading.Thread(target=perf_counter)
monitor_thread.start()

agent_thread = threading.Thread(target=agent)
agent_thread.start()

monitor_thread.join()
agent_thread.join()




