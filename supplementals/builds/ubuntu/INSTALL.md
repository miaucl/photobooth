# Ubuntu 22

These instructions are tailored towards running the photobooth on a Ubuntu 22, using gphoto2 for the camera and pycups for printing.

## Configure and update Ubuntu

As always, make sure to be up-to-date.

```bash
sudo apt update
sudo apt upgrade
```

Afterwards, open the configuration utility to adapt everything to your needs (e.g., setup WiFi, hostname, etc.)

## Configure touch screen, printer etc

Configure any not working hardware, e.g., my touch screen needs some additional steps.

If you plan on using a printer, make sure it is configured as **default printer**!

## Install dependencies for the photobooth

These dependencies are required to run the application.

### Install required packages

In a terminal, enter the following commands

```bash
sudo apt install python3-dev python3-pip venv 
sudo apt install gphoto2 libgphoto2-dev # to use gphoto2
sudo apt install libffi6 libffi-dev # for gphoto2-cffi bindings
sudo apt install libcups2-dev # to use pycups
sudo apt install gettext # to add other languages
```

### Misc.

Remove some files to get gphoto2 working

Some distros ship with a utility called `gvfs` to allow mounting cameras as virtual file systems.
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

### Initialize `venv`

To avoid installing everything on a system level, I recommend to initialize a virtual environment.
For that, enter the folder created in the previous step

```bash
cd photobooth
```

and run the following command

```bash
python3 -m venv .venv
```

Activate the virtual environment.
You have to do this whenever you open a new terminal or rebooted your hardware

```bash
source .venv/bin/activate
```

### Install photobooth with dependencies

Run the following command to download and install all dependencies and the photobooth:

```bash
pip install numpy Pillow pycups requests PyQt6 gphoto2 gphoto2-cffi Flask
```

## Run Photobooth from Terminal

If not yet done, activate your virtual environment

```bash
source .venv/bin/activate
```

and run the photobooth as

```bash
python -m photobooth
```

Alternatively, use the Python binary of the virtual environment to start the photobooth directly without activating the environment first:

```bash
.venv/bin/python -m photobooth
```

This is useful, e.g., when starting the photobooth from scripts, desktop shortcuts, or when using an autostart mechanism of your window manager.

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
