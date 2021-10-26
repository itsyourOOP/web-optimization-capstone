
pid=`ps ax | grep "chrome --remote" | awk '{ print $1; }' | head -1`

taskset -a -cp 4,5 $pid

