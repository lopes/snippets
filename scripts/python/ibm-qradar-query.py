#!/usr/bin/env python3

from sys import argv
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from json import loads
from time import sleep


'''
Performs queries in IBM QRadar.

Requires a valid token and a QRadar instace (tested
under v7.3.0).  The only query implemented at this
moment is `top5-hp`.

Before start using, you must setup at least TOKEN,
CIDR, and SERVER constants according to your
environment.

Usage:
$ python query-radar.py top5-hp

'''
__author__ = 'Joe Lopes'
__license__ = 'MIT'
__date__ = '2019-02-27'


TOKEN = ''
CIDR = ''
SERVER = ''
RETRY = 10
SLEEP = 10  # seconds


class QueryRadar(object):
    def __init__(self, token, query, proto='https',
        server=SERVER, path='api/ariel/searches'):
        self.token = token
        self.query = quote(query)
        self.url = f'{proto}://{server}/{path}'
        self.search_id = self.request_search()
        self.results = self.get_results()

    def request_search(self):
        req = Request(f'{self.url}?query_expression={self.query}',
            headers={'Content-Type':'application/json','SEC':self.token},
            method='POST')
        print(f'Requesting search to {self.url}')
        with urlopen(req) as r:
            return loads(r.read())['search_id']

    def get_results(self):
        req = Request(f'{self.url}/{self.search_id}/results',
            headers={'Content-Type':'application/json','SEC':self.token},
            method='GET')
        for t in range(1, RETRY+1):
            print(f'Requesting results ({t}/{RETRY})')
            sleep(SLEEP)
            try:
                with urlopen(req) as r:
                    return loads(r.read())
            except HTTPError:
                pass
        print('Unable to retrieve results.\nSearch ID:', self.search_id)
        exit(1)


if __name__ == '__main__':
    if argv[1] == 'top5-hp':
        q = QueryRadar(TOKEN,
            f"select sourceip, count(sourceip) as csip \
            from flows where incidr('{CIDR}',destinationip) \
            group by sourceip order by csip desc limit 5 last 7 days")
        print('\nIP ADDRESS\t\tCOUNT')
        print('-' * 29)
        for i in q.results['flows']:
            print(f'{i["sourceip"]}\t\t{int(float(i["csip"]))}')
