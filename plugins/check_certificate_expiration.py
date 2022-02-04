#!/usr/bin/env python

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 0.1

# Certificates expiration check with openssl

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from os import path
from subprocess import PIPE, Popen
from textwrap import dedent


class Parsing(object):

    name = path.basename(__file__)

    def __init__(self):

        parser = ArgumentParser(prog='python {0}'.format(self.name), add_help=False,
            formatter_class=RawDescriptionHelpFormatter, description=dedent('''\
                Nagios Certificate Plugin
                -------------------------
                  Python script for
                  certificate expiration
                  check.
                '''), epilog = dedent('''\
                Check the git repository at https://github.com/fredericomateusmartins/nagios-collection,
                for more information about usage, documentation and bug report.'''))

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-H', '--host', metavar='host', type=str, help='Host certificate to check', required=True)
        optional.add_argument('-p', '--port', metavar='int', type=int, help='Port where service is running', required=True)
        optional.add_argument('-h', '--help', action='help', help='Show this help message')
        optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(self.name, __version__),
            help='Show program version')

        self.args = parser.parse_args()


class Expiration(object):

    def __init__(self, args):

        command = 'date --date="$(echo | openssl s_client -connect {0}:{1} 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f 2)" --iso-8601'.format(
            args.host, args.port)

        try:
            stdout, error = Popen(command, shell=True, stdout=PIPE, stderr=PIPE).communicate()

        except KeyboardInterrupt:
            raise SystemExit

        expire = datetime(*map(int, stdout.split('-'))) - datetime.now()

        if error:
            print("NOT OK: {0}".format(error))
            exit(2)

        elif expire.days >= 60:
            print("OK: Certificate valid for {0} days".format(expire.days))
            exit(0)

        elif expire.days < 60 and expire.days > 0:
            print("WARNING: {0} for certificate {1} to expire".format(expire.days, args.servername))
            exit(1)

        else:
            print("NOT OK: Certificate {0} expired".format(args.servername))
            exit(2)


args = Parsing().args
Expiration(args)
