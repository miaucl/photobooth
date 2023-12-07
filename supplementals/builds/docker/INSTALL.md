# Docker

These instructions are tailored towards running the photobooth in a docker container, using a dummy camera and pyqt pdf for printing.

## Configure host system

Install docker. (I let you decide how you want to do that ^^)

## Setup xserver

For linux based hosts, you are fine.
For mac based hosts, follow this using XQuartz: <https://gist.github.com/sorny/969fe55d85c9b0035b0109a31cbcb088>
For windows based hosts, help yourself ;)

## Start container

You might need to adjust the ENV variable `DISPLAY` according to your setup.

```bash
docker compose up --build
```

_`--build` flag is useful for development :)_

## Configure Dockerfile

Replace the the `autostart.sh` with `autorun.sh` to skip the home screen.

Replace the CMD with `CMD ["sleep", "infinity"]` for debugging.

## PyQT 5 vs 6

As long as there is no proper way to setup a ubuntu docker image with pyqt6, pyqt5 is used, which requires Pillow==9.
