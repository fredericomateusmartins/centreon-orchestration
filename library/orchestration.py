# Centreon configuration file parser and API objects

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 1

from collections import OrderedDict
from configparser import RawConfigParser, MissingSectionHeaderError
from getpass import getpass
from json import dumps
from requests import get, post
from subprocess import PIPE, Popen
from textwrap import dedent
from time import sleep
from types import MethodType
from warnings import filterwarnings


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
    hostgroup_resource = aclresourcename
    command_action = add
    command_line = $USER1$/check_ping -H $HOSTADDRESS$ -w 3000.0,80% -c 5000.0,100% -p 1
    service_action = add
    service_alias = Service Name
    service_group = hostgroupname
    service_template = templatename
    resource_action = reload
    poller_action = restart''')

defaultconf = {}

for param in default.split('\n'):
    defaultconf[param.split(' = ')[0]] = param.split(' = ')[1]


class Configuration(object):

    objects = OrderedDict([('command', []), ('hostgroup', []), ('service', []), ('host', []), ('resource', []), ('poller', [])])

    def __init__(self, inifile):

        self.inifile = inifile

    def Generate(self, host=None, orch=None):
        
        if not host:
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
                    #action = add
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
                    #resource = aclresourcename
                    
                    [commandname]
                    type = command
                    #action = add
                    #line = $USER1$/check_ping -H $HOSTADDRESS$ -w 3000.0,80% -c 5000.0,100% -p 1
                    
                    [servicename]
                    type = service
                    #action = add
                    #alias = Service Name
                    #group = hostgroupname
                    #template = templatename
                    #check_command = check-host-alive
                    #check_command_arguments = !5000,20%!10000,60% 
    
                    [aclresourcename]
                    type = resource
                    #action = reload
    
                    [pollername]
                    type = poller
                    #action = restart
                ''').format(default))
        else:
            obj = orch.Clone(host)
            with open(self.inifile, 'w') as openini:
                openini.write(dedent('''\
                    # Change hostname
                    [hostname]
                    type = host
                    action = add
                    # Change alias description
                    alias = Host Name
                    # Change IP address
                    ip = 10.1.20.1
                    template = {0}
                    group = {1}
                    # Change ACL
                    resource = {2}
                    poller = {3}
                    snmp_community = 1ft4Ko9uqdt8U
                    snmp_version = 2c

                    # Change ACL
                    [{2}]
                    type = resource
                    action = reload
    
                    [{3}]
                    type = poller
                    action = restart
                ''').format(obj['templates'], obj['hostgroups'], 'GSS_SAS-Resources', obj['poller']))

    def Apply(self):

        try:
            config = RawConfigParser()
            
            with open(self.inifile, 'r') as openini:
                config.read_file(openini)

        except MissingSectionHeaderError as e:
            print("Error: {0}".format(e))
            raise SystemExit
        
        except IOError:
            print("Error: No such file or directory")
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
        
        filterwarnings("ignore", category=DeprecationWarning)
        
        for param in defaultconf:
            try:
                if param.startswith(object['type']):
                    type = param.partition('_')[2]

            except KeyError:
                object[type] = defaultconf[param]

        return object


