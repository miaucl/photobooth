# Mac Ventura (Apple Silicon)

These instructions are tailored towards running the photobooth on a Mac M1X, , using opencv for the camera and qtprinter for printing.

_Hint: Just make sure, you only have one camera available for OpenCV. Continuity Camera using your IPhone might be causing problems._

## Install homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Configure touch screen, printer etc

If you plan on using a printer, make sure it is configured as default printer!

## Install dependencies for the photobooth

These dependencies are required to run the application.

### Install required packages

In a terminal, enter the following commands

```bash
brew install python virtualenv
brew install opencv # to use opencv
brew install gettext # to add other languages
```

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
pip install numpy opencv-python Pillow requests PyQt6 Flask
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
