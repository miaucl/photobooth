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

# Import all connections
with open('wifi.json') as f:
   wifi_list = json.load(f)

# Iterate through all 
for wifi in wifi_list:
    # Check for active WIFI connection already
    ps = subprocess.Popen(['iwconfig'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
        print(output)
        time.sleep(60) # If connection found, check every minute
        break # Start over

    except subprocess.CalledProcessError:
        # grep did not match any lines
        print("No wireless networks connected")

        ssid = wifi["ssid"]
        password = wifi["password"]

        print(f"Trying to connect to wifi: {ssid}")

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

        print("Wifi config added. Refreshing configs")
        ## refresh configs
        os.popen("sudo wpa_cli -i wlan0 reconfigure")