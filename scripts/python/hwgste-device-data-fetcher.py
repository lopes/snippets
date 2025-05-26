#!/usr/bin/env python3

'''HWg-STEpy is a simple script to get STE info.

This script takes advantage of  HWg-STE's XML interface
to retrieve temperature and humidity information, then
print them on the screen.

To use this, first edit the `devices' variable below to
include the IP addresses of your STE devices, then run:

$ python hwgste.py
'''
__author__ = 'Joe Lopes'
__license__ = 'MIT'
__date__ = '2018-12-28'


from urllib.request import urlopen

try:
    from xmltodict import parse
except ModuleNotFoundError:
    print('Install xmltodict with: $ pip install xmltodict')
    exit(0)


devices = ['888.888.888.888', '888.888.888.888']


def get_data(term):
    '''Gets relevant data from the device.

    :param term: dict object from XML data of a HWg-STE device.
    :returns: a string with relevant data.
    '''
    device = term['val:Root']['Agent']['DeviceName']
    ip = term['val:Root']['Agent']['IP']
    temp_unit = term['val:Root']['SenSet']['Entry'][0]['Units']
    temp_value = term['val:Root']['SenSet']['Entry'][0]['Value']
    rh_unit = term['val:Root']['SenSet']['Entry'][1]['Units']
    rh_value = term['val:Root']['SenSet']['Entry'][1]['Value']

    data = f'Device...........: {device} ({ip})\n'
    data += f'Temperature......: {temp_value} ({temp_unit})\n'
    data += f'Relative Humidity: {rh_value} ({rh_unit})'
    return data


if __name__ == '__main__':
    for device in devices:
        print('-' * 49)
        print(get_data(parse(urlopen(f'http://{device}/values.xml'))))
