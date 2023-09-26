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

echo "Install photobooth-wifi-setup systemd"

LAUNCH_SCRIPT=wifi-setup.py

chmod +x $LAUNCH_SCRIPT

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd $DIR

echo "Entry point: $DIR/$LAUNCH_SCRIPT"

sudo cat << EOF > /lib/systemd/system/photobooth-wifi-setup.service
[Unit]
Description=Run photobooth wifi setup
After=multi-user.target
After=graphical.target
[Service]
User=pi
Restart=always
RestartSec=60s
WorkingDirectory=$DIR
ExecStart=$DIR/$LAUNCH_SCRIPT
[Install]
WantedBy=multi-user.target
EOF

echo "Service"
echo "Enable: 'sudo systemctl enable photobooth-wifi-setup.service'"
echo "Start: 'sudo systemctl start photobooth-wifi-setup.service'"
echo "Restart: 'sudo systemctl restart photobooth-wifi-setup.service'"
echo "Reload config: 'sudo systemctl daemon-reload'"
echo "Show logs: 'journalctl -xefu photobooth-wifi-setup.service -b'"