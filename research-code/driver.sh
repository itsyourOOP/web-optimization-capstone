#!/bin/bash

# for ((i = 1000; i < 4000; i += 200)); do
# 	echo "test $i"
# 	cpupower frequency-set -d $i
# 	cpupower frequency-set -u $i
# done

POSITIONAL=()
while [[ $# -gt 0 ]]; do
	key="$1"

	case $key in
	-c | --cores)
		CORES="$2"
		shift # past argument
		shift # past value
		;;
	-sf | --start-frequency)
		START_FREQ="$2"
		shift # past argument
		shift # past value
		;;
	-ef | --end-frequency)
		END_FREQ="$2"
		shift # past argument
		shift # past value
		;;
	--default)
		DEFAULT=YES
		shift # past argument
		;;
	*)                  # unknown option
		POSITIONAL+=("$1") # save it in an array for later
		shift              # past argument
		;;
	esac
done
echo "NUMBER OF CORES  = ${CORES}"
echo "START FREQ  = ${START_FREQ}"
echo "END FREQ  = ${END_FREQ}"

./configure-machine.sh -c ${CORES} &
./configure-machine.sh -c 91

if [[ -n $1 ]]; then
	echo "Last line of file specified as non-opt/last argument:"
	tail -1 $1
fi
