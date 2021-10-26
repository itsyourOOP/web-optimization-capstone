
import os

# Change the CPU affinity mask 
# of the calling process 
# using os.sched_setaffinity() method 
  
# Below CPU affinity mask will 
# restrict a process to only 
# these 2 CPUs (0, 1) i.e process can 
# run on these CPUs only 
affinity_mask = {0, 1} 
pid = 0
os.sched_setaffinity(0, affinity_mask) 
print("CPU affinity mask is modified for process id % s" % pid) 

# Now again, Get the set of CPUs 
# on which the calling process 
# is eligible to run. 
pid = 0
affinity = os.sched_getaffinity(pid) 

