# Centreon Orchestration <img src="http://permabit.com/web/wp-content/uploads/2011/12/Orchestration.png" align="right" height="261" width="261"/>
Centreon Environment Orchestration

## Synopsis

The `centreon-orchestration` is intended to be used as a monitoring orchestrator, for easability in adding and editing Centreon objects.
<br>
<br>
The `.ini` file consists of sections for each Centreon object, with parameters in each section for the API.
<br>
<br>
<br>
<br>
<br>
The program requires an `.ini` file as argument, in order to create or edit objects as needed.

```shell
python centreon-orchestration.py --ini playbooks/hostname.ini --user username
```

There can also be generated a default `.ini` file:

```shell
python centreon-orchestration.py --ini playbooks/new_hostname.ini --generate-ini
```

Or generate a `.ini` file based on a host current configuration:

```shell
python centreon-orchestration.py --ini playbooks/clone_hostname.ini --user username --generate-ini --host hostname
```

Every parameter is optional inside the file sections, except it's '[name]' and 'type'. All values will be fetch in the default section.<br>
_If there's no default section, or it is commented out, the default values are set by the program._<br>
_The sections are parsed with the following order `command` > `hostgroup` > `service` > `host` > `resource` > `poller` regardless of their position in the file._
_If another type is given, other than the one's previously shown, it will be ignored by the parser._

```shell
[machine_hostname]
type = host
action = add
alias = New Host Description
ip = 10.1.20.1
template = centreon_host_template
group = linux-servers|hostgroupname_test
resource = resource_name
poller = poller_name
snmp_community = community_string
snmp_version = snmp_version

[hostgroupname_test]
type = hostgroup
action = add
alias = New Test Hostgroup
resource = resource_name

[check_ping_test]
type = command
action = add
line = $USER1$/check_ping -H $HOSTADDRESS$ -w 3000.0,80% -c 5000.0,100% -p 1

[servicename_test]
type = service
action = add
alias = New Test Service
group = hostgroupname_test
template = resource_name
check_command = check_ping_test

[resource_name]
type = resource
action = reload

[poller_name]
type = poller
action = restart
```

## Installation

The only dependencies needed by the program are listed below.

Needed packages:
- [Centreon](https://github.com/centreon/centreon)
- [Python 2.6+](https://www.python.org/download/releases/2.6.6/)
- [ConfigParser](https://svn.python.org/projects/python/branches/release27-maint/Lib/ConfigParser.py)

The program was tested to run only in RHEL-like distributions.

## License

The content of this project and the source code is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html), the full license text can be seen [here](LICENSE).
