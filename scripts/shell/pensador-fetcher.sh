#!/bin/bash

# Retrieves the last @pensador's tweet.  Manages it retrieving one
# tweet per day, by using a file to cache the quote.
#
# Joe Lopes <lopes.id>
# GPLv3+
# 2013-01-02
##


#
# Global Variables
#
TODAY=$(date +%Y%m%d)
FILE="$HOME/.pensador"


file_feed(){
#
# Feeds the file with a new quote.
# If the new quote is equal to the old, do nothing.
#
    local quot=$(get_tweet)
    [ -z "$quot" ] && return 1
    [ "$quot" != "$(file_get_quot)" ] && echo -e "$TODAY\n$quot" > $FILE
    return $?
}

#
# Retrives the date and the quote from the file.
#
file_get_date(){ head -n 1 $FILE; }
file_get_quot(){ echo; tail -1 $FILE; echo; }

get_tweet(){
#
# Gets the @pensador's last tweet.
#
    local url="http://twitter.com/statuses/user_timeline/25989479.rss"

    curl -s --connect-timeout 5 "$url" |
    grep -m 2 "<description>" |
    tail -1 |
    cut -d ":" -f2- |
    sed -e "# Removes spaces at the begin
            s/^ *//

            # Formats the end
            s/<\/description>$/ --@pensador/

            # ISO 8859-1 Characters - Substitution
            s/&#192;/À/g; s/&#193;/Á/g; s/&#194;/Â/g; s/&#195;/Ã/g;
            s/&#196;/Ä/g; s/&#197;/Å/g; s/&#198;/Æ/g; s/&#199;/Ç/g;
            s/&#200;/È/g; s/&#201;/É/g; s/&#202;/Ê/g; s/&#203;/Ë/g;
            s/&#204;/Ì/g; s/&#205;/Í/g; s/&#206;/Î/g; s/&#207;/Ï/g;
            s/&#208;/Ð/g; s/&#209;/Ñ/g; s/&#210;/Ò/g; s/&#211;/Ó/g;
            s/&#212;/Ô/g; s/&#213;/Õ/g; s/&#214;/Ö/g; s/&#216;/Ø/g;
            s/&#217;/Ù/g; s/&#218;/Ú/g; s/&#219;/Û/g; s/&#220;/Ü/g;
            s/&#221;/Ý/g; s/&#222;/Þ/g; s/&#223;/ß/g; s/&#224;/à/g;
            s/&#225;/á/g; s/&#226;/â/g; s/&#227;/ã/g; s/&#228;/ä/g;
            s/&#229;/å/g; s/&#230;/æ/g; s/&#231;/ç/g; s/&#232;/è/g;
            s/&#233;/é/g; s/&#234;/ê/g; s/&#235;/ë/g; s/&#236;/ì/g;
            s/&#237;/í/g; s/&#238;/î/g; s/&#239;/ï/g; s/&#240;/ð/g;
            s/&#241;/ñ/g; s/&#242;/ò/g; s/&#243;/ó/g; s/&#244;/ô/g;
            s/&#245;/õ/g; s/&#246;/ö/g; s/&#248;/ø/g; s/&#249;/ù/g;
            s/&#250;/ú/g; s/&#251;/û/g; s/&#252;/ü/g; s/&#253;/ý/g;
            s/&#254;/þ/g; s/&#255;/ÿ/g"
}


#
# Main
#
default="19700101\nA natureza detesta o vazio. --Blaise Pascal"
[ -f "$FILE" ] || echo -e "$default" > $FILE
[ "$TODAY" != "$(file_get_date)" ] && file_feed
file_get_quot

exit $?
