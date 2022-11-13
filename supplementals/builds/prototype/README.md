# Prototype

This is a prototype using a raspberry 4 which the official touch screen and standard cam.

## Hardware

- Raspberry Pi 4 (2GB)
- Official Raspberry Pi Touch Screen
- Raspberry Pi Camera v2

## OS: Raspbian Bullseye

Setup cups with the printer: <https://www.elektronik-kompendium.de/sites/raspberry-pi/2007081.htm>

Set desktop background to: `./media/desktop-bg.png`

Disable screensaver/screen blanking. By default, Raspbian blanks the screen after ten minutes of idle time.
You probably do not want that for a photobooth, thus it is best to disable this.

> Option 1: Do it either in the GUI or with `raspi-config`. [source](https://pimylifeup.com/raspberry-pi-disable-screen-blanking/)
> Option 2: For that, edit `/etc/lightdm/lightdm.conf` and change the startup command to the following: `xserver-command=X -s 0 -dpms`

Change brightness of screen for official touch screen with following tool: [https://pypi.org/project/rpi-backlight/]

Remove color splash screen during boot-up: <https://forums.raspberrypi.com/viewtopic.php?t=269406>

> Open `/boot/config.txt`
> Add:
> disable_splash=1

Add custom startup splash: <https://www.tomshardware.com/how-to/custom-raspberry-pi-splash-screen>

> Replace `./media/splash.png` in folder `/usr/share/plymouth/themes/pix/splash.png`

Hide boot messages: <https://scribles.net/silent-boot-up-on-raspbian-stretch/>

> `sudo systemctl mask plymouth-start.service`

Hide blinking cursor:

> Open `/boot/cmdline.txt`
> Add:
> vt.global_cursor_default=0

Hide the taskbar: <https://raspberrypi.stackexchange.com/questions/8874/how-do-i-auto-hide-the-taskbar>

Hide the mouse cursor when not moving: <https://forums.raspberrypi.com/viewtopic.php?t=234879>

> Install `sudo apt install unclutter`
> Open `/etc/xdg/lxsession/LXDE-pi/autostart`
>Add `unclutter -idle 0.01`

Disable popup when inserting a usb stick: <https://ubuntuforums.org/showthread.php?t=1935099>

`pcmanfm` > edit > preferences > volume management

Hide volumes and wastebasket on the desktop by right clicking on desktop and go to desktop preferences.

Rotate the default orientation to portrait in the settings. (left)
