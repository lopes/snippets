#!/usr/bin/env python3
#ip-expander.py
#
# Expand IP ranges into individual addresses.
#
# REQUIREMENTS
# The `cidr-ranges-list.txt` file must be in the same directory as this script.
# This file must follow the format:
#   <CIDR>, "<COMMENT>"
#
# USAGE
# Having the requirements met, run this script and it will output the expanded.
# You might want to redirect the output to a file, like this:
#   python3 ip-expand.py > expanded.txt
#
# AUTHOR.: Joe Lopes <lopes.id>
# DATE...: 2024-08-06
# LICENSE: MIT
##


from re import compile
from ipaddress import IPv4Network

re_line = compile(r'(?P<cidr>[\d/\.]+)\s*,\s*"(?P<comm>.*)"$')
expanded = list()

with open('cidr-ranges-list.txt','r') as f:
  lines = f.readlines()
  for line in lines:
    match = re_line.match(line)
    if match:
      addrs = IPv4Network(match.group('cidr'))
      comm = match.group('comm')
      for addr in addrs:
        expanded.append(f'{addr}  // {comm}')

for line in expanded:
  print(line)
