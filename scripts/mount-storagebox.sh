#!/bin/bash
# Wrapper script for mounting Storage Box via WebDAV
# Used by systemd service

set -e

STORAGE_BOX_URL="https://u526046.your-storagebox.de"
MOUNT_POINT="/mnt/storagebox"
CREDENTIALS_FILE="/root/.davfs2_secrets"

# Read credentials from file
if [ -f "$CREDENTIALS_FILE" ]; then
    USERNAME=$(grep "$STORAGE_BOX_URL" "$CREDENTIALS_FILE" | awk '{print $2}')
    PASSWORD=$(grep "$STORAGE_BOX_URL" "$CREDENTIALS_FILE" | awk '{print $3}')
else
    echo "Error: Credentials file not found: $CREDENTIALS_FILE" >&2
    exit 1
fi

# Mount using credentials
# Use printf to avoid redirection override issue with pipe
printf '%s\n%s\n' "$USERNAME" "$PASSWORD" | mount.davfs "$STORAGE_BOX_URL" "$MOUNT_POINT" \
    -o uid=1000,gid=1000,file_mode=0770,dir_mode=0770,noexec,nosuid,nodev

exit $?
