#!/bin/bash
#
# Zips and crypts a directory.
#
# TODO
#   - Ask confirmation before delete.
#
# DATE: 2015-03-27
##

OUTPUT="$(basename $(pwd))"  #current dirname

cd ..
tar -czvf "${OUTPUT}.tgz" "${OUTPUT}"
gpg --symmetric --cipher-algo aes256 "${OUTPUT}.tgz"

if [ "$?" == "0" ]; then
    rm -rf "${OUTPUT}.tgz"
    echo "REMEMBER TO DELETE THE ORIGINAL FILES!"
fi

exit $?
