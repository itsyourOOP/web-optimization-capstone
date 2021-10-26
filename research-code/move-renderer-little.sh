

./move-chrome-little.sh

pid=`ps ax | grep "type=renderer" | awk '{ print $1; }' | head -1`

taskset -a -cp 0-3 $pid

