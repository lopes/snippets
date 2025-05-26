#!/bin/sh
#
# Reads a Brazilian "Nota Fiscal Eletrônica" in PDF format,
# figures out what is it competence (the reference in time
# for that document), and then renames the file using this
# data, like: %Y%m[-COUNT].pdf.
#
# Note: the regex may differ according the format used in
# the PDF file (data disposition), so it should be
# adjusted accordingly.
#
# Requires:
#   - pdfgrep
#
# Usage
#   $0 nfe.pdf
#   for i in nfe-*.pdf; do nferen.sh $i; done
#
# Author.: José Lopes <lopes.id>
# Date...: 2021-03-08
# License: MIT
##

NAME="$1"
COMPETENCE="$(pdfgrep -o \[0-9\]\?\[0-9\]\/\[0-9\]\{4\}\ \  "$NAME")"
MONTH="$(echo $COMPETENCE | cut -d "/" -f1 | awk '{printf "%02d\n", $0;}')"
YEAR="$(echo $COMPETENCE | cut -d "/" -f2)"
NEW_NAME="$YEAR$MONTH.pdf"
COUNT=1

while [ -f "$NEW_NAME" ]; do
    NEW_NAME="$YEAR$MONTH-$COUNT.pdf"
    ((COUNT++))
done
mv -v "$NAME" "$NEW_NAME"
