#!/bin/bash

for ((i = 1000; i < 4000; i += 200)); do
	echo "test $i"
done
# sudo cpupower frequency-set -u 3000mhz