class Orchestrate(object):

    user = 'admin'
    force = False
    password = None
    status = []

    def __init__(self):

        pass

    def __getattribute__(self, attr):

        method = object.__getattribute__(self, attr)

        if type(method) is MethodType and method.__name__ is not 'Execute':
            self.status = []

        return method

    def Authenticate(self):

        if not self.password:
            try:
                self.password = getpass()
            except KeyboardInterrupt:
                print(), exit(0)

        stdout, error = Popen('/usr/bin/centreon -u {0} -p {1}'.format(self.user, self.password),
            shell=True, stdout=PIPE, stderr=PIPE).communicate()

        if stdout.strip():
            sleep(2); print("Wrong username or password.")
            self.password = None
            self.Authenticate()
            
    def Enable(self, host, service):
    
        self.Execute('-o SERVICE -a setparam -v "{0};{1};event_handler_enabled;1"'.format(host, service))
            
    def Disable(self, host, service):

        self.Execute('-o SERVICE -a setparam -v "{0};{1};event_handler_enabled;0"'.format(host, service))

    def Hostgroup(self, name, hostgroup):

        if hostgroup['action'] == 'add':
            self.Execute('-o HG -a add -v "{0};{1}"'.format(name, hostgroup['alias']))
            if 'resource' in hostgroup:
                self.Execute('-o ACLRESOURCE -a grant_hostgroup -v "{0};{1}"'.format(hostgroup['resource'], name))

        # Create new entries for possible configurations

    def Command(self, name, command):

        if command['action'] == 'add':
            self.Execute('-o CMD -a ADD -v \'{0};check;{1}\''.format(name, command['line']))

        # Create new entries for possible configurations

    def Service(self, name, service):
        
        if 'host' in service.keys():
            action = 'SERVICE'
            target = service['host']
        else:
            action = 'HGSERVICE'
            target = service['group']

        if service['action'] == 'add':
            self.Execute('-o {0} -a add -v "{1};{2};{3}"'.format(action, target, name, service['template']))
            if 'check_command' in service:
                self.Execute('-o {0} -a setparam -v "{1};{2};check_command;{3}"'.format(action, target, name, service['check_command']))
                if 'check_command_arguments' in service:
                    self.Execute('-o {0} -a setparam -v "{1};{2};check_command_arguments;{3}"'.format(action, 
                        target, name, service['check_command_arguments']))

        # Create new entries for possible configurations

    def Host(self, name, host):

        if host['action'] == 'add':
            self.Execute('-o HOST -a ADD -v "{0};{1};{2};{3};{4};{5}"'.format(name, host['alias'], host['ip'],
                host['template'], host['poller'], host['group']))
            self.Execute('-o HOST -a setparam -v "{0};snmp_community;1ft4Ko9uqdt8U"'.format(name))
            self.Execute('-o HOST -a setparam -v "{0};snmp_version;2c"'.format(name))
            if 'resource' in host:
                self.Execute('-o ACLRESOURCE -a grant_host -v "{0};{1}"'.format(host['resource'], name))

        # Create new entries for possible configurations

    def Resource(self, name, resource):

        self.Execute('-o ACL -a reload')

        # Create new entries for possible configurations

    def Poller(self, name, poller):
        
        stdout, status = Popen('/usr/bin/centreon -u {0} -p {1} -a POLLERLIST | grep {2}'.format(self.user, 
            self.password, name), shell=True, stdout=PIPE, stderr=PIPE).communicate()

        if poller['action'] == 'restart':
            self.Execute('-a APPLYCFG -v "{0}"'.format(stdout[0]), True)

        # Create new entries for possible configurations

    def Clone(self, host):
    
        objects = OrderedDict([('hostgroups', []), ('templates', []), ('poller', [])]) # Poller damages output, best if it is last
        
        self.Execute('-o HOST -a gethostgroup -v {0}'.format(host))
        self.Execute('-o HOST -a gettemplate -v {0}'.format(host))
        self.Execute('-a POLLERLIST')
        
        for each, obj in zip(self.status, objects.keys()):
            if not each[0]:
                if obj == 'poller':
                    for line in each[1].split('\n'):
                        poller = line[1:].strip()
                        self.Execute('-o INSTANCE -a GETHOSTS -v {0} | grep {1}'.format(poller, host))
                        if self.status[-1][1]:
                            objects[obj].append(poller)
                else:
                    for line in each[1].split('\n')[1:]:
                        objects[obj].append(line.split(';')[1])
            else:
                print('Error: {0}'.format(each[1]))
                raise SystemExit
                
            objects[obj] = '|'.join(objects[obj])
        	   
        return objects
        
    def Execute(self, command, privileged=False):
        
        if privileged:
            stdout, status = Popen('sudo su -c "/usr/bin/centreon -u {0} -p {1} {2}" centreon'.format(self.user, self.password, command), shell=True, stdout=PIPE, stderr=PIPE).communicate()
        else:
            stdout, status = Popen('/usr/bin/centreon -u {0} -p {1} {2}'.format(self.user, self.password, command), shell=True, stdout=PIPE, stderr=PIPE).communicate()

        self.status.append([status, stdout.strip()])


