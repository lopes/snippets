#!/usr/bin/env python
#coding: utf8

"""IP

Provides a class that stores an IPv4 address like an
integer number. But it is transparent to the user.

"""

__author__ = 'Joe Lopes <lopes.id>'
__license__ = 'GPLv3+'
__version__ = '0.1.0'
__date__ = '2013-02-25'


import re


class IPv4(object):

    """Stores an IPv4 address in its integer form.

    This process is totally transparent for the user
    and this class can also receive the number of bits
    that compose the address too --like in IP masks.

    Requires re module.

    Raises AttributeError if the given IP addr is
    not valid.

    Examples:
        - IPv4(127.0.0.1)
        - IPv4(24)  # 255.255.255.0

    """

    def __init__(self, addr='127.0.0.1'):
        pat_addr = re.compile('^(((1[0-9]|[1-9]?)[0-9]|2([0-4][0-9]|5[0-5]))\.){3}((1[0-9]|[1-9]?)[0-9]|2([0-4][0-9]|5[0-5]))$')
        pat_numb = re.compile('(^3[012]$|^[12][0-9]$|^[0-9]$)')

        if pat_addr.match(addr):
            self.addr = self.to_number(addr)

        elif pat_numb.match(addr):
            self.addr = self.fill(int(addr))

        else:
            raise AttributeError('Invalid IP address: {0}'.format(addr))


    def __int__(self):
        """Converts an IP object to integer notation."""
        return self.addr


    def __str__(self):
        """Converts an IP object to string notation."""
        return self.to_string(self.addr)


    def to_number(self, ipstr='127.0.0.1'):
        """Receives an IPv4 addr and returns its integer notation."""
        octets = ipstr.split('.')
        ipnumber = 0

        for octet in octets:
            ipnumber = ipnumber << 8
            ipnumber += int(octet)

        return ipnumber


    def to_string(self, ipnum=0):
        """Receives an IP addr and returns its traditional notation."""
        octlist = []

        for index in [0, 1, 2, 3]:
            octlist.append(ipnum & 255)
            ipnum = ipnum >> 8

        return '{0}.{1}.{2}.{3}'.format(octlist[3], octlist[2],
                                        octlist[1], octlist[0])

    def fill(self, bits=8):
        """Fill an IP address with ``bits'' 1."""
        number = 2 ** bits - 1
        return number << (32 - bits)


##
# Main
#
if __name__ == '__main__':
    input_string = raw_input('Type: ')

    try:
        input_list = input_string.split('/')
        addr = IPv4(input_list[0].strip())
        mask = IPv4(input_list[1].strip())

    except IndexError:
        if 0 <= addr.addr <= 2147483647:
            bits = '8'
        elif 2147483648 <= addr.addr <= 3221225471:
            bits = '16'
        elif 3221225472 <= addr.addr <= 3758096383:
            bits = '24'
        else:
            bits = '28'

        mask = IPv4(bits)

    except AttributeError:
        print 'Invalid input: {0}'.format(input_string)
        exit(1)

    subnet = int(addr) & int(mask)
    broadcast = subnet | ~int(mask)
    wildcard = ~int(mask)
    noh = (4294967295 ^ int(mask)) - 1
    fh = int(subnet) + 1
    lh = int(broadcast) - 1

    print('\nString: {0}\tDecimal: {1}\tHexadecimal: {2}\tOctal: {3}\tBinary: {4}'.format(addr, int(addr), hex(int(addr)), oct(int(addr)), bin(int(addr))[2:].zfill(32)))
    print('String: {0}\tDecimal: {1}\tHexadecimal: {2}\tOctal: {3}\tBinary: {4}'.format(mask, int(mask), hex(int(mask)), oct(int(mask)), bin(int(mask))[2:].zfill(32)))
    print('Subnet: {0}'.format(mask.to_string(subnet)))
    print('Broadcast: {0}'.format(mask.to_string(broadcast)))
    print('Wildcard: {0}'.format(mask.to_string(wildcard)))
    print('Number of Hosts: {0}'.format(noh))
    print('First Host: {0}'.format(mask.to_string(fh)))
    print('Last Host: {0}\n'.format(mask.to_string(lh)))
