# Internet via SIM Card

To provide the photobooth with internet using mobile data and a SIM card, following stick can be used.

Surf Stick: E3372-325

## Setup Device

Connect the Stick and check if it is detected

```bash
sudo apt install usb-modeswitch ppp wvdial
sudo reboot
lsusb
```

## Setup Connection

Find the device following command

```bash
dmesg
```

and look for something like

```log
[    6.665092] usb 1-1.2.3: New USB device found, idVendor=3566, idProduct=2001, bcdDevice=ff.ff
[    6.665170] usb 1-1.2.3: New USB device strings: Mfr=2, Product=3, SerialNumber=4
[    6.665188] usb 1-1.2.3: Product: Mobile
[    6.665202] usb 1-1.2.3: Manufacturer: Mobile
[    6.665224] usb 1-1.2.3: SerialNumber: 123456789ABCD
[    6.680003] Console: switching to colour dummy device 80x25
[    6.748598] usb-storage 1-1.2.3:1.0: USB Mass Storage device detected
[    6.811035] scsi host0: usb-storage 1-1.2.3:1.0
[    6.814079] vc4-drm gpu: bound fe400000.hvs (ops vc4_hvs_ops [vc4])
[    6.851210] Registered IR keymap rc-cec
[    6.855961] rc rc0: vc4-hdmi-0 as /devices/platform/soc/fef00700.hdmi/rc/rc0
```

Good, the device is connected, but you will not see an interface with `ifconfig -a`

Know to set it up, place the magic file `40-huawei.rules` at `/etc/udev/rules.d/40-huawei.rules`

Reboot and hope for the best!

### If it works, it should look like this

Output of `dmesg`

```log
[   82.358589] usb 1-1.2.3: new high-speed USB device number 6 using xhci_hcd
[   82.472342] usb 1-1.2.3: New USB device found, idVendor=3566, idProduct=2001, bcdDevice=ff.ff
[   82.472376] usb 1-1.2.3: New USB device strings: Mfr=2, Product=3, SerialNumber=4
[   82.472393] usb 1-1.2.3: Product: Mobile
[   82.472408] usb 1-1.2.3: Manufacturer: Mobile
[   82.472421] usb 1-1.2.3: SerialNumber: 123456789ABCD
[   83.678918] usb 1-1.2.3: reset high-speed USB device number 6 using xhci_hcd
[   84.902847] usb 1-1.2.3: reset high-speed USB device number 6 using xhci_hcd
[   85.016281] usb 1-1.2.3: device firmware changed
[   85.023050] usb 1-1.2.3: USB disconnect, device number 6
[   85.024798] usbcore: registered new interface driver cdc_ether
[   85.028592] usbcore: registered new interface driver rndis_host
[   86.186461] usb 1-1.2.3: new high-speed USB device number 7 using xhci_hcd
[   86.300021] usb 1-1.2.3: New USB device found, idVendor=3566, idProduct=2001, bcdDevice=ff.ff
[   86.300035] usb 1-1.2.3: New USB device strings: Mfr=2, Product=3, SerialNumber=4
[   86.300041] usb 1-1.2.3: Product: Mobile
[   86.300046] usb 1-1.2.3: Manufacturer: Mobile
[   86.300050] usb 1-1.2.3: SerialNumber: 123456789ABCD
[   86.307510] rndis_host 1-1.2.3:1.0 usb0: register 'rndis_host' at usb-0000:01:00.0-1.2.3, RNDIS device, 62:09:57:00:7f:ee
[   87.352392] rndis_host 1-1.2.3:1.0 usb0: unregister 'rndis_host' usb-0000:01:00.0-1.2.3, RNDIS device
[   87.458799] usb 1-1.2.3: reset high-speed USB device number 7 using xhci_hcd
[   87.575569] rndis_host 1-1.2.3:1.0 usb0: register 'rndis_host' at usb-0000:01:00.0-1.2.3, RNDIS device, 62:09:57:00:7f:ee
[   88.628988] rndis_host 1-1.2.3:1.0 usb0: unregister 'rndis_host' usb-0000:01:00.0-1.2.3, RNDIS device
[   88.747072] usb 1-1.2.3: reset high-speed USB device number 7 using xhci_hcd
[   88.863620] rndis_host 1-1.2.3:1.0 usb0: register 'rndis_host' at usb-0000:01:00.0-1.2.3, RNDIS device, 62:09:57:00:7f:ee
```

### If it does not work, good may help you

Consult the internet ;)

## Misc

When you plug the usb device in, after the pi has started, it usually just works. But if it is connected, sometimes it stays in default mode and `usb_modeswitch` is needed to kick things off. To do so, following script `setup.sh` can be installed at `/etc/huawei_brovi/setup.sh` called with a `1m` period in the cron tab of the pi. It does not hurt when everything is already set up and it keeps running, just make sure it is executable.

```txt
* * * * * /etc/huawei_brovi/setup.sh
```

### Sources

Sources:

- <https://raspberry.tips/raspberrypi-tutorials/usb-surfstick-am-raspberry-pi-verwenden-mobiles-internet>
- <https://unix.stackexchange.com/questions/733971/usb-lte-modem-brovi-e3372-325-not-working>
- <https://www.draisberghof.de/usb_modeswitch/bb/viewtopic.php?f=3&t=3043&p=20026#p20054>
