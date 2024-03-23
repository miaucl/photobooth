#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "Executing deploy script: $SCRIPT_DIR"

if [ -z "$1" ]; then
  echo "First argument has not been supplied and should be the address of the host"
  exit 1
fi

HOST=$1
SSH_USER="${2:-pi}"
TARGET="${3:-'photobooth'}"
SOURCE="$SCRIPT_DIR/../../../"

echo "Deploying on host $HOST as $SSH_USER to $TARGET"

if -z "ping -c1 -W1 $HOST" &> /dev/null; then
  echo Could not reach $HOST
  exit 1
fi

rsync -azP ${SOURCE}photobooth ${SOURCE}supplementals ${SOURCE}*.sh ${SOURCE}photobooth.cfg $SSH_USER@$HOST:$TARGET

ssh $SSH_USER@$HOST "sudo systemctl restart photobooth"

echo "Deployment successful, restarting now ..."