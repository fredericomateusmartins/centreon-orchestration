#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Frederico Martins"
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
                Check the git repository at https://github.com/fredericomateusmartins/nagios-collection,
                for more information about usage, documentation and bug report.'''))

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-H', '--host', metavar='host', type=str, help='Physical host for temperature check', required=True)
        optional.add_argument('-s', '--community-string', metavar='str', type=str, help='SNMP community string', required=True)
        optional.add_argument('-c', '--critical', type=int, help='Critical threshold', default=99)
        optional.add_argument('-w', '--warning', type=int, help='Warning threshold', default=80)
        optional.add_argument('-h', '--help', action='help', help='Show this help message')
        optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(self.name, __version__),
            help='Show program version')

        self.args = parser.parse_args()


class Check(object):

    def __init__(self, args):

        output = {'perfdata': '', 'text': [], 'faulty': [], 'status': 0}

        stdout, status = Popen('snmpwalk -v 2c -c {0} {1} lmTempSensorsTable'.format(args.community_string, args.host),
            shell=True, stdout=PIPE, stderr=PIPE).communicate()

        stdout = stdout.split('\n')
        n = len(stdout) / 3

        for device, temperature in zip(stdout[n:n*2], stdout[n*2:]):
             device, temperature = device.split(':')[-1].strip(), int(temperature.split(':')[-1].strip()[:2])
             output['perfdata'] += '"{0}"={1} '.format(device.replace(' ', '_'), temperature)
             output['text'].append('{0}: {1} ºC'.format(device, temperature))

             if temperature >= args.critical:
                 output['status'] = 2
                 output['faulty'].append(device)
             elif temperature >= args.warning:
                 if not output['status']:
                     output['status'] = 1
                 output['faulty'].append(device)

        if output['faulty']:
            print 'Devices: {0} threshold reached | {1}'.format(', '.join(output['faulty']), output['perfdata'])
            exit(output['status'])

        print ', '.join(output['text']), '|', output['perfdata']
        exit(0)

args = Parsing().args
Check(args)
