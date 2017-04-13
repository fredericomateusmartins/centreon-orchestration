# Centreon configuration file parser and API objects

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 1

from collections import OrderedDict
from configparser import ConfigParser, MissingSectionHeaderError
from getpass import getpass
from subprocess import PIPE, Popen
from textwrap import dedent
from time import sleep


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

defaultconf = {}

for param in default.split('\n'):
    defaultconf[param.split(' = ')[0]] = param.split(' = ')[1]


class Configuration(object):

    objects = OrderedDict([('service', []), ('hostgroup', []), ('host', []), ('resource', []), ('poller', [])]) # command

    def __init__(self, inifile):

        self.inifile = inifile

    def Generate(self):

        with open(self.inifile, 'w') as openini:
            openini.write(dedent('''\
                # Centreon .ini template, for environment orchestration.
                # Create a new object by cloning an object based on it's type.
                # Every field is optional, except it's '[name]' and 'type ='. All values will be fetch in the default section.
                # If there's no default section, or it is commented out, the default values are set by the program.

                # Default configurations
                [default] 
                {0}

                [hostname]
                type = host
                #action = add # add, edit, delete
                #alias = Host Name
                #ip = 10.1.20.1
                #template = templatename
                #group = hostgroupname
                #resource = aclresourcename
                #poller = mypoller
                #snmp_community = 1ft4Ko9uqdt8U
                #snmp_version = 2c

                [hostgroupname]
                type = hostgroup
                #action = add
                #alias = Hostgroup Name
                #service = servicename
                #resource = aclresourcename

                [servicename]
                type = service
                #action = add
                #alias = Service Name
                #template = templatename
                #check_command = check-host-alive

                [aclresourcename]
                type = resource
                #action = edit

                [pollername]
                type = poller
                #action = restart # Unique action
            ''').format(default))

    def Apply(self):

        try:
            config = ConfigParser()
            config.read(self.inifile)

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

    def Assert(self, object): # Asserts the default values, in case any attribute is not specified
    
        for param in defaultconf:
            try:
                if param.startswith(object['type']):
                    type = param.partition('_')[2]
                    object[type] = object[type].split('#')[0].strip() # Remove comment from value 

            except KeyError:
                object[type] = defaultconf[param]

        return object


class Orchestrate(object):

    user = 'admin'
    force = False
    password = None

    def __init__(self):

        pass

    def Authenticate(self):

        try:
            self.password = getpass()
            stdout, error = Popen('/usr/bin/centreon -u {0} -p {1}'.format(self.user, self.password),
                shell=True, stdout=PIPE, stderr=PIPE).communicate()

            if stdout.strip():
                sleep(2); print("Wrong username or password.")
                self.Authenticate()

        except KeyboardInterrupt:
            raise SystemExit

    def Service(self, name, service):

        self.status = []

        if service['action'] == 'add':
            self.Execute('-o STPL -a add -v "{0};{1};{2}"'.format(name, service['alias'], service['template']))
            if 'check_command' in service:
                self.Execute('-o STPL -a setparam -v "{0};check_command;{1}"'.format(name, service['check_command']))

        # Create new entries for possible configurations

    def Hostgroup(self, name, hostgroup):

        self.status = []

        if hostgroup['action'] == 'add':
            self.Execute('-o HG -a add -v "{0};{1}"'.format(name, hostgroup['alias']))
            if 'service' in hostgroup:
                for each in hostgroup['service'].split(','):
                    self.Execute('-o HGSERVICE -a add -v "{0};{1};{1}"'.format(name, each))
            if 'resource' in hostgroup:
                self.Execute('-o ACLRESOURCE -a grant_hostgroup -v "{0};{1}"'.format(hostgroup['resource'], name))

        # Create new entries for possible configurations

    def Host(self, name, host):

        self.status = []

        if host['action'] == 'add':
            self.Execute('-o HOST -a ADD -v "{0};{1};{2};{3};{4};{5}"'.format(name, host['alias'], host['ip'], host['template'],
                host['poller'], host['group']))
            self.Execute('-o HOST -a setparam -v "{0};snmp_community;1ft4Ko9uqdt8U"'.format(name))
            self.Execute('-o HOST -a setparam -v "{0};snmp_version;2c"'.format(name))
            if 'resource' in host:
                self.Execute('-o ACLRESOURCE -a grant_host -v "{0};{1}"'.format(host['resource'], name))

        # Create new entries for possible configurations

    def Resource(self, name, resource):

        self.status = []

        self.Execute('-o ACL -a reload')

        # Create new entries for possible configurations

    def Poller(self, name, poller):

        self.status = []
        
        stdout, status = Popen('/usr/bin/centreon -u {0} -p {1} -a POLLERLIST | grep {2}'.format(self.user, self.password, name), 
                               shell=True, stdout=PIPE, stderr=PIPE).communicate()

        if poller['action'] == 'restart':
            self.Execute('-a APPLYCFG -v "{0}"'.format(stdout[0]))

        # Create new entries for possible configurations

    def Execute(self, command):

        stdout, status = Popen('/usr/bin/centreon -u {0} -p {1} {2}'.format(self.user, self.password, command), shell=True, stdout=PIPE, stderr=PIPE).communicate()

        self.status.append([status, stdout.strip()])
