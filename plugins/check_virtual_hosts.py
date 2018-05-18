#!/usr/bin/env python

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 0.1

# Check all configured sites in a webserver and makes a connectivity test. Currently only developed for Apache.

from argparse import ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter
from os import path
from subprocess import PIPE, Popen
from textwrap import dedent


class Parsing(object):

    name = path.basename(__file__)

    def __init__(self):

        parser = ArgumentParser(prog='python {0}'.format(self.name), add_help=False,
            formatter_class=RawDescriptionHelpFormatter, description=dedent('''\
                Nagios Virtual Host Plugin
                --------------------------
                  Python script for
                  HTTPd Virtual 
                  Host check.
                '''), epilog = dedent('''\
                Check the git repository at https://github.com/flippym/nagios-collection,
                for more information about usage, documentation and bug report.'''))

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-u', '--user', metavar='user', type=str, choices=Webserver.userlist,
            help='HTTP server user. Default: {0}'.format(Webserver.userlist[0]), default=Webserver.userlist[0])
        optional.add_argument('-h', '--help', action='help', help='Show this help message')
        optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(self.name, __version__),
            help='Show program version')

        self.args = parser.parse_args()


class Webserver(object):

    hostdict, errors = {}, []
    userlist = ['httpd', 'nginx']

    def __init__(self, user):

        self.user = 'HTTPd' if user == self.userlist[0] else 'NGINX'

        getattr(self, self.user)

        for website in self.hostdict.keys():
            self.ServiceTest(website)

        if not self.errors:
            self.SuccessExit()

        self.ErrorExit('Error in URL: {0}'.format(', '.join(self.errors)))


    def HTTPd(self):

        stdout, error = Popen('httpd -S', shell=True, stdout=PIPE, stderr=PIPE).communicate()

        if error:
            self.ErrorExit(error)

        for output in stdout.split('\n'):
            output = output.strip()

            try:
                port, hosttype, name = output.split(' ')[1:4]
                hostconf, line = output[output.find("(")+1:output.find(")")].split(':')

            except ValueError:
                continue

            if output.startswith('port') and hosttype == 'namevhost':
                with open(hostconf, 'r') as openconf:
                    ending = openconf.read().find('</VirtualHost>')
                    proto = openconf.read().find('SSLEngine on')
                
                protocol = 'https' if ending < proto and proto != -1 else 'http' # Decide between http and https based on conf files
                self.hostdict[name] = '{0}://{1}'.format(protocol, name)


    def NGINX(self):

        pass


    def ServiceTest(self, name):

        try:
            url = self.hostdict[name]
            stdout, error = Popen('curl -fsS {0} >> /dev/null'.format(url), shell=True, stdout=PIPE, stderr=PIPE).communicate()

            if error:
                self.errors.append(name)

        except KeyError:
            del self.hostdict[name]


    def ErrorExit(self, error):

        print("{0} Critical - {1}".format(self.user, error))
        exit(2)


    def SuccessExit(self):

        print("{0} OK - Checked {1} Virtual Hosts".format(self.user, len(self.hostdict)))
        exit(0)


args = Parsing().args
Webserver(args.user)
