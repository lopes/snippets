#!/usr/bin/env python3
#
# Created this program to list the top 10 most used
# passwords in Exército Brasileiro's leak.  More
# about this here:
# http://www.tecmundo.com.br/ataque-hacker/89110-in-seguranca-nacional-exercito-hackeado-tem-7-mil-contas-crackeadas.htm
# Passwords were dumped, each in a newline, like this: <CPF>:<Password>
#
# AUTHOR: Joe Lopes <lopes.id>
# LICENSE: GPLv3+
# DATE: 2015-11-11
#
# OUTPUT:
# # used    %       password        shannon guessing    entropy
# ======    ======  ==============  ======= ========    =======
# 381       5.37    12345678        3.0     4.5         4.5
# 79        1.11    123456789       3.17    5.0         5.0
# 18        0.25    87654321        3.0     4.5         4.5
# 16        0.23    10203040        2.0     2.25        2.25
# 12        0.17    06121966        2.16    2.38        2.38
# 9         0.13    infantaria      2.45    2.8         2.8
# 9         0.13    flamengo        3.0     4.5         4.5
# 9         0.13    exercito        2.75    3.62        3.62
# 8         0.11    cavalaria       2.28    2.67        2.67
# 8         0.11    79360011        2.5     3.0         3.0
# Total passwords: 7092
# Minimum entropy: 0.0
# Maximum entropy: 3.32
# Average entropy: 2.51
##


import re
import math
from collections import Counter


def shannon(s):
    '''http://rosettacode.org/wiki/Entropy#Python:_More_succinct_version'''
    p, lns = Counter(s), float(len(s))
    return -sum(count/lns * math.log(count/lns,2) for count in p.values())

def guessing(s):
    '''https://www.lysator.liu.se/~jc/mthesis/A_Source_code.html#functiondef:entropies.py:guessing_entropy'''
    vector, d, l = list(), dict(), len(s)
    for c in s: d[c] = d.get(c, 0) + 1
    for c in d.items(): vector.append(c[1] / l)
    return sum([p*i for i,p in enumerate(sorted(vector,reverse=True))]) + 1

def xkcd(s):
    '''http://www.explainxkcd.com/wiki/index.php/936:_Password_Strength
    Consider s as a truly random string.  Returns how many bits of entropy
    it has.
    TODO: Fix some bugs here.  Apparently, some characters aren't splitted
          properly.  Ex.: re.split(..., 'ReieRainha') == ['R', 'eie', 'R', 'ainha']
          After every bugs are fixed, change line 90.

    '''

    weights = (lambda x: 26 if x.islower() else 0,
               lambda x: 10 if x.isdigit() else 0,
               lambda x: 26 if x.isupper() else 0,
               lambda x: 0 if x.isalnum() else 32)
    charsets = filter(None, re.split('([a-z]+)|([0-9]+)|([A-Z]+)|([^a-z0-9A-Z]+)', s)[1:-1])
    print(list(charsets))

    return len(s) * math.log(sum([w(c) for c in list(charsets) for w in weights]), 2)

def get_passwords(dump_file):
    '''Open dump file, get passwords, count and put'em in a dictionary.'''

    with open(dump_file) as f: dump = f.read()
    passwords, count = dict(), 0

    for line in dump.splitlines():
        if (re.match('^[0-9]+:', line)):
            count += 1
            p = line.split(':')[1]
            passwords[p] = passwords.get(p, 0) + 1
    return (passwords, count)

def create_table(p):
    '''Create a list of tuples (table) in this form:
       [(<time used>, <%>, <pass>, <shannon>, <guessing>, <xkcd>), ...]

    '''

    t, plen = list(), p[1]

    for k,v in p[0].items():
        t.append((v, v*100.0/plen, k, shannon(k), guessing(k), guessing(k)))
    return (sorted(t,reverse=True), plen)


table, plen = create_table(get_passwords('eb.txt'))


print('# used\t%\tpassword\tshannon\tguessing\tentropy\n\
======\t======\t==============\t=======\t========\t=======')
for t in table[:10]:
    print(str(t[0]) + '\t' + str(round(t[1], 2)) + '\t' + t[2] + '\t' +
          str(round(t[3], 2)) + '\t' + str(round(t[4], 2)) + '\t\t' + str(round(t[5], 2)))

print('Total passwords: ' + str(plen) +
      '\nMinimum entropy: ' +
      str(abs(round(min([e[3] for e in table]), 2))) +
      '\nMaximum entropy: ' +
      str(round(max([e[3] for e in table]), 2)) +
      '\nAverage entropy: ' +
      str(round(sum([e[3] for e in table]) / plen, 2)))
