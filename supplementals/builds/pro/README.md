# Pro

This is a pro using a raspberry pi 4 with the 10.1inch DSI LCD (C) and standard cam v3 or raspicam HQ.

## Hardware

=> ~ CHF ???

- Raspberry Pi 4 Model B 2GB (CHF 59.90) [link](https://www.pi-shop.ch/raspberry-pi-4-model-b-2gb)
- Raspberry Pi Cam v3 (CHF 25) [link](https://www.digikey.ch/de/products/detail/raspberry-pi/SC0872/17278639?utm_adgroup=General&utm_source=google&utm_medium=cpc&utm_campaign=Shopping_Product_All%20%28Catch-up%29&utm_term=&productid=17278639&utm_content=General&utm_id=go_cmp-17998691427_adg-142975836667_ad-615797033692_aud-555897227485:pla-293946777986_dev-c_ext-_prd-17278639_sig-CjwKCAjw7c2pBhAZEiwA88pOFyZh97S-6Jb-mIY3DETJJ-CZq_M5ywdCyjNMjDoEqsGgxqT2vj3AqhoCuTsQAvD_BwE&gclid=CjwKCAjw7c2pBhAZEiwA88pOFyZh97S-6Jb-mIY3DETJJ-CZq_M5ywdCyjNMjDoEqsGgxqT2vj3AqhoCuTsQAvD_BwE)
- Raspberry Pi HQ Camera (CHF 60.90) [link](https://www.pi-shop.ch/hq-camera)
- Raspberry Pi Lens (CHF 26.20) [link](https://www.digitec.ch/de/s1/product/raspberry-pi-camera-diverse-elektronikmodul-13191781)
- Raspberry Pi Cable (CHF 9.00) [link](https://www.pi-shop.ch/flex-kabel-fuer-das-raspberry-pi-kamera-modul-46cm)
- SanDisk (CHF 9.85) [link](https://www.digitec.ch/de/s1/product/sandisk-ultra-flair-16-gb-usb-a-usb-30-usb-stick-5751581?supplier=406802)
- 10.1inch (CHF 88.90) [link](https://www.pi-shop.ch/10-1inch-capacitive-touch-display-for-raspberry-pi) <https://www.waveshare.com/wiki/10.1inch_DSI_LCD_(C)> [docs](https://www.waveshare.com/wiki/10.1inch_DSI_LCD_(C))
- USB-C Breakout (CHF 4.85) [link](https://www.sparkfun.com/products/15100)
- Magnets 3.5mm x 6mm
- USB-C Breakout (CHF 4.85) [link](https://www.sparkfun.com/products/15100)
- Chinc Plug (CHF 0.25) [link](https://www.berrybase.ch/cinch-einbaubuchse-metallausfuehrung-vergoldet-loetmontage)
- Chinc Connecter (CHF 0.15) [link](https://www.berrybase.ch/cinchstecker-kunststoffausfuehrung-mit-knickschutz-loetmontage)
- Adafruit NeoPixel (CHF 21.65) [link](https://www.adafruit.com/product/3636)
- Adafruit Trinket M0 (CHF 10.80) [link](https://www.adafruit.com/product/3500)
- Level-Shifter (CHF 0.50) [link](https://www.adafruit.com/product/1787)
- Capacitor 500-1000uF
- Resistor 300-500 Ohm
- Push Button

## Installation

### OS: Raspbian Bullseye

Install the 64 bit Raspbian Bullseye OS.

### Display: Waveshare

Follow the setup guide from waveshare [docs](https://www.waveshare.com/wiki/10.1inch_DSI_LCD_(C))

_Brightness control of kernel 6.x is bugged atm. Use the last available for 5.x as workaround._

### Ports

Disable privileged ports for webserver on port 80:

```bash
#save configuration permanently
echo 'net.ipv4.ip_unprivileged_port_start=0' > /etc/sysctl.d/50-unprivileged-ports.conf
#apply conf
sysctl --system
```

### Screensaver

Disable screensaver/screen blanking. By default, Raspbian blanks the screen after ten minutes of idle time.
You probably do not want that for a photobooth, thus it is best to disable this.

Find and change following command `xserver-command` in `/etc/lightdm/lightdm.conf` and change it to: `xserver-command=X -s 0 -dpms`

_You can also do it with `raspi-config` like shown [here](https://pimylifeup.com/raspberry-pi-disable-screen-blanking/)._

### Splash Screen

Remove color splash screen during boot-up as discussed [here](<https://forums.raspberrypi.com/viewtopic.php?t=269406>).

Add `disable_splash=1` at the end of the file `/boot/config.txt`.

### Wifi Configuration

Change WIFI access permissions: `sudo chmod a+w /etc/wpa_supplicant/wpa_supplicant.conf`

Use the installation script to enable automatic wifi configuration:

```bash
./install-systemd.sh
```

The photobooth should now automatically switch between available wifi networks. (Just have a bit of patience ^^)

Don't forget to define the `wifi.json` file with wifi network access:

```json
[
  {
    "ssid": "my-network-1",
    "password": "my-password-1"
  },
  {
    "ssid": "my-network-2",
    "password": "my-password-2"
  }
]
```

_Order the list according to your prioritisation._

### Miscellaneous

Hide the taskbar as discussed [here](<https://raspberrypi.stackexchange.com/questions/8874/how-do-i-auto-hide-the-taskbar>) like following: Panel Settings > Advanced > Minimize panel when not in use

Hide volumes and wastebasket on the desktop by right clicking on desktop and opening the desktop preferences.

Disable [popup](<https://ubuntuforums.org/showthread.php?t=1935099>) when inserting a usb stick like following: `pcmanfm` > edit > preferences > volume management > Untick third box (Show only be necessary when USB Stick is **not yet** inserted at startup)

Set desktop background to: `./media/desktop-bg.png`











TODO: 



Setup cups with the printer: <https://www.elektronik-kompendium.de/sites/raspberry-pi/2007081.htm>
