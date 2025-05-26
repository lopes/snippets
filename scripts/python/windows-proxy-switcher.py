'''Sets Windows' proxy configurations easily.

This script allows user to update Windows proxy settings easily,
by using predefined values assigned to proxies identified by
keywords.

Note that it'll also refresh your system to guarantee that all
settings take effect.  Although in the tests it seemed unnecessary
(Windows 8.1), it's considered just a guarantee.

Of course, you must reload all pages after running this script, but
the first thing you gotta do before running it is to setup the PROXIES
variable, creating an ID for each proxy in your environment, so you
can refer to it by using that ID as a parameter.

The "default" and "off" words are reserved, one for your proxy default
settings and the other to disable proxy --remember to set up the
"default" keyword properly.  Running this script without parameters
will print the current proxy settings on screen.

Usage examples:
$ python winproxy.py
$ python winproxy.py off
$ python winproxy.py proxyid

Based on: https://bitbucket.org/canassa/switch-proxy
'''
__author__ = 'Joe Lopes'
__license__ = 'MIT'
__date__ = '2019-01-03'


import ctypes

from sys import argv
from winreg import OpenKey, QueryValueEx, SetValueEx
from winreg import HKEY_CURRENT_USER, KEY_ALL_ACCESS


PROXIES = {
    'default': {
        'enable': 1,
        'override': u'127.0.0.1;localhost;<local>',
        'server': u'10.0.0.5:8080'
    },
    'off': {
        'enable': 0,
        'override': u'-',
        'server': u'-'
    },
    'proxyid': {
        'enable': 1,
        'override': u'127.0.0.1;localhost;<local>',
        'server': u'10.0.1.5:8080'
    },
}

INTERNET_SETTINGS = OpenKey(HKEY_CURRENT_USER,
    r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
    0, KEY_ALL_ACCESS)


def set_key(name, value):
    SetValueEx(INTERNET_SETTINGS, name, 0,
        QueryValueEx(INTERNET_SETTINGS, name)[1], value)


if __name__ == '__main__':
    try:
        proxy = argv[1]
    except IndexError:
        print(f'Enable....: {QueryValueEx(INTERNET_SETTINGS,"ProxyEnable")[0]}')
        print(f'Server....: {QueryValueEx(INTERNET_SETTINGS,"ProxyServer")[0]}')
        print(f'Exceptions: {QueryValueEx(INTERNET_SETTINGS,"ProxyOverride")[0]}')
        exit(0)

    try:
        set_key('ProxyEnable', PROXIES[proxy]['enable'])
        set_key('ProxyOverride', PROXIES[proxy]['override'])
        set_key('ProxyServer', PROXIES[proxy]['server'])

        # granting the system refresh for settings take effect
        internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
        internet_set_option(0, 37, 0, 0)  # refresh
        internet_set_option(0, 39, 0, 0)  # settings changed
    except KeyError:
        print(f'Registered proxies: {PROXIES.keys()}')
        exit(1)
    exit(0)
