# Classic

This is a classic using a raspberry pi zero 2 which the 7inch QLED Integrated Display and standard cam v2.

## Hardware

- Raspberry Pi Zero 2
- Raspberry Pi Camera v2
- 7inch QLED Integrated Display ([Docs](https://www.waveshare.com/wiki/70H-1024600#CAD_Drawing))
- Switch [link](https://www.digikey.com/en/products/detail/zf-electronics/CRE22F2BBBNE/446064)
- IRM 30 5ST [link](https://www.meanwell-web.com/en-gb/ac-dc-single-output-encapsulated-power-supply-irm--30--5st)
- LogiLink Smile [link](https://www.digitec.ch/de/s1/product/logilink-smile-usb-a-dockingstation-usb-hub-12776233?dbq=1&gclid=Cj0KCQiAsoycBhC6ARIsAPPbeLuSqziMTKka5bsK8nV0Phmgn8bYfRX4SiDYr0Et2__k1bhvytIP0LkaAnqcEALw_wcB&gclsrc=aw.ds)
- IEC Gerätestecker C14, 250V [link](https://ch.schurter.com/de/datasheet/6100-3#)
- GU10 Fassung [link](https://www.distrelec.ch/de/fassung-gu10-2a-250v-keramik-weiss-bailey-lights-141234/p/30148723?trackQuery=gu10+fassung&pos=1&origPos=1&origPageSize=50&track=true)
- LED spot VLE D 4.9-50W GU10 [link](https://www.lighting.philips.ch/prof/led-lampen-und-roehren/led-reflektorlampen/master-ledspot-value-gu10-hochvolt-reflektorlampen/929001349102_EU/product) 

## OS: Raspbian Bullseye

Setup the display with following guide: <https://www.waveshare.com/wiki/70H-1024600#Structure_Design>

> Add following to `config.txt` of the SD Card:

```txt
hdmi_group=2
hdmi_mode=87
hdmi_cvt 1024 600 60 6 0 0 0
hdmi_drive=1
```

Rotate the screen and touch

> Add `xrandr --output HDMI-1 --rotate right` to `/etc/xdg/lxsession/LXDE-pi/autostart`
> Follow: <https://www.waveshare.com/w/upload/1/19/7inch_HDMI_LCD_%28B%29_User_Manual.pdf>

Rotate the touch: <https://www.waveshare.com/wiki/7inch_HDMI_LCD#Touch_calibration>

> Run `sudo apt-get install xserver-xorg-input-evdev xinput-calibrator`
> Copy `sudo cp -rf /usr/share/X11/xorg.conf.d/10-evdev.conf /usr/share/X11/xorg.conf.d/45-evdev.conf`
> Run touch calibration
> Add result to `/usr/share/X11/xorg.conf.d/99-calibration.conf` (example for right):

```txt
#touch rotate 0 degrees (X=0):
Section "InputClass"
        Identifier      "calibration"
        MatchProduct    "WaveShare WS170120"
        Option  "Calibration"   "855 836 173 176"
        Option  "SwapAxes"      "1"
        Option "EmulateThirdButton" "1"
        Option "EmulateThirdButtonTimeout" "1000"
        Option "EmulateThirdButtonMoveThreshold" "300"
EndSection
```

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

Connect raspberry to printer network

TODO: stats
