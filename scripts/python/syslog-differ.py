#!/usr/local/bin/python3

'''
Monitors some log files and send new entries to syslog.
This script requires a config file to import paths to the files.
The main concept is that there are a repository with log files
(which I call 'source files') and an auxiliary repository of
files ('working files').
The idea here is to create a copy of source files in the work
directory, then calculating the diff between the source files
and the working files.  This difference is sent to syslog and
appended to the appropriate working file.  Obviously, in the
first execution the whole file will be sent to syslog and this
will also happen at the end of the day.

DEPLOYMENT
    1. Create the configuration file
    2. Give this script the necessary permissions
    3. Configure syslog to forward events to a SIEM
    4. Test the script execution
    5. Automate the execution using cron

NOTE
When files are rotated the last logs will be lost because
the new file will be smaller in size than the last one and
then the new will override the old one.  This way, the last
log entries written in the old file will be lost.  A routine
could be created to retrieve the last entries from the old
file before override it in workroot, but a way to minimize
such problem is to run this script often.  If it runs every
30 seconds, for instance, only the last 30 seconds of logs
will be lost in a day.

Author: Joe Lopes <lopes.id>
License: MIT
Date: 2021-08-25

CONFIG
The configuration file (teslacoil.conf) must have the structure
below and the correct path to it must be informed in line 71.
    [path]
        logroot  = /var/directory
        workroot = /tmp/teslacoil
    [files]
        group1 = f1.log f2.log
        group2 = f3.log f4.log

CHANGELOG
    2021-09-27
    Added the `encoding` option to solve the `UnicodeDecodeError`.
    In my case, the charset is the same hardcoded here, but other
    people can easily change it setting up the variable.
'''

from datetime import date
from re import match
from difflib import ndiff
from syslog import syslog, LOG_NOTICE, LOG_ERR
from configparser import ConfigParser
from os import makedirs
from os.path import getsize, isdir
from shutil import copyfile

today = date.today().strftime('%Y-%m-%d')
year = today[:4]
re_newlog = r'^- '
encoding = 'ISO-8859-1'
config = ConfigParser()
config.read('teslacoil.conf')

def full_sync(src_path, dst_path, src):
    copyfile(src_path, dst_path)
    try:
        for line in src:
            syslog(LOG_NOTICE, line)
    except UnicodeDecodeError:
        syslog(LOG_ERR, f'UnicodeDecodeError: {src_path}')

for k in config['files'].keys():
    for f in config['files'][k].split(' '):
        sf_path = f'{config["path"]["logroot"]}/{k}/{year}/{f}.{today}'
        try:
            with open(sf_path, 'r', encoding=encoding) as sf:
                wf_path = f'{config["path"]["workroot"]}/{k}/{f}'
                try:
                    with open(wf_path, 'r+', encoding=encoding) as wf:
                        # new day clean-up
                        if getsize(sf_path) < getsize(wf_path):
                            full_sync(sf_path, wf_path, sf)
                            continue
                        try:
                            for line in ndiff(sf.readlines(), wf.readlines()):
                                if match(re_newlog, line):
                                    syslog(LOG_NOTICE, line[2:])
                                    wf.write(line[2:])
                        except UnicodeDecodeError:
                            syslog(LOG_ERR, f'UnicodeDecodeError: {sf_path}')
                except FileNotFoundError:
                    if not isdir(f'{config["path"]["workroot"]}/{k}'):
                        makedirs(f'{config["path"]["workroot"]}/{k}')
                    full_sync(sf_path, wf_path, sf)
        except FileNotFoundError:
            pass
