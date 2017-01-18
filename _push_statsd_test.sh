#!/bin/bash

declare -a pid_list

for i in `seq 10`
do
    curl 192.168.100.91 &
    pid_list+="$! "
done

echo "${pid_list[@]}"
wait ${pid_list}
