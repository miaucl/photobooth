# Prototype

## Hardware

- Raspberry Pi 4 (2GB)
- Official Raspberry Pi Touch Screen
- Raspberry Pi Camera v2

## Software

### OS: Raspbian Bullseye

Settings:

Change brightness of screen for official touch screen with following tool: [https://pypi.org/project/rpi-backlight/]

Remove color splash screen during bootup: https://forums.raspberrypi.com/viewtopic.php?t=269406

> Open `/boot/config.txt`
> Add:
> disable_splash=1

Remove logs on screen: https://ananddrs.com/2013/09/18/rpi-hide-boot-msg/

> Open `/boot/cmdline.txt`
> Add:
> console=tty3
> loglevel=3

Add custom startup splash: https://www.tomshardware.com/how-to/custom-raspberry-pi-splash-screen

> Replace `splash.png` in folder `/usr/share/plymouth/themes/pix/`

Hide the taskbar: https://raspberrypi.stackexchange.com/questions/8874/how-do-i-auto-hide-the-taskbar

Hide the mouse cursor when not moving: https://forums.raspberrypi.com/viewtopic.php?t=234879

> Use `unclutter -idle 0.01`

Disable popup when inserting a usb stick: https://ubuntuforums.org/showthread.php?t=1935099

Hide volumes on the desktop by right clicking on desktop and go to desktop preferences.
