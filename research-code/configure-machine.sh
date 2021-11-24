#!/bin/bash

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
echo "MACHINE CONFIGURED WITH ${CORES} CORES"
