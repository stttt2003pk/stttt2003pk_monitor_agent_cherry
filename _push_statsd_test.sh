#!/bin/bash
log_file="test.log"

declare -a pid_list

while true;
do
    for i in `seq 10`
        do
            {
                curl -silent 192.168.100.91 > ${log_file};
                curl -silent 192.168.100.92 > ${log_file};
            } &
            pid_list+="$! "
        done

    #echo "${pid_list[@]}"
    wait ${pid_list[@]}

    sleep 5
done
