#!/bin/bash

status=1
while [ $status -ne 137 ];
do
  wattsup -t /dev/ttyUSB0 watts
  status=$?
  #echo "status: $status"
done

