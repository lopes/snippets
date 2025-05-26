#!/usr/bin/env python3

'''Squid Cleaner

This script takes a file with a list of domains in Squid format
separated by "comma-space" and outputs a new list without
duplicates, shadows (.domain.com and domain.com <-removes this),
and overlaps (.domain.com, sub.domain.com <-removes this).

It can also check is domains are responsive, but of course this
can be tricky, because of false positives.

DATE: 2019-06-26
'''


from sys import argv
from re import match


class SquidCleaner(object):
    def __init__(self, infile, outfile):
        self.domains = [s.strip() for s in
            sorted(infile.readlines()[0].split(', '))]

        self.stats = {
            'initial': len(self.domains),
            'duplicate': 0,
            'shadowed': 0,
            'overlapped': 0
        }

        self.drop_duplicates()
        self.drop_shadows()
        self.drop_overlaps()
        outfile.write(', '.join(self.domains))

    def drop_duplicates(self):
        domains = self.domains.copy()
        for domain in self.domains:
            while domains.count(domain) > 1:
                domains.remove(domain)
                print(f'DUPLICATE: {domain}')
                self.stats['duplicate'] += 1
        self.domains = domains

    def drop_shadows(self):
        '''Excludes shadowed domains (.domain.com and domain.com <-this).'''
        domains = self.domains.copy()
        for domain in self.domains:
            if domain.startswith('.'):
                while domains.count(domain[1:]):
                    domains.remove(domain[1:])
                    print(f'SHADOWED: {domain[1:]}')
                    self.stats['shadowed'] += 1
        self.domains = domains

    def drop_overlaps(self):
        '''Excludes overlaps (.domain.com and sub.domain.com <-this).'''
        domains = self.domains.copy()
        super_domains = [s[1:] for s in domains if s.startswith('.')]
        for domain in self.domains:
            for super_domain in super_domains:
                if match(f'^.+?\.{super_domain}', domain):
                    try:
                        domains.remove(domain)
                        print(f'OVERLAPPED: {domain}')
                        self.stats['overlapped'] += 1
                    except ValueError:
                        pass  # already removed
        self.domains = domains


if __name__ == '__main__':
    with open(argv[1], 'r') as i, open(argv[2], 'w') as o:
        sc = SquidCleaner(i, o)
        print(f'\nInitial: {sc.stats["initial"]}', end=', ')
        print(f'Duplicate: {sc.stats["duplicate"]}', end=', ')
        print(f'Shadowed: {sc.stats["shadowed"]}', end=', ')
        print(f'Overlapped: {sc.stats["overlapped"]}', end=', ')
        print(f'Now: {len(sc.domains)}')
