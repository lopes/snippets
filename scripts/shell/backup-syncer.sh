#!/bin/bash
#
# Syncs backups from different servers in a single
# place, using rsync.  This "single place", in this
# case is a shared folder in a Windows 2008 system.
# So, we have to mount it using Samba first.
#
# AUTHOR.: Joe Lopes <lopes.id>
# LICENSE: GPLv3+
# DATE: 2013-04-03
##

BKP_PATH="$HOME/Public/backups-servers"

# Is file server mounted?
while [ ! -e "$BKP_PATH" ]; do
    read -sp "AD password for user service: " pass
    sudo mount -t smbfs \
               -o username=service,password="$pass",uid=1000,gid=1000 \
               //10.0.1.2/files \
               "$HOME/Public"
done
echo  # Next line, please.

# Sync backups.
echo "PIRANHA"; rsync -avz root@10.0.1.1:/var/local/piranha \
                      --delete-after \
                      "$BKP_PATH"
echo "TRAIRA";  rsync -e "ssh -p 2222" \
                      -avz lopes@10.0.1.3:/var/local/traira \
                      --delete-after \
                      "$BKP_PATH"
echo "AGULHA";  rsync -e "ssh -p 2222" \
                      -avz lopes@10.0.1.4:/var/local/agulha \
                      --delete-after \
                      "$BKP_PATH"
