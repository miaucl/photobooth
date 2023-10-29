#!/usr/bin/env python3
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

# RPI wifi setup

import os
import json
import subprocess
import time

RECONFIGURE_DELAY = 15 #s
INITIALIZED_FLAG = '/tmp/photobooth-wifi-setup-initialized'

# Import all connections
with open('wifi.json') as f:
   wifi_list = json.load(f)

# Check for active WIFI connection
def check_connection():
    ps = subprocess.Popen(['iwconfig'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        output = str(subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout))
        print(output, flush=True)

        return ("ESSID:off" not in output)
            

    except subprocess.CalledProcessError:
        print("Subprocess error")
        return False

# Check initialized flag
if os.path.isfile(INITIALIZED_FLAG):
    # If connection found, abort and wait for next check cycle
    if check_connection():
        exit(0)
else:
    # Create the initialized flag
    try:
        open(INITIALIZED_FLAG, 'a').close()
    except OSError:
        print(f"Failed creating the file: {INITIALIZED_FLAG}", flush=True)
    else:
        print(f"File created: {INITIALIZED_FLAG}", flush=True)

# Iterate through all possible wifi connections
for wifi in wifi_list:
    # grep did not match any lines
    print("No wireless networks connected")

    ssid = wifi["ssid"]
    password = wifi["password"]

    print(f"Trying to connect to wifi: {ssid}", flush=True)

    config_lines = [
        'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev',
        'update_config=1',
        'country=CH',
        '\n',
        'network={',
        '\tssid="{}"'.format(ssid),
        '\tpsk="{}"'.format(password),
        '}'
    ]
    config = '\n'.join(config_lines)

    # writing to file (might need allow access once: 'sudo chmod a+w /etc/wpa_supplicant/wpa_supplicant.conf')
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
        f.write(config)

    print("Wifi config added. Refreshing configs", flush=True)
    # refresh configs
    os.popen("wpa_cli -i wlan0 reconfigure")
    # wait before checking
    time.sleep(RECONFIGURE_DELAY)
    # Exit if new connect established
    if check_connection():
        exit(0)
else:
    # Exit and wait for next cycle
    print("None of the configured wifi options was successful", flush=True)
    exit(1)