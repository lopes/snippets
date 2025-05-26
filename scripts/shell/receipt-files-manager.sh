#!/bin/bash

# A receipt files' manager.
#
# Author.: Joe Lopes <lopes.id>
# Website: 2013-01-02
# Licence: GPLv3+
##


function main(){
#
# cd to directory ($1) and works there. Reads all items. If its
# a file, then gets its new filename and renames it.
#
    cd "$1"

    for filename in *; do
        if [ -d "$filename" ]; then
            main "$filename"
            cd ..
            continue

        elif [ -f "$filename" ]; then
            local aux=$(new_filename "$filename")
            [ -f $aux ] && aux="C$aux"  # Avoids equal names.
            mv "$filename" $aux
        fi
    done
}

function new_filename(){
#
# Receives the filename in $1 and returns the new filename
# according to the filename modification datetime.
#
# The pattern of return is ISO 8601 compliant:
#     [YYYY][DD][MM]T[hh][mm]Z  <.extension>
#
#TODO Deal with files without extension.
#
    local aux=$(stat --format="%y" "$1" |
                awk '{ print $1 $2 }' |
                sed -e "s/[-:]//g" |
                cut --delimiter="." -f1).$(echo ${1##*.} |
                sed -e "# Lower case
                       y/ABCDEFGHIJKLMNOPQRSTUVWXYZ/abcdefghijklmnopqrstuvwxyz/
                       y/ÀÁÂÃÄÅÈÉÊËÌÍÎÏÒÓÔÕÖÙÚÛÜÇÑ/àáâãäåèéêëìíîïòóôõöùúûüçñ/")
    echo "${aux:0:8}T${aux:8:4}Z${aux:14}"
}


#
# Main
#

if [ -d "$1" ]; then
    main "$1"

elif [ -f "$1" ]; then
    path=${1%/*}
    file=${1##*/}
    [ "$path" == "$file" ] && path="."
    cd "$path"
    mv "$file" "$(new_filename "$file")"

else
    echo "Chloe: Path/File not found - $1"
    exit 1
fi
