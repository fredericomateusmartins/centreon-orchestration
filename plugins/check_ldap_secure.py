#!/usr/bin/env python

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 0.1

# Check secure LDAP connection with certificate, through port 636.

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import path, popen
from sys import exit
from textwrap import dedent
from time import time


class Parsing(object):
    
    name = path.basename(__file__)

    def __init__(self):
        
        parser = ArgumentParser(prog='python {0}'.format(self.name), add_help=False,
            formatter_class=RawDescriptionHelpFormatter, description=dedent('''\
                Nagios Secure LDAP Plugin
                -------------------------
                  Python script for
                  LDAPS certificate
                  check.
                '''), epilog = dedent('''\
                Check the git repository at https://github.com/flippym/nagios-collection,
                for more information about usage, documentation and bug report.'''))

        optional.add_argument('-f', '--fqdn', dest='host', type=str, required=True, help='LDAP Server FQDN')
        optional.add_argument('-b', '--basedn', dest='base', type=str, required=True, help='LDAP server base DN, example: "dc=example,dc=com"')
        optional.add_argument('-u', '--binduser', dest='user', type=str, required=True, help='Bind user name, example: "uid=bind,ou=users,dc=example,dc=com"')
        optional.add_argument('-p', '--bindpass', dest='password', type=str, required=True, help='Bind user password')
        optional.add_argument('-c', '--certificate', dest='cert' , type=str, help='Specify the certificate to use, the default is fetched by the FQDN specified')
        optional.add_argument('-h', '--help', action='help', help='Show this help message')
        optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(self.name, __version__), help='Show program version')
        
        self.args = parser.parse_args()

        if not self.args.cert:
                self.args.cert = '/etc/openldap/certs/{0}.pem'.format(args.fqdn.split('.')[0])


class Run(object):
    
    def __init__(self, args):

        timestart = time()
        ldapsearch = popen('env LDAPTLS_CACERT=%s ldapsearch -x -H ldaps://%s -b %s -D %s -w %s -s one' % (args.cert, args.host, args.base, args.user, args.password))

        for each in ldapsearch:
                if "result: 0 Success" == each.strip():
                        print("LDAP OK - %s seconds response time" % round(time() - timestart, 2))
                        exit(0)

        print("LDAP Critical - Could not bind to LDAP server")
        exit(2)


args = Parsing().args
Run(args)
