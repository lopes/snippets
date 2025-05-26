#!/bin/bash

# A DNS propagation checker. Fetches in many DNS servers around
# the world for IPs assigned to a given domain.
#
# Author: Joe Lopes <lopes.id>
# Date: 2013-01-02
#
#TODO: - Add more DNS servers around the world.


#
# Global Variables
#

DOMAIN=""
REGEX="^[a-zA-Z0-9\.-]*(.com|.net|.org|.gov|.br|.es|.uk)$"

# Adding more servers
# The variable which stores IPs uses spaces as
# delimiter. That which stores names uses sem-
# icolons.
#
# Remember that the N'th IP corresponds to the
# N'th name. So, be careful when editing this,
# to avoid mistakes.
SERVERIPS="8.8.8.8 208.67.222.222 68.94.156.1 4.2.2.1 203.23.236.66
           202.83.95.227 189.38.95.95 200.221.11.100 202.27.158.40
           212.158.248.5"
SERVERNAMES="[US] Google Public DNS;[US] OpenDNS;[US] AT&T;[US] Level 3;
             [AU] Comcel;[AU] OpenNIC;[BR] GigaDNS;[BR] Universo Online (UOL);
             [NZ] Xtra;[UK] Bulldog Broadband"

USAGE="
USAGE: "${0##*/}" DOMAIN

EXAMPLE
 $ ./"${0##*/}" joselop.es

NOTE
 DOMAIN MUST be a valid domain like www.joselop.es or
 joselop.es. Do NOT use \"http://\" (or something like)
 as prefix.
"

#
# Functions
#

main(){
#
# Iterates over IPs list, getting the respective server name and
# checking what is the IP of $DOMAIN in that server.
#
    local ip
    local name

    # Output's header
    printf "%-30s %15s\n" "     DNS SERVER" "ASSOCIATED IP"
    echo "     ========================= ==============="

    # For each IP, gets its server name,
    # updates server name's list and
    # figure out the IP for $DOMAIN in
    # that DNS server.
    for ip in $SERVERIPS; do
        name="$(echo $SERVERNAMES | cut -d\; -f1)"
        SERVERNAMES="$(echo $SERVERNAMES | cut -d\; -f2-)"

        printf "%-30s %15s\n" "$name" "$(answer "$ip" "$DOMAIN")"
    done

    return $?
}

answer(){
#
# This is the program's core system.
# Receives DNS's IP and Domain through $1 and $2.
# Returns the IP associated to that Domain.
#
    dig @"$1" "$2" | grep -a1 "ANSWER SECTION" | tail -1 | awk '{print $NF}'
}

registers(){
#
# Displays all DNS servers used in Puck, with its IP addresses.
#
    local ip
    local name

    # Output's header
    printf "%-30s %15s\n" "     DNS SERVER" "IP ADDRESS"
    echo "     ========================= ==============="

    for ip in $SERVERIPS; do
        name="$(echo $SERVERNAMES | cut -d\; -f1)"
        SERVERNAMES="$(echo $SERVERNAMES | cut -d\; -f2-)"

        printf "%-30s %15s\n" "$name" "$ip"
    done

    return $?
}


#
# Main
#

if [ $# -gt "0" ]; then
    DOMAIN="$1"
else
    echo -n "Domain: "
    read -r
    DOMAIN="$REPLY"
fi

if [[ $DOMAIN =~ $REGEX ]]; then
    if ping -c 1 $DOMAIN > /dev/null 2>&1; then
        main
        exit $?
    else
        echo -e "\n$DOMAIN is offline or there is a problem with your link."
        echo -e "Check out this issue and try again.\n"
        exit 2
    fi
else
    echo "$USAGE"
    exit 1
fi
