#/bin/sh
#
# Packs and unpacks sensitive data in a more secure fashion.
# Read $HELP for usage tips.
#
# Author: José Lopes <lopes.id>
# License: MIT
# Date: 2021-09-28
##

HELP="
USAGE
${0} <encrypt|decrypt> [file.txt|directory|file.txt.tgz.gpg]
${0} [--help|-h]

EXAMPLES
${0} enc passwords.json          # create: passwords.json.tgz.gpg
${0} enc mfa                     # create: mfa.tgz.gpg
${0} dec passwords.json.tgz.gpg  # decrypt and extract passwords.json
${0} dec mfa.tgz.gpg             # decrypt and extract mfa directory
"
ERROR="
Invalid command: \"$1\"
Use --help for usage tips
"

function encrypt(){
    echo "Packing up data..."; tar -czvf "$1.tgz" "$1"
    echo "Encrypting data..."; gpg --symmetric --cipher-algo aes256 "$1.tgz"
    echo "Removing unencrypted data..."; rm -rf "$1" "$1.tgz"
}

function decrypt(){
    echo "Decrypting data..."; gpg -o "${1%.*}" --decrypt "$1"
    echo "Unpacking data..."; tar -xzvf "${1%.*}"
    echo "Removing garbage..."; rm -rf "$1" "${1%.*}"
}

case "$1" in
    "--help"  | "-h")  echo "$HELP"; exit 0 ;;
    "encrypt" | "enc") encrypt "$2" ;;
    "decrypt" | "dec") decrypt "$2" ;;
    *) echo "$ERROR" ;;
esac
