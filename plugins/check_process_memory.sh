#!/bin/bash

# Checks process memory percentage usage

process=`top -b -c -n 1 | grep -i [s]omeapp` # The [?] is used prevent grep process output

if [[ "$?" -ne 0 ]]; then
    echo "CRITICAL: Proccess not running | megabytes=0"
    exit 2
fi

total_memory=`grep MemTotal /proc/meminfo | awk '{print $2}'`
process_used_memory=`echo $process | awk '{print $10}'`
bytes_used_memory=`python -c "print(round($process_used_memory / 100 * $total_memory / 1024))"`

for parameter in $process; do
    if [[ $parameter == '-Xmx'* ]]; then
        max_memory=`python -c "print('$parameter'[4:-1])"`
        break
    fi
done

limit_memory_check=`bc -l <<< "85/100*$max_memory"`

if [[ `echo $limit_memory_check'<'$bytes_used_memory | bc -l` -ne 0 ]]; then
    echo "CRITICAL: Used memory over 85% of maximum limit | megabytes=$bytes_used_memory"
    exit 2
fi

echo "Memory being used: $bytes_used_memory | megabytes=$bytes_used_memory"
exit 0
