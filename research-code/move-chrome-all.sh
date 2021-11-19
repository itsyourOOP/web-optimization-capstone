
pid=`ps ax | grep "chrome --remote" | awk '{ print $1; }' | head -1`

taskset -a -cp 0-5 $pid

# core ranges
#

