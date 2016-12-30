#!/usr/bin/env python

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 0.1

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from configparser import ConfigParser, MissingSectionHeaderError
from getpass import getpass
from os import path
from subprocess import PIPE, Popen
from textwrap import dedent


default = dedent('''\
    host_action = add
    host_alias = Host Name
    host_ip = 10.1.20.1
    host_template = templatename
    host_group = hostgroupname
    host_resource = aclresourcename
    host_poller = pollername
    host_snmp_community = 1ft4Ko9uqdt8U
    host_snmp_version = 2c
    hostgroup_action = add
    hostgroup_alias = Hostgroup Name
    hostgroup_service = servicename
    hostgroup_resource = aclresourcename
    service_action = add
    service_alias = Service Name
    service_template = templatename
    resource_action = edit
    poller_action = restart''')

defaultconf = {param.split(' = ')[0]:param.split(' = ')[1] for param in default.split('\n')}


class Parsing(object):

    name = path.basename(__file__)
    objects = {'host':[], 'hostgroup':[], 'service':[], 'resource':[], 'poller':[]}

    def __init__(self):

        self.Arguments()

        if self.args.generate_ini and (not path.exists(self.args.ini) or input("File {0} exists, overwrite? [y/N] ".format(self.args.ini)) == 'y'):
            self.Generate()

        if self.args.generate_ini:
            raise SystemExit

        self.Configuration()


    def Arguments(self):

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
        optional.add_argument('-u', '--user', metavar='user', type=str, help='Centreon user with administration privileges.',
            default='admin')
        optional.add_argument('-g', '--generate-ini', action='store_true', help='Generate .ini template configuration file.')
        optional.add_argument('-h', '--help', action='help', help='Show this help message')
        optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(self.name, __version__),
            help='Show program version')

        self.args = parser.parse_args()
  

    def Generate(self):

        with open(self.args.ini, 'w') as openini:
            openini.write(dedent('''\
                # Centreon .ini template, for environment orchestration.
                # Clone each object based on it's type.

                #Default program configurations
                [default] 
                {0}

                [hostname]
                type = host
                #action = add # Uses the default 'host_action' if omitted
                #alias = Host Name # Uses the default 'host_alias' if omitted
                #ip = 10.1.20.1 # Uses the default 'host_ip' if omitted
                #template = templatename # Uses the default 'host_template' if omitted
                #group = hostgroupname # Uses the default 'host_group' if omitted
                #resource = aclresourcename
                #poller = mypoller # Uses the default 'host_poller' if omitted
                #snmp_community = 1ft4Ko9uqdt8U
                #snmp_version = 2c

                [hostgroupname]
                type = hostgroup
                #action = add # Uses the default 'hostgroup_action' if omitted
                #alias = Hostgroup Name
                #service = servicename
                #resource = aclresourcename

                [servicename]
                type = service
                #action = add
                #alias = Service Name
                #template = templatename
                #check_command = check-host-alive # check_host_alive = yes

                [aclresourcename]
                type = resource
                #action = edit

                [pollername]
                type = poller
                #action = restart''').format(default))


    def Configuration(self):

        print("Info: Parsing file '{0}'".format(self.args.ini))

        try:
            config = ConfigParser()
            config.read(self.args.ini)

        except MissingSectionHeaderError as e:
            print("Error: {0}".format(e))
            raise SystemExit

        try: # Update default configurations, based on .ini file values
            for key, value in config['default'].items():
                defaultconf[key] = value.split('#')[0].strip()

            del config['default']

        except KeyError: # In case there is no Default section
            pass

        try:
            for each in config.sections():
                self.objects[config[each]['type']].append(config[each])

        except KeyError as e:
            print("Error: Missing {0} in '{1}'".format(e, each)) # "No such type {0}"
            raise SystemExit


class Orchestrate(object):

    group = 'VMWare'
    poller = 'Poller_SAS_OaM'
    resource = 'GSS_SAS-Resources'
    service = 'host-alive'

    def __init__(self, user, objects):

        self.user, self.objects = user, objects

        #self.Authenticate()

        for objtype in ['service', 'hostgroup', 'host', 'resource', 'poller']:
            for obj in self.objects[objtype]:
                name = str(obj).partition(': ')[2][:-1]
                obj = Assert(obj)

                print("Action: {0} {1} '{2}'".format(obj['action'].capitalize(), objtype, name))
                getattr(self, objtype.capitalize())(name, obj)

    def Authenticate(self):

        self.password = getpass()
        stdout, error = Popen('/usr/bin/centreon -u {0} -p {1}'.format(self.user, self.password),
            shell=True, stdout=PIPE, stderr=PIPE).communicate()

        if stdout.strip():
            print("Wrong username or password.")
            self.Authenticate()

    def Service(self, name, service):

        if service['action'] == 'add':
            self.Command('-o STPL -a add -v "{0};{1};{2}"'.format(name, service['alias'], service['template']))
            if 'check_command' in service:
                self.Command('-o STPL -a setparam -v "{0};check_command;{1}"'.format(name, service['check_command']))

        # Create new entries for possible configurations

    def Hostgroup(self, name, hostgroup):

        if hostgroup['action'] == 'add':
            self.Command('-o HG -a add -v "{0};{1}"'.format(name, hostgroup['alias']))
            if 'service' in hostgroup:
                self.Command('-o HGSERVICE -a add -v "{0};{1};{1}"'.format(name, hostgroup['service']))
            if 'resource' in hostgroup:
                self.Command('-o ACLRESOURCE -a grant_hostgroup -v "{0};{1}"'.format(self.resource, self.group))

        # Create new entries for possible configurations

    def Host(self, name, host):

        if host['action'] == 'add':
            self.Command('-o HOST -a ADD -v "{0};{1};{2};{3};{4};{5}"'.format(name, host['alias'], host['ip'], host['template'],
                host['poller'], host['group']))
            self.Command('-o HOST -a setparam -v "{0};snmp_community;1ft4Ko9uqdt8U"'.format(name))
            self.Command('-o HOST -a setparam -v "{0};snmp_version;2c"'.format(name))
            if 'resource' in host:
                self.Command('-o ACLRESOURCE -a grant_host -v "{0};{1}"'.format(host['resource'], name))

        # Create new entries for possible configurations

    def Resource(self, name, resource):

        self.Command('-o ACL -a reload')

        # Create new entries for possible configurations

    def Poller(self, name, poller):

        if poller['action'] == 'restart':
            self.Command('-a APPLYCFG -v "{0}"'.format(self.poller))

        # Create new entries for possible configurations

    def Command(self, command):

        Popen('/usr/bin/centreon -u {0} -p {1} {2}'.format(self.user, self.password, command), shell=True).communicate()


def Assert(object): # Asserts the default values, in case any attribute is not specified
    
    for param in defaultconf:
        try:
            if param.startswith(object['type']):
                type = param.partition('_')[2]
                object[type] = object[type].split('#')[0].strip() # Remove comment from value 

        except KeyError:
            object[type] = defaultconf[param]

    return object


try:
    p = Parsing()
    Orchestrate(p.args.user, p.objects)

except KeyboardInterrupt:
    raise SystemExit
