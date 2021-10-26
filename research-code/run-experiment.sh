#!/bin/bash

#declare -a sites=("amazon" "bbc" "cnn" "craigslist" "ebay" "espn" "google" "msn" "nytimes" "reddit" "slashdot" "twitter" "youtube")
declare -a sites=("amazon" "bbc" "cnn" "craigslist" "ebay" "google" "msn" "slashdot" "twitter" "youtube")

#declare -a configs=("renderer-little" "renderer-big" "chrome-big" "chrome-little" "chrome-all")
declare -a configs=("renderer-big" "chrome-big" "chrome-little" "chrome-all")

declare -a big_freqs=("0.6Ghz" "0.8Ghz" "1.0Ghz" "1.2GHz" "1.4GHz" "1.6GHz" "1.8GHz" "2.0GHz")
declare -a little_freqs=("0.6Ghz" "0.8Ghz" "1.0Ghz" "1.2GHz" "1.4GHz")

run () {
 echo "Running config '$config' on page '$page' with big freq of '$big_freq' and little freq of '$little_freq'"
 suffix="$config-$page-$big_freq-$little_freq"
 ./move-$config.sh
 ./run-perf.sh &
 ./run-power-monitor.sh > experiment-output/power-$suffix.txt &
 sudo -u rock ./load-single-page.py $page > experiment-output/load-times-$suffix.txt
 sleep 1
 killall -9 perf
 killall -9 wattsup
 sleep 2
 kill -9 `ps ax | grep power-monitor | cut -d" " -f1`
 killall -9 wattsup
 sync
 mv perf.out experiment-output/perf-$suffix.out
 gzip --force experiment-output/perf-$suffix.out
}

if [ "$EUID" -ne 0 ]
  then echo "Please run as sudo/root"
  exit
fi

echo "Starting chrome..."
./run-chrome.sh 1>/dev/null 2>/dev/null &

sleep 10

echo -n " done."

# running baseline -> chrome-all config with scheduil DVFS 
baseline () {
  echo "Setting DVFS governor to schedutil..."
  ./change-governor-schedutil.sh

  for page in ${sites[@]}; do
    config="chrome-all"
    big_freq="schedutil"
    little_freq="schedutil"
    run
  done
}

baseline; sleep 2

exit

echo "Setting DVFS governor to userspace..."
./change-governor-userspace.sh

sleep 1

for page in ${sites[@]}; do
  for config in ${configs[@]}; do
    for big_freq in ${big_freqs[@]}; do
      for little_freq in ${little_freqs[@]}; do
        cpufreq-set -c 5 -f ${big_freq}
        cpufreq-set -c 0 -f ${little_freq}
        run
      done
    done
  done
done

killall chrome
sleep 2
killall -q -9 chrome 

