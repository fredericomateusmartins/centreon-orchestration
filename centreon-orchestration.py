#!/usr/bin/env python

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 0.1

from argparse import ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter
from configparser import ConfigParser
from getpass import getpass
from os import path
from subprocess import PIPE, Popen
from sys import argv
from textwrap import dedent


pool = {
    'alfr0101vmh':'10.2.38.10',
    'alfr0102vmh':'10.2.38.11',
    'alfr0103vmh':'10.2.38.12'
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
        optional.add_argument('-i', '--ini', metavar='file', type=str, help='Specify .ini configuration file.', required=True)
        optional.add_argument('-g', '--generate-ini', action='store_true', help='Generate .ini configuration template file.')
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

    def __init__(self, user):

        self.user = user

        self.Authenticate()
        self.CreateService()
        self.CreateGroup()

        for host, ip in pool.items():
            self.CreateHost(host, ip)

        self.RestartPoller()


    def Authenticate(self):

        self.password = getpass()
        stdout, error = Popen('/usr/bin/centreon -u {0} -p {1}'.format(self.user, self.password),
            shell=True, stdout=PIPE, stderr=PIPE).communicate()

        if stdout.strip():
            print('Wrong username or password.')
            self.Authenticate()


    def CreateService(self):

        self.Command('-o STPL -a add -v "{0};VMWare_Host_Alive;GSS-SAS-Generico"'.format(self.service))
        self.Command('-o STPL -a setparam -v "{0};check_command;check-host-alive"'.format(self.service))


    def CreateGroup(self):

        print("Creating hostgroup {0} and granting ACL Resource {1} access".format(self.group, self.resource))

        self.Command('-o HG -a add -v "{0};VMWare Physical Servers"'.format(self.group))
        self.Command('-o HGSERVICE -a add -v "{0};host-alive;{1}"'.format(self.group, self.service))

        self.Command('-o ACLRESOURCE -a grant_hostgroup -v "{0};{1}"'.format(self.resource, self.group))


    def CreateHost(self, host, ip):

        print("Creating host {0} and granting ACL Resource {1} access".format(host, self.resource))

        location = 'Alfragide' if host[:4] == 'alfr' else 'Boavista'
        enclosure = host[4:6]
        blade = host[6:8]

        self.Command('-o HOST -a ADD -v "{0};{1} VMWare Server - Enclosure:{2} Blade:{3};{4};host-gsssas;{5};{6}"'.format(
            host, location, enclosure, blade, ip, self.poller, self.group))
        self.Command('-o HOST -a setparam -v "{0};snmp_community;1ft4Ko9uqdt8U"'.format(host))
        self.Command('-o HOST -a setparam -v "{0};snmp_version;2c"'.format(host))

        self.Command('-o ACLRESOURCE -a grant_host -v "{0};{1}"'.format(self.resource, host))


    def RestartPoller(self):

        print("Restarting poller {0} and reloading ACL configurations".format(self.poller))

        self.Command('-o ACL -a reload')

        self.Command('-a APPLYCFG -v "{0}"'.format(self.poller))


    def Command(self, command):

        Popen('/usr/bin/centreon -u {0} -p {1} {2}'.format(self.user, self.password, command), shell=True).communicate()


class CentreonINI():

    def __init__(self, filename, generate):

        if generate and (not path.exists(filename) or input("File {0} exists, overwrite? [y/N] ".format(filename)) == 'y'):
            self.Generate(filename)

        if generate:
            raise SystemExit

        self.Parse()


    def Generate(self, filename):

        with open(filename, 'w') as openini:
            openini.write(dedent('''\
                # Centreon .ini template, for environment orchestration.
                # Clone each object based on it's type.

                #Default program configurations
                #[default] 
                #host_action = add # add, edit, delete
                #host_template = templatename
                #host_group = hostgroupname
                #host_resource = aclresourcename
                #host_poller = pollername
                #host_snmp_community = 1ft4Ko9uqdt8U
                #host_snmp_version = 2c
                #hostgroup_action = add
                #hostgroup_resource = aclresourcename
                #service_action = add
                #service_template = templatename
                #resource_action = edit
                #poller_action = restart # restart, reload

                [hostname]
                type = host
                alias = Host Name
                ip = 10.1.20.1
                #action = add # Uses the default 'host_action' if omitted
                #template = templatename # Uses the default 'host_template' if omitted
                #group = hostgroupname # Uses the default 'host_group' if omitted
                #resource = aclresourcename
                #poller = mypoller # Uses the default 'host_poller' if omitted
                #snmp_community = 1ft4Ko9uqdt8U
                #snmp_version = 2c

                [hostgroupname]
                type = hostgroup
                alias = Hostgroup Name
                service = name;template
                #action = add # Uses the default 'hostgroup_action' if omitted
                #resource = aclresourcename

                [servicename]
                type = service
                alias = Service Name
                #action = add
                #template = templatename
                #check_command = check-host-alive # check_host_alive = yes

                [aclresourcename]
                type = resource
                #action = edit

                [pollername]
                type = poller
                #action = restart'''))


    def Parse(self):

        objects = {'host':[], 'hostgroup':[], 'service':[], 'resource':[], 'poller':[]}

        config = ConfigParser()
        config.read('centreon.ini')

        for each in config.sections():
            objects[config[each]['type']].append(each)


try:
    p = Parsing()
    CentreonINI(p.args.ini, p.args.generate_ini)
    CentreonAPI(p.args.user)

except KeyboardInterrupt:
    raise SystemExit
