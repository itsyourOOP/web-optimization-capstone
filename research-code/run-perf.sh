
pid=`ps ax | grep "type=renderer" | awk '{ print $1; }' | head -1`

# --all-user is not valid; 
perf stat -I 200 --all-user -e instructions,cycles,cache-references,cache-misses,branch-misses,bus-cycles -p $pid -o perf.out

