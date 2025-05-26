#!/bin/bash
#
# A deprecated IPv4 war dialer--more like an example on
# how to make bitwise operations in Bash.
#
# DATE: 2013-01-02
##

str2int(){
    local octet int=0
    for octet in $(echo $1 | tr "." " "); do
        int=$((int << 8))
        int=$((int + octet))
    done
    echo $int
}

int2str(){
    local octets int=$1
    for index in 1 2 3 4; do
        octets="$((int & 255)) $octets"
        int=$((int >> 8))
    done
    echo $octets | tr " " "."
}


ADDR_STR=$1
ADDR_INT=$(str2int "$1")

for ((index=$ADDR_INT; index < 4294967295; ++index)); do
   ADDR_STR=$(int2str $index)
   echo -n "$ADDR_STR - "
   pingy=$(ping -c 3 $ADDR_STR 2>1)
   echo "OK"
done
