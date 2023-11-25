# Installation instructions

These instructions are tailored towards running the photobooth on a Raspberry Pi (Buster and Bullseye, 4 and 400, though earlier versions were also tested on 1B+ and 3B+), using picamera2 and pycups.

## Install Raspbian and configure it

This is just for my own reference and maybe useful, if you have a similar hardware setup.
Skip this, if you have your hardware already up and running.

### Install Raspbian Desktop

Choose Raspbian Desktop instead of the Lite flavor, which lacks some packages required for the GUI.

Download and installation instructions are available at the [Raspberry Pi website](https://www.raspberrypi.org/documentation/installation/installing-images/)

### Configure and update Raspbian

Boot up the Raspberry Pi for the first time and open a terminal (press Ctrl+Alt+T).
Enter the following to update everything to the latest version:

```bash
sudo apt update
sudo apt upgrade
```

Afterwards, open the configuration utility to adapt everything to your needs (e.g., setup WiFi, hostname, etc.)

```bash
sudo raspi-config
```

### Configure touch screen, printer etc

Configure any not working hardware, e.g., my touch screen needs some additional steps since some of the latest Raspbian releases.
See the instructions at the end for my hardware setup.

If you plan on using a printer, make sure it is configured as default printer!

## Install dependencies for the photobooth

These dependencies are required to run the application.

### Install required packages

In a terminal, enter the following commands

```bash
sudo apt install python3-dev python3-pip virtualenv 
sudo apt install qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools python3-pyqt5 # for PyQt5-GUI
sudo apt install libcups2-dev # to use pycups
sudo apt install python3-picamera2 # to use picamera2
sudo apt install gettext # to add other languages
```

#### Additional requirements for gphoto2

_Alternative setup with gphoto2._

To use `gphoto2` enter following commands:

```bash
sudo apt install gphoto2 libgphoto2-dev # to use gphoto2
```

If you want to use the gphoto2-cffi bindings you have to install the following packages:

```bash
sudo apt install libffi6 libffi-dev # for gphoto2-cffi bindings
```

Remove some files to get gphoto2 working

Raspbian ships with a utility called `gvfs` to allow mounting cameras as virtual file systems.
This enables you to access some camera models as if they were USB storage drives, however, it interferes with our use of the camera, as the operating system then claims exclusive access to the camera.
Thus, we have to disable these functionalities.

*Note: This might break file manager access etc. for some camera models.*

To remove these files, enter the following in a terminal:

```bash
sudo rm /usr/share/dbus-1/services/org.gtk.vfs.GPhoto2VolumeMonitor.service
sudo rm /usr/share/gvfs/mounts/gphoto2.mount
sudo rm /usr/share/gvfs/remote-volume-monitors/gphoto2.mount
sudo rm /usr/lib/gvfs/gvfs-gphoto2-volume-monitor
sudo rm /usr/lib/gvfs/gvfsd-gphoto2
```

You should reboot afterwards to make sure these changes are effective.

## Install photobooth

These are the steps to install the application.

### Clone the Photobooth repository

Run the following command to obtain the source code:

```bash
git clone https://github.com/miaucl/photobooth.git
```

This will create a folder `photobooth` with all necessary files.

### Install photobooth with dependencies

Run the following command to download and install all dependencies and the photobooth:

```bash
pip install numpy Pillow gpiozero pycups requests PyQt5 picamera2 Flask boto3 qrcode
```

## Run Photobooth from Terminal

Run the photobooth as

```bash
export DISPLAY=:0
python -m photobooth # --run
```

Change any settings via the "Settings" menu.
Afterwards, select "Start photobooth" to get started.
You can trigger the countdown via space bar or an external button.

To exit the application, use the Esc-key or an external button.

You can directly startup the photobooth to the idle screen (skipping the welcome screen) by appending the parameter `--run`.

If you want to run from `ssh`, you need to set `export DISPLAY=:0` for it to work.

If you want to use another language, change it either in your machine or prepend `LANG=ex python...` before the start command.

## Autorun Photobooth with systemd

Use the installation script:

```bash
./install-systemd.sh
```

The photobooth should now auto-start on launch and restart when crashing.
