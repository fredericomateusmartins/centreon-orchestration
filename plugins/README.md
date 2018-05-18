# Nagios Collection
Nagios Plugin Collection

## Synopsis

Nagios custom made plugins for Red Hat Enterprise Linux.

## Installation

Save the plugins next to the Nagios plugins, restore it's ownership/permissions/SELinux context and test it's execution seeing the parameters with **--help**.

Needed packages: (according to each plugin)
- openldap-clients (ldap_secure)
- NGINX or HTTPd (virtual_hosts)
- cURL (soap_endpoint)

## Contributions

Please ensure your pull request adheres to the following guidelines:

- Try to push clean and intuitive code only. 
- Search previous suggestions before making a new one, as yours may be a duplicate.
- Make an individual pull request for each suggestion.
- Keep descriptions short and simple, but descriptive.
- Check your spelling and grammar.

## License

The content of this project and the source code is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html), the full license text can be seen [here](LICENSE).
