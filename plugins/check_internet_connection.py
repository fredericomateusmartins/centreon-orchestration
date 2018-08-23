#!/usr/bin/python3

from socket import create_connection, gethostbyname
from time import time

# Nagios exit status codes
status = {'ok': 0, 'warning': 1, 'critical': 2}

def Connect(hostname, port=443):

    try:
        host = gethostbyname(hostname)
        create_connection((host, 80), 2)
    except OSError:
        pass
    else:
        return True
    return False

for hostname in ('www.google.com', 'www.gitlab.com'):
    start = time()
    if Connect(hostname):
        print("Connected to '{}' in {:.2f}s".format(hostname, time()-start))
        exit(status['ok'])
else:
    print("Unable to connect to any domain")
    exit(status['critical'])
