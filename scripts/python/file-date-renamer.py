'''
Moves and renames files according to their modification dates.

source directory has a structure like:

SOX-old
    + dir1
        + file1
    + dir2
        + file1

All files will be moved to destination, with no subdirectories.

DATE: 2018-10-29
'''


from os import walk, rename
from os.path import abspath, join, getmtime, splitext, exists
from datetime import datetime


source = abspath('./SOX-old')
destination = abspath('./SOX')


for root,dirs,files in walk(source,topdown=False):
    for f in files:
        print(f'Processing: {f}')
        n,e = splitext(f)
        mtime = datetime.fromtimestamp(getmtime(join(root,f)))
        try:
            rename(join(root,f), join(destination,f'cors-turno-{mtime.strftime("%Y%m%d")}-1{e}'))
        except FileExistsError:
            i = 2
            while exists(join(destination,f'cors-turno-{mtime.strftime("%Y%m%d")}-{i}{e}')):
                i += 1
            rename(join(root,f), join(destination,f'cors-turno-{mtime.strftime("%Y%m%d")}-{i}{e}'))
