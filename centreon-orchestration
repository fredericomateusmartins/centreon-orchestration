#!/usr/bin/env python

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 0.1

from argparse import ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter
from getpass import getpass
from os import path
from subprocess import PIPE, Popen
from sys import argv
from textwrap import dedent


pool = {
    'host1':'10.1.20.11',
    'host2':'10.1.20.12',
    'host3':'10.1.20.13',
    'host4':'10.1.20.14',
    'host5':'10.1.20.15'
}


class Parsing(object):

    name = path.basename(__file__)

    def __init__(self):

        parser = ArgumentParser(prog='python {0}'.format(self.name), add_help=False,
            formatter_class=RawDescriptionHelpFormatter, description=dedent('''\
                Centreon API Automation
                -----------------------
                  Python script for
                  Centreon task
                  automation.
                '''), epilog = dedent('''\
                Check the git repository at https://github.com/flippym/centreon-orchestration,
                for more information about usage, documentation and bug report.'''))

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-u', '--user', metavar='user', type=str, help='Centreon user with administration privileges.',
            default='admin')
        optional.add_argument('-h', '--help', action='help', help='Show this help message')
        optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(self.name, __version__),
            help='Show program version')

        self.args = parser.parse_args()


class CentreonAPI(object):

    group = 'VMWare'
    poller = 'Poller_SAS_OaM'
    resource = 'GSS_SAS-Resources'
    service = 'host-alive'

    def __init__(self, args):

        self.user = args.user

        self.Authenticate()
        self.CreateService()
        self.CreateGroup()

        for host, ip in pool.items():
            self.CreateHost(host, ip)

        self.RestartPoller()


    def Authenticate(self):

        try:
            self.password = getpass()
            stdout, error = Popen('/usr/bin/centreon -u {0} -p {1}'.format(self.user, self.password),
                shell=True, stdout=PIPE, stderr=PIPE).communicate()

            if stdout.strip():
                print('Wrong username or password.')
                self.Authenticate()

        except KeyboardInterrupt:
            print
            raise SystemExit


    def CreateService(self):

        self.FilterCommand('-o STPL -a add -v "{0};VMWare_Host_Alive;GSS-SAS-Generico"'.format(self.service))
        self.FilterCommand('-o STPL -a setparam -v "{0};check_command;check-host-alive"'.format(self.service))


    def CreateGroup(self):

        print("Creating hostgroup {0} and granting ACL Resource {1} access".format(self.group, self.resource))

        self.FilterCommand('-o HG -a add -v "{0};VMWare Physical Servers"'.format(self.group))
        self.FilterCommand('-o HGSERVICE -a add -v "{0};host-alive;{1}"'.format(self.group, self.service))

        self.FilterCommand('-o ACLRESOURCE -a grant_hostgroup -v "{0};{1}"'.format(self.resource, self.group))


    def CreateHost(self, host, ip):

        print("Creating host {0} and granting ACL Resource {1} access".format(host, self.resource))

        location = 'Alfragide' if host[:4] == 'alfr' else 'Boavista'
        enclosure = host[4:6]
        blade = host[6:8]

        self.FilterCommand('-o HOST -a ADD -v "{0};{1} VMWare Server - Enclosure:{2} Blade:{3};{4};host-gsssas;{5};{6}"'.format(
            host, location, enclosure, blade, ip, self.poller, self.group))
        self.FilterCommand('-o HOST -a setparam -v "{0};snmp_community;1ft4Ko9uqdt8U"'.format(host))
        self.FilterCommand('-o HOST -a setparam -v "{0};snmp_version;2c"'.format(host))

        self.FilterCommand('-o ACLRESOURCE -a grant_host -v "{0};{1}"'.format(self.resource, host))


    def RestartPoller(self):

        print("Restarting poller {0} and reloading ACL configurations".format(self.poller))

        self.FilterCommand('-o ACL -a reload')

        self.FilterCommand('-a APPLYCFG -v "{0}"'.format(self.poller))


    def FilterCommand(self, command):

        Popen('/usr/bin/centreon -u {0} -p {1} {2}'.format(self.user, self.password, command), shell=True).communicate()

p = Parsing()
CentreonAPI(p.args)
