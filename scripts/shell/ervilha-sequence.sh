#!/bin/bash
#
# Displays the sequence until its Nth item, passed through $1.
# The sequence starts with 1 and its next item will be given
# by the read of the current item.
# For exemple, if the 4th item is 1211 --three one and one
# two--, the 5th item will be 3112.
#
# Author.: Joe Lopes <lopes.id>
# Licence: GPLv3+
# Date: 2013-01-09
##

max=$1  # Must be an integer > 0.
item="1"  # First sequence's item.

for ((count=1; count <= max; count++)); do
    echo $item
    aux=$item
    item=""

    while [[ ${#aux} -gt 0 ]]; do
        num=${aux:0:1}  # Get the first number.
        # How many times does the number repeat in item?
        repeat=$(echo $(($(echo $aux | sed "s/[^$num]//g" | wc -m)-1)))
        item="$item$repeat$num"  # Build next item
        aux=${aux//$num/}  # Delete all occurrences of $num in $aux.
    done
done
