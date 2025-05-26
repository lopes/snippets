#!/usr/bin/env bash
#
# A backup script to be used with my external HDD.
# Date: 2016-09-07
##
set -euo pipefail  # Bash's strict mode


backup_dirs="Documents Movies Music Pictures Public"

os="$(uname -s)"
logfile="/tmp/${0}-$(date -u +"%Y-%m-%d").log"
usage="
USAGE: ${0} [OPTIONS]
OPTIONS
 -h, --help             Display this message and exit
 -s, --sync [TARGET]    Backup to [TARGET]
 -c, --clean [TARGET]   Delete junk files in [TARGET]
 -e, --eject [DEVICE]   Eject VeraCrypt container and external disk

EXAMPLES
 \$ ${0} -s /Volumes/lopes -c /Volumes/lopes -e /dev/disk2s1
 \$ ${0} -s /Volumes/lopes
 \$ ${0} -c /Volumes/lopes -e /dev/disk2s1
"


sync() {
    # USAGE: sync $backup_dirs
    # rsync options:
    # -a: archive mode
    # -H: preserve hard-links
    # -h: human readable numbers
    # -x: don't cross file system boundaries
    # -v: increase verbosity
    # --numeric-ids: don't map UID/GID values
    # --delete: delete extraneous files from destination directories
    # --progress: show progress during transfer
    # --stats: print statistics
    # --exclude: files to avoid syncing
    # --out-format: output format
    # --log-file-format: as it says
    # --log-file: one log file to rule'em all
    ##
    while [ -n "${1:-}" ]; do
        logger "info" "Syncing $1 -> $sync_target"
        rsync -aHhxv --numeric-ids --delete --progress --stats \
            --exclude=".DS_Store" --exclude=".fseventsd" \
            --exclude=".Spotlight-V100" --exclude=".Trashes" \
            --exclude=".com.apple*" --exclude="._*" \
            --out-format="RSYNC: %f %b bytes" \
            --log-file-format="RSYNC: %f %b bytes" --log-file="$logfile" \
            "$1" \
            "$sync_target"
        shift
    done
}

clean() {
    logger "info" "Cleaning $1"
    find "$1" \( -name ".DS_Store" -o -name ".fseventsd" \
        -o -name ".Spotlight-V100" -o -name ".Trashes" -o -name ".com.apple*" \
        -o -name "._*" \) -exec rm -rf {} \;
}

eject() {
    case "$os" in
        "Linux")
            logger "info" "Unmounting encrypted containers"
            veracrypt -d
            logger "info" "Unmounting disk $1"
            unmount "$1"
            ;;
        "Darwin")  # Mac
            logger "info" "Unmounting encrypted containers"
            /Applications/VeraCrypt.app/Contents/MacOS/VeraCrypt -d
            logger "info" "Unmounting disk $1"
            diskutil unmount "$1"  #/dev/disk2s1
            ;;
        *)
            logger "error" "Unsuportted operating system: $os"
            exit 1
            ;;
    esac
}

logger() {
    # USAGE: logger LEVEL MESSAGE
    iso8601utc="$(date -u +"%Y%m%dT%H%M%SZ")"
    case "$1" in
        "info") log="$iso8601utc  INFO: $2" ;;
        "warning") log="$iso8601utc  WARNING: $2" ;;
        *)
            log="$iso8601utc  ERROR: Unrecognized log level: $1"
            exit 1
            ;;
    esac
    echo "$log" |tee -a "$logfile"
}


##
# MAIN
# Processing args.
while [ -n "${1:-}" ]; do
    case "${1:-}" in
        -s | --sync) shift; sync_target="$1" ;;
        -c | --clean) shift; clean_target="$1" ;;
        -e | --eject) shift; eject_target="$1" ;;
        -h | --help) echo "$usage"; exit 0 ;;
        *) echo "$usage"; exit 1 ;;
    esac
    shift
done

cd ~

if [ -n "${sync_target:-}" ]; then
    # TODO: test if $sync_target exists and is writable
    sync $backup_dirs  # do not use double quotes here!
fi

if [ -n "${clean_target:-}" ]; then
    # TODO: test if $clean_target exists and is writable
    clean "$clean_target"
fi

if [ -n "${eject_target:-}" ]; then
    # TODO: test if $eject_target exists and is unmountable
    eject "$eject_target"
fi
