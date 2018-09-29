#!/usr/bin/bash

status=`snmpwalk -v2c -c $2 $1 'NET-SNMP-EXTEND-MIB::nsExtendResult."selinux_status"' | awk -F: '{print $NF}' | xargs`

if [ "$status" -eq 2 ]; then
    echo "SELinux: OK"
    exit 0
else
    echo "SELinux: NOT OK"
    exit 2
fi
