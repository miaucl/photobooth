#!/bin/bash

set -e

LANG=C

echo "Install photobooth systemd"

LAUNCH_SCRIPT=autousb.sh

chmod +x $LAUNCH_SCRIPT

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd $DIR

echo "Entry point: $DIR/$LAUNCH_SCRIPT"

sudo cat << EOF > /lib/systemd/system/photobooth.service
[Unit]
Description=Run photobooth
After=multi-user.target
After=graphical.target
[Service]
User=pi
Restart=on-failure
RestartSec=5s
WorkingDirectory=$DIR
Environment="DISPLAY=:0"
ExecStart=$DIR/$LAUNCH_SCRIPT
ExecStop=/usr/bin/killall -9 $DIR/$LAUNCH_SCRIPT
[Install]
WantedBy=multi-user.target
EOF

systemctl stop photobooth.service
systemctl enable photobooth.service
systemctl daemon-reload photobooth.service
systemctl start photobooth.service

echo "Show logs: 'journalctl -xefu photobooth.service -b'"
