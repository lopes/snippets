#!/usr/bin/python
#
# Analyses a file system path, calculating the hash for each file
# and storing hash and the path for file.  Errors will be recorded
# in errors table ---duh!
#
# Author: Joe Lopes <lopes.id>
# License: GPLv3+
# Date: 2015-11-30
#
## INSTRUCTIONS
# Setup TARGET variable with your file system path to be analysed.
#
## DATABASE
# This software uses PostgreSQL to store data.  You must install
# it and Psycopg before run it.  You also have to build the
# environment with the SQL commands below and setup DB, DB_USER,
# and DB_PASS according to your definitions.
#
# Packages used:
#   -Python 3.3 <http://python.org>
#   -PostgreSQL 9.2 <http://postgresql.org>
#   -Psycopg 2.5.1 <http://initd.org/psycopg>
#
## SQL COMMANDS
#/*creating tables*/
#create table hashes(
#    id serial primary key,
#    sha1 varchar(40) not null unique
#);
#create table files(
#    id serial primary key,
#    path varchar(1024) not null,
#    size integer,
#    ctime timestamp,
#    mtime timestamp,
#    hash integer not null references hashes(id)
#);
#create table errors(
#    id serial primary key,
#    path varchar(1024) not null
#);
#
#/*creating functions*/
#create or replace function ins_hash(varchar(40))
#returns void as
#$$
#    insert into hashes(sha1)
#    values ($1);
#$$
#language sql;
#create or replace function ins_file(varchar(1024), varchar(40),
#                                     integer, timestamp, timestamp)
#returns void as
#$$
#    insert into files(path, hash, size, ctime, mtime)
#    values ($1, (select id from hashes where sha1 = $2), $3, $4, $5);
#$$
#language sql;
#create or replace function ins_error(varchar(1024))
#returns void as
#$$
#    insert into errors(path)
#    values ($1)
#$$
#language sql;
##


import time
from os import walk
from os import stat
from hashlib import sha1

import psycopg2


###
# GLOBAL VARIABLES
# You should set these at your will.
DB      = 'fserver'
DB_USER = 'postgres'
DB_PASS = 'foobar'
TARGET  = 'a:'


###
# MAIN
# Trying to connect to database.
conn = psycopg2.connect(database=DB, user=DB_USER, password=DB_PASS)
cur = conn.cursor()

# Everything's fine.  Let's rock'n'roll!
count = 0
for (dirpath, dirnames, filenames) in walk(TARGET):
    for f in filenames:
        count += 1
        print(count)

        try:
            abspath = '{0}/{1}'.format(dirpath, f)

            sha_1 = sha1(open(abspath, 'rb').read()).hexdigest()

            # Storing hash
            try:
                cur.execute("select ins_hash(%s);", (sha_1,))
            except psycopg2.IntegrityError:
                pass  #Hash already recorded?  OK, next plz!
            conn.commit()

            # Storing file path
            size = stat(abspath).st_size
            ctime = time.strftime('%Y-%m-%d %H:%M:%S',
                                  time.gmtime(stat(abspath).st_ctime))
            mtime = time.strftime('%Y-%m-%d %H:%M:%S',
                                  time.gmtime(stat(abspath).st_mtime))
            cur.execute("select ins_file(%s, %s, %s, %s, %s);",
                        (abspath, sha_1, size, ctime, mtime))
            conn.commit()

        except FileNotFoundError:
            # Logging error
            cur.execute("select ins_error(%s);", (abspath,))
            conn.commit()

# Bye, bye, PostgreSQL!
conn.commit()
cur.close()
conn.close()

exit(0)
