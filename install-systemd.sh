#!/bin/bash
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2023  <photobooth-lausanne at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

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

echo "Enable: 'sudo systemctl enable photobooth.service'"
echo "Start: 'sudo systemctl start photobooth.service'"
echo "Restart: 'sudo systemctl restart photobooth.service'"
echo "Reload config: 'sudo systemctl daemon-reload'"
echo "Show logs: 'journalctl -xefu photobooth.service -b'"
