#!/usr/bin/python3
#
# This program retrives and update a certain file according to a URI.  In other
# words, the URI is fetched and, if the content of that file is different, the
# new content is written into that file.
#
# License: MIT
# Date: 2017-02-21
##


from urllib.request import urlopen
from hashlib import sha256
from logging import basicConfig, info, INFO
from os import remove


path_current = '/home/user/.thief.txt'
path_auxfile = '/tmp/thief.txt'
uri = 'https://SET.THIS.URI'
content = ''


def file_hasher(p):
    """Hashes a file using SHA 256.

    Args:
        - p (string): file's path.

    Returns the hash itself in hex.

    """

    BLOCKSIZE = 65536
    hasher = sha256()
    with open(p, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


basicConfig(level=INFO)
info('Fetching content')
with urlopen(uri) as response, open(path_auxfile, 'wb') as f:
    content = response.read()
    f.write(content)

try:
    info('Hashing files')
    if file_hasher(path_current) != file_hasher(path_auxfile):
        info('Writing new content')
        with open(path_current, 'wb') as f:
            f.write(content)
    else:
        info('No changes are needed')
except FileNotFoundError:
    info('Writing new content')
    with open(path_current, 'wb') as f:
        f.write(content)

info('Deleting auxiliary file')
remove(path_auxfile)
