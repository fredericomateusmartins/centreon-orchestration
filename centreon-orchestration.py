#!/usr/bin/env python

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 1

# Orchestrate a new environment for Centreon, based on a .ini file parsing. Currently only developed the action add,
# for hosts/hostgroups/services and edit for ACL resources.

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import path
from textwrap import dedent

from library.output import Handler
from library.orchestration import Configuration, Orchestrate


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
                Check the git repository at https://github.com/flippym/centreon-orchestration,
                for more information about usage, documentation and bug report.'''))

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-i', '--ini', metavar='file', type=str, help='Specify .ini configuration file', required=True)
        optional.add_argument('-u', '--user', metavar='user', type=str, help='Centreon user with administration privileges',
            default='admin')
        optional.add_argument('-f', '--force', action='store_true', help='Force provision to continue, even if error are encountered')
        optional.add_argument('-g', '--generate-ini', action='store_true', help='Generate .ini template configuration file')
        optional.add_argument('-h', '--help', action='help', help='Show this help message')
        optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(self.name, __version__),
            help='Show program version')

        self.args = parser.parse_args()


hand = Handler()
pars = Parsing()
conf = Configuration(pars.args.ini)

if pars.args.generate_ini:
    try:
        if not path.exists(conf.inifile) or raw_input("File {0} exists, overwrite? [y/N] ".format(conf.inifile)) == 'y':
            conf.Generate()
        
        raise SystemExit

    except KeyboardInterrupt:
        raise SystemExit

hand.Info('Parsing file {0}'.format(conf.inifile))
conf.Apply()

orch = Orchestrate()
orch.user = pars.args.user
orch.force = pars.args.force

orch.Authenticate()

for types in conf.objects.keys():
    for objects in conf.objects[types]:
        name = str(objects).partition(': ')[2][:-1]
        objects = conf.Assert(objects)

        try:
            hand.Start('{0} {1} {2}'.format(objects['action'].capitalize(), types, name))
            getattr(orch, types.capitalize())(name, objects)
        except KeyboardInterrupt:
            hand.Stop(None, proceed=orch.force)
            exit()

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
                hand.Error(each[1])
                break
            elif not each[0] and each[1]:
                hand.Info(each[1])
                break
