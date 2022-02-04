#!/usr/bin/env python

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 1.1

# Orchestrate a new environment for Centreon, based on a .ini file parsing

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from json import loads
from os import path
from signal import SIGINT, signal
from textwrap import dedent

from library import Configuration, Handler, Orchestrate, ROrchestrate


class Parsing(object):

    name = path.basename(__file__)

    def __init__(self):

        self.Arguments()

    def Arguments(self):

        parser = ArgumentParser(prog='python {0}'.format(self.name), add_help=False,
            formatter_class=RawDescriptionHelpFormatter, description=dedent('''\
                Centreon API Automation
                -----------------------
                  Python script for
                  Centreon task
                  automation.
                '''), epilog = dedent('''\
                Check the git repository at https://github.com/fredericomateusmartins/centreon-orchestration,
                for more information about usage, documentation and bug report.'''))

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-i', '--ini', metavar='file', type=str, help="Specify .ini configuration file", required=False)
        optional.add_argument('-u', '--user', metavar='user', type=str, help="Centreon user with administration privileges",
            default='admin')
        optional.add_argument('-f', '--force', action='store_true', help="Force provision to continue, even if error are encountered")
        optional.add_argument('-e', '--enable', metavar='dic', type=str, help="Enable event handler for set of hosts in a given dictionary. Ex: '{\"hostname.example.com\":[\"Memory\",\"SSH_Connectivity\"]}'")
        optional.add_argument('-d', '--disable', metavar='dic', type=str, help="Disable event handler for set of hosts in a given dictionary like 'enable'")
        optional.add_argument('-g', '--generate-ini', action='store_true', help="Generate .ini template configuration file")
        optional.add_argument('-H', '--host', metavar='host', help="Generates .ini configuration file based on given host")
        optional.add_argument('-R', '--REST', action='store_true', help="Use REST API instead of CLAPI")
        optional.add_argument('-h', '--help', action='help', help="Show this help message")
        optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(self.name, __version__),
            help='Show program version')

        self.args = parser.parse_args()


def SignalHandler(signal, frame):
    
    try:
        if hand.animation.isAlive():
            hand.Stop()
    except AttributeError:
        print
        
    exit()
    
    
signal(SIGINT, SignalHandler)

hand = Handler()
pars = Parsing()
conf = Configuration(pars.args.ini)

if pars.args.REST:
    orch = ROrchestrate('centreon.example.com')
else:
    orch = Orchestrate()

orch.user = pars.args.user
orch.force = pars.args.force
orch.Authenticate()

for action in ['enable', 'disable']:
    if getattr(pars.args, action):
        hosts = loads(getattr(pars.args, action))
        for host in hosts:
            if type(hosts[host]) is not list:
                print('Services must be in a list format inside the dictionary')
                exit(1)
            for service in hosts[host]:
                hand.Start('{0} service {1} for host {2}'.format(action.capitalize(), service, host))
                getattr(orch, action.capitalize())(host, service)
                hand.Stop(orch.status[0], proceed=orch.force)
        exit(0)
        

if pars.args.generate_ini and not pars.args.host:
    if not path.exists(conf.inifile) or raw_input("File {0} exists, overwrite? [y/N] ".format(conf.inifile)) == 'y':
        conf.Generate()
        raise SystemExit

conf.Apply()

for types in conf.objects.keys():
    for objects in conf.objects[types]:
        name = str(objects).partition(': ')[2][:-1]
        objects = conf.Assert(objects)

        hand.Start('{0} {1} {2}'.format(objects['action'].capitalize(), types, name))
        getattr(orch, types.capitalize())(name, objects)

        for status in orch.status:
            if types == 'poller':
                status[0] = None
                orch.status = [[None, None]]
                break
            elif status[0]:
                break

        hand.Stop(status[0], proceed=orch.force)

        for each in orch.status:
            if each[0]:
                hand.Info(each[1])
                break
            elif not each[0] and each[1]:
                hand.Info(each[1])
                break
