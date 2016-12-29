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
    'alfr0103vmh':'10.2.38.12',
    'alfr0104vmh':'10.2.38.13',
    'alfr0105vmh':'10.2.38.48',
    'alfr0106vmh':'10.2.38.90',
    'alfr0107vmh':'10.2.38.97',
    'alfr0108vmh':'10.2.38.98',
    'alfr0109vmh':'10.2.38.135',
    'alfr0110vmh':'10.2.38.136',
    'alfr0111vmh':'10.2.38.161',
    'alfr0112vmh':'10.2.38.215',
    'alfr0113vmh':'10.2.38.216',
    'alfr0114vmh':'10.2.38.217',
    'alfr0115vmh':'10.2.38.218',
    'alfr0601vmh':'10.2.38.177',
    'alfr0602vmh':'10.2.38.178',
    'alfr0603vmh':'10.2.38.179',
    'alfr0604vmh':'10.2.38.180',
    'alfr0605vmh':'10.2.38.185',
    'alfr0606vmh':'10.2.38.186',
    'alfr0607vmh':'10.2.38.187',
    'alfr0608vmh':'10.2.38.188',
    'alfr0609vmh':'10.2.38.189',
    'alfr0610vmh':'10.2.38.190',
    'alfr0611vmh':'10.2.38.191',
    'alfr0612vmh':'10.2.38.192',
    'alfr0613vmh':'10.2.38.40',
    'alfr0614vmh':'10.2.38.39',
    'alfr0615vmh':'10.2.38.219',
    'alfr1004vmh':'10.2.38.142',
    'alfr1005vmh':'10.2.38.143',
    'alfr1006vmh':'10.2.38.144',
    'alfr1007vmh':'10.2.38.145',
    'alfr1008vmh':'10.2.38.146',
    'alfr1009vmh':'10.2.38.147',
    'alfr1010vmh':'10.2.38.148',
    'alfr1011vmh':'10.2.38.149',
    'alfr1012vmh':'10.2.38.150',
    'alfr1013vmh':'10.2.38.151',
    'alfr1014vmh':'10.2.38.152',
    'alfr1015vmh':'10.2.38.153',
    'alfr1016vmh':'10.2.38.140',
    'alfr1104vmh':'10.2.38.156',
    'alfr1105vmh':'10.2.38.157',
    'alfr1106vmh':'10.2.38.158',
    'alfr1107vmh':'10.2.38.159',
    'alfr1108vmh':'10.2.38.160',
    'alfr1109vmh':'10.2.38.164',
    'alfr1110vmh':'10.2.38.165',
    'alfr1111vmh':'10.2.38.166',
    'alfr1112vmh':'10.2.38.167',
    'alfr1113vmh':'10.2.38.168',
    'alfr1114vmh':'10.2.38.169',
    'alfr1115vmh':'10.2.38.171',
    'alfr1116vmh':'10.2.38.172',
    'boav0301vmh':'10.129.74.49',
    'boav0302vmh':'10.129.74.50',
    'boav0303vmh':'10.129.74.51',
    'boav0304vmh':'10.129.74.52',
    'boav0305vmh':'10.129.74.53',
    'boav0306vmh':'10.129.74.54',
    'boav0307vmh':'10.129.74.55',
    'boav0308vmh':'10.129.74.56',
    'boav0309vmh':'10.129.74.57',
    'boav0310vmh':'10.129.74.58',
    'boav0311vmh':'10.129.74.59',
    'boav0312vmh':'10.129.74.60',
    'boav0313vmh':'10.129.74.61',
    'boav0314vmh':'10.129.74.62',
    'boav0315vmh':'10.129.74.63',
    'boav0316vmh':'10.129.74.64',
    'boav0401vmh':'10.129.74.65',
    'boav0402vmh':'10.129.74.66',
    'boav0403vmh':'10.129.74.67',
    'boav0404vmh':'10.129.74.68',
    'boav0405vmh':'10.129.74.69',
    'boav0406vmh':'10.129.74.70',
    'boav0407vmh':'10.129.74.71',
    'boav0408vmh':'10.129.74.72',
    'boav0409vmh':'10.129.74.73',
    'boav0410vmh':'10.129.74.74',
    'boav0411vmh':'10.129.74.75',
    'boav0412vmh':'10.129.74.76',
    'boav0413vmh':'10.129.74.77',
    'boav0414vmh':'10.129.74.78',
    'boav0415vmh':'10.129.74.79',
    'boav0416vmh':'10.129.74.80',
    'boav0501vmh':'10.129.74.81',
    'boav0502vmh':'10.129.74.82',
    'boav0503vmh':'10.129.74.83',
    'boav0504vmh':'10.129.74.84',
    'boav0505vmh':'10.129.74.85',
    'boav0506vmh':'10.129.74.86',
    'boav0507vmh':'10.129.74.87',
    'boav0508vmh':'10.129.74.88',
    'boav0509vmh':'10.129.74.89',
    'boav0510vmh':'10.129.74.90',
    'boav0511vmh':'10.129.74.91',
    'boav0512vmh':'10.129.74.92',
    'boav0513vmh':'10.129.74.93',
    'boav0514vmh':'10.129.74.94',
    'boav0515vmh':'10.129.74.95',
    'boav0516vmh':'10.129.74.96'
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
