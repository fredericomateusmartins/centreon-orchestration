#!/usr/bin/env python

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 0.1

# Check physical host CPU temperature.

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import path
from subprocess import PIPE, Popen
from sys import exit
from textwrap import dedent


class Parsing(object):
    
    name = path.basename(__file__)

    def __init__(self):
        
        parser = ArgumentParser(prog='python {0}'.format(self.name), add_help=False,
            formatter_class=RawDescriptionHelpFormatter, description=dedent('''\
                Nagios CPU Temperature Plugin
                -----------------------------
                  Python script for CPU
                  temperature
                  check.
                '''), epilog = dedent('''\
                Check the git repository at https://github.com/flippym/nagios-collection,
                for more information about usage, documentation and bug report.'''))

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-H', '--host', metavar='host', type=str, help='Physical host for temperature check', required=True)
        optional.add_argument('-s', '--snmp', metavar='str', type=str, help='SNMP community string', required=True)
        optional.add_argument('-c', '--critical', type=int, help='Critical threshold', default=99)
        optional.add_argument('-w', '--warning', type=int, help='Warning threshold', default=80)
        optional.add_argument('-h', '--help', action='help', help='Show this help message')
        optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(self.name, __version__),
            help='Show program version')

        self.args = parser.parse_args()


class Check(object):
    
    def __init__(self, args):

        stdout, status = Popen('snmpwalk -v 2c -c {0} {1} lmTempSensorsTable'.format(args.community, args.host),
            shell=True, stdout=PIPE, stderr=PIPE).communicate()
          
        stdout = stdout.split('\n')
        n = len(stdout) / 3
        for line in zip(stdout[n:n], stdout[n*2:]): # TODO

        print("LDAP Critical - Could not bind to LDAP server")
        exit(2)


args = Parsing().args
Check(args)    