class ROrchestrate(Orchestrate):

    def __init__(self, url):

        self.url = url

    def Authenticate(self):

        if not self.password:
            try:
                self.password = getpass()
            except KeyboardInterrupt:
                print(), exit(0)

        response = post('http://{0}/centreon/api/index.php?action=authenticate'.format(self.url), data=
            {"username": self.user, "password": self.password})

        try:
            self.token = response.json()['authToken']
        except (ValueError, TypeError):
            sleep(2); print("Wrong username or password for user {0}.".format(self.user))
            self.password = None
            self.Authenticate()
            
    def Enable(self, host, service):
        
        self.Execute({"object": "service", "action": "setparam", "values": 
            "{0};{1};event_handler_enabled;1".format(host, service)})
            
    def Disable(self, host, service):
        
        self.Execute({"object": "service", "action": "setparam", "values": 
            "{0};{1};event_handler_enabled;0".format(host, service)})

    def Hostgroup(self, name, hostgroup):

        if hostgroup['action'] == 'add':
            self.Execute({"object": "hg", "action": "add", "values": "{0};{1}".format(name, hostgroup['alias'])})
            if 'resource' in hostgroup:
                self.Execute({"object": "aclresource", "action": "grant_hostgroup", "values": "{0};{1}".format(
                    hostgroup['resource'], name)})

        # Create new entries for possible configurations

    def Command(self, name, command):

        if command['action'] == 'add':
            self.Execute({"object": "cmd", "action": "add", "values": '{0};check;{1}'.format(name, command['line'])})

        # Create new entries for possible configurations

    def Service(self, name, service):
        
        if 'host' in service.keys():
            action = "service"
            target = service['host']
        else:
            action = "hgservice"
            target = service['group']

        if service['action'] == 'add':
            self.Execute({"object": action, "action": "add", "values": "{0};{1};{2}".format(target, name,
                service['template'])})
            if 'check_command' in service:
                self.Execute({"object": action, "action": "setparam", "values": "{0};{1};check_command;{2}".format(
                    target, name, service['check_command'])})
                if 'check_command_arguments' in service:
                    self.Execute({"object": action, "action": "setparam", "values": "{0};{1};check_command_arguments;{2}".format(
                        target, name, service['check_command_arguments'])})

        # Create new entries for possible configurations

    def Host(self, name, host):

        if host['action'] == 'add':
            self.Execute({"object": "host", "action": "add", "values": "{0};{1};{2};{3};{4};{5}".format(name, 
                host['alias'], host['ip'], host['template'], host['poller'], host['group'])})
            if 'resource' in host:
                self.Execute({"object": "aclresource", "action": "grant_host", "values": "{0};{1}".format(
                    host['resource'], name)})

        # Create new entries for possible configurations

    def Resource(self, name, resource):

        self.Execute({"object": "acl", "action": "reload"})

        # Create new entries for possible configurations

    def Poller(self, name, poller):

        self.Execute({"action": "pollerlist"})
        for each in self.status[-1][1]:
            if type(each) is dict and each['name'].lower() == name:
                break

        if poller['action'] == 'restart':
            self.Execute({"action": "applycfg", "values": each['poller_id']})

        # Create new entries for possible configurations

    def Clone(self, host):
        
        objects = OrderedDict([('hostgroups', []), ('templates', []), ('poller', [])]) # Poller damages output, best if it is last
        
        self.Execute({"object": "host", "action": "gethostgroup", "values": host})
        self.Execute({"object": "host", "action": "gettemplate", "values": host})
        self.Execute({"action": "pollerlist"})
        
        for each, obj in zip(self.status, objects.keys()):
            if not each[0]:
                if obj == 'poller':
                    for line in each[1].split('\n'):
                        poller = line[1:].strip()
                        self.Execute({"object": "instance", "action": "gethosts", "values": poller})

                        if self.status[-1][1]:
                            objects[obj].append(poller)
                else:
                    for line in each[1].split('\n')[1:]:
                        objects[obj].append(line.split(';')[1])
            else:
                print('Error: {0}'.format(each[1]))
                raise SystemExit
                
            objects[obj] = '|'.join(objects[obj])
               
        return objects
        
    def Execute(self, data):

        api_string = 'http://{0}/centreon/api/index.php?action=action&object=centreon_clapi'.format(self.url)
        response = post(api_string, data=dumps(data), headers={'content-type': 'application/json',
            'centreon-auth-token': self.token})

        try:
            result = response.json()
            if response.__dict__['status_code'] != 200:
                raise RuntimeError
        except ValueError:
            self.status.append([1, response])
        except RuntimeError:
            self.status.append([1, result])
        else:
            self.status.append([0, result['result']])
