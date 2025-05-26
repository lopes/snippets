#!/bin/bash
#
# It will catch all of your network interfaces and
# find out what's the manufacturer of each according
# to its OUI.
#
# Joe Lopes <lopes.id>
# GPLv3
# 2013-01-24
##

NICS="$(ifconfig -a |grep -v "^ " \
                    |sed -e '/^$/d; /^lo/d' \
                    |cut -d ' ' -f1 \
                    |tr '\n' ' ')"
MANU=""
SITE="$(curl -s http://standards.ieee.org/develop/regauth/oui/oui.txt)"

for nic in $NICS; do
    MANU="$MANU $(echo "$SITE" |grep "$(ifconfig |grep HWaddr \
                                            |sed -e "s/^.*HWaddr //; s/:/-/g" \
                                            |cut -c-8)" \
                               |cut -f3)"
done

echo -e NICs.........: $NICS
echo -e Manufacturers: $MANU

exit 0
