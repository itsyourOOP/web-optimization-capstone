
pid=`ps ax | grep "type=renderer" | awk '{ print $1; }' | head -1`
sudo bpftrace --unsafe ./chrome2.bt $pid


