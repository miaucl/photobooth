FROM ubuntu:22.04
ENV DISPLAY=:0
ENV LIBGL_ALWAYS_INDIRECT=1
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN apt update
RUN apt install python3-pip libcups2-dev gettext -y
RUN apt install python3-pyqt5 -y
RUN pip install numpy pyqt5 Pillow==9 pycups requests Flask boto3 qrcode
RUN mkdir /opt/photobooth
COPY autostart.sh autorun.sh /opt/photobooth
COPY photobooth /opt/photobooth/photobooth
COPY supplementals/builds/docker/photobooth.cfg /opt/photobooth
EXPOSE 8080
CMD ["/opt/photobooth/autorun.sh"]