#!/usr/bin/env python

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 0.1

# SOAP check for endpoints with curl statement.
# Usage: python check_soap_endpoint.py -t json -u 'Vodafone TV Net Voz/2.2/ANDROID' -H http://localserver:8080/service/location -d '{"sid":"randomstring"}' -c Success

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import path
from subprocess import PIPE, Popen
from textwrap import dedent


class Parsing(object):

    name = path.basename(__file__)
    type = {'xml':'text/xml', 'json':'application/json'}

    def __init__(self):

        parser = ArgumentParser(prog='python {0}'.format(self.name), add_help=False,
            formatter_class=RawDescriptionHelpFormatter, description=dedent('''\
                Nagios SOAP UI Plugin
                ---------------------
                  Python script for
                  SOAP UI endpoint
                  check.
                '''), epilog = dedent('''\
                Check the git repository at https://github.com/fredericomateusmartins/nagios-collection,
                for more information about usage, documentation and bug report.'''))

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-c', '--check-string', metavar='string', type=str, help='Check string', required=True)
        optional.add_argument('-d', '--data', metavar='dict', type=str, help='Post request data', required=True)
        optional.add_argument('-H', '--host', metavar='URL', type=str, help='URL host to check', required=True)
        optional.add_argument('-s', '--soap-action', metavar='header', type=str, help='Soap-action cURL header format', default='')
        optional.add_argument('-t', '--type', metavar='type', type=str, choices=self.type,
            help='Data type. Default: {0}'.format(self.type.keys()[0]), default=self.type.keys()[0])
        optional.add_argument('-u', '--user-agent', metavar='header', type=str, help='User-agent cURL header format', required=True)
        optional.add_argument('-h', '--help', action='help', help='Show this help message')
        optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(self.name, __version__),
            help='Show program version')

        self.args = parser.parse_args()


class SOAP(object):

    def __init__(self, args):

        command = '/usr/bin/curl -s -H \'User-Agent: {0}\' -d \'{1}\' -H \'Content-Type: {2}; charset=utf-8\' -H \'SOAPAction: {3}\' {4}'.format(
            args.user_agent, args.data, Parsing.type[args.type], args.soap_action, args.host)

        try:
            stdout, error = Popen(command, shell=True, stdout=PIPE, stderr=PIPE).communicate()

        except KeyboardInterrupt:
            raise SystemExit

        if args.check_string in stdout and not error:
            print("OK")
            exit(0)

        else:
            print("NOT OK: {0}".format('\n'.join((stdout, error))))
            exit(2)


args = Parsing().args
SOAP(args)
