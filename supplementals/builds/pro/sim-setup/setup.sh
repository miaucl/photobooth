#!/bin/bash
/usr/sbin/usb_modeswitch -v  3566 -p 2001  -X
/usr/sbin/modprobe option
echo  3566 2001 ff > /sys/bus/usb-serial/drivers/option1/new_id
ls -la /dev/ttyUSB4| grep dialout && {
    echo AT^RESET > /dev/ttyUSB4
    timeout 2 cat /dev/ttyUSB4
    }