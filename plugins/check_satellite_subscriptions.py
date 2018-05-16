#!/usr/bin/env python

from datetime import datetime
from requests import get, post

class Satellite(object):

    host = 'satellite.example.com'
    satellite = 'https://{}/katello/api/v2'.format(host)
    username = 'username'
    password = 'password'

    def GetSubscriptions(self):

        self.result = get('{0}/subscriptions?per_page=10000'.format(self.satellite), auth=(self.username,
            self.password), verify=False).json()

        if self.result.get('error', None):
            print(self.result['error']['message'])
            exit(1)
        elif self.result.get('errors', None):
            print(self.result['displayMessage'])
            exit(1)

        self.result = self.result['results']

        if not self.result:
            print("No subscriptions found, permissions for user '{0}' may be missing".format(self.username))
            exit(1)

    def AboutToExpire(self):

        self.expiring = {}

        for each in self.result:
            if not each['support_level']:
                continue

            year, month, day = each['end_date'][:10].split('-')
            if (datetime(int(year), int(month), int(day)) - datetime.now()).days < 30:
                date = '{0}-{1}-{2}'.format(day, month, year)
                if not date in self.expiring:
                    self.expiring[date] = 0

                self.expiring[date] += 1


sat = Satellite()
sat.GetSubscriptions()
sat.AboutToExpire()

if sat.expiring:
    for date in sat.expiring:
        print("{0} subscriptions expire in {1}".format(sat.expiring[date], date))
    exit(1)

print("All subscriptions OK")
exit(0)
