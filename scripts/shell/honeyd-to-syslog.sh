#!/bin/ksh
#
# Parses honeyd logfiles to syslog and sends them to a SIEM.
# This script is compatible with OpenBSD 6.4 and ksh.  If
# you're running in Linux/Bash, the commands below should help:
#
# YESTERDAY="$(date -u +"%Y-%m-%d" -d "yesterday")"
#
# Deploy: simply edit global variables according to your
# environment, give this file 0755 permissions, and
# edit crontab to run it periodicaly.  Then, add these
# lines to /etc/syslog.conf (change x.x.x.x for your
# SIEM address):
#
# !!logger
# *.*   @tls://x.x.x.x
# !*
#
# Author: Joe Lopes <lopes.id>
# License: MIT
# Date: 2019-03-15
##


INPATH="/path/to/log"
OUTPATH="/path/to/aux/dir"
YESTERDAY="$(date -r "$(expr $(date +%s) - 86400)" "+%Y-%m-%d")"
YEAR="$(echo $YESTERDAY | cut -d"-" -f 1)"


syslogger() {
    # $1: listener subdirectory
    # $2: listener prefix
    # $3: file filter
    in="$INPATH/$1/$YEAR/$2.$YESTERDAY"
    out="$OUTPATH/$2.$YESTERDAY"
    test -e "$in" && \
        egrep "$3" "$in" > "$out" && \
        logger -i -t logger -f "$out" && \
        rm -f "$out"
}


syslogger "directory_1" "file_prefix_a" ""
syslogger "directory_2" "file_prefix_b" "(regex|optional)"
