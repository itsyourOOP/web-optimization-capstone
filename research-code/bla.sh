#!/bin/bash

declare -a big_freqs=("0.6Ghz" "0.8Ghz" "1.0Ghz" "1.2GHz" "1.4GHz" "1.6GHz" "1.8GHz" "2.0GHz")

for big_freq in ${big_freqs[@]}; do
  cpufreq-set -c 5 -f $big_freq
  cpufreq-info -c 4-5 
done

