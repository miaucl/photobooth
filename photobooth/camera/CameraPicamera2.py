#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2018  Balthasar Reuter <photobooth at re - web dot eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import io
import logging
from time import sleep

from PIL import Image

from picamera2 import Picamera2

from .CameraInterface import CameraInterface



class CameraPicamera2(CameraInterface):

    def __init__(self):

        super().__init__()

        self.hasPreview = True
        self.hasIdle = True

        self._running = False
        self._activeConfig = None

        logging.info('Using PiCamera2')

        self._cap = None

        self.setActive()
        self.setIdle()

    def setActive(self, config=None):

        if self._cap is None:
            self._cap = Picamera2()
            self._picture_config = self._cap.create_still_configuration()
            self._preview_config = self._cap.create_preview_configuration({ "size": (self._cap.still_configuration.size[0] // 4, self._cap.still_configuration.size[1] // 4) }, buffer_count=4)
            self._cap.align_configuration(self._preview_config)
            self._cap.configure(self._preview_config)
        if self._running and config and config != self._activeConfig:
            self._cap.stop()
            self._running = False
            self._cap.configure(config)
            self._activeConfig = config
        if not self._running:
            # There is currently an interference between the libcamera and the official touchscreen which makes the .start() fail occasionally. This is a (temporary, or permanent^^) workaround to make sure it tries until it starts.
            while True:
                try:
                    self._cap.start()
                    break
                except:
                    logging.warn('Starting Picamera2 failed, try again...')
            self._running = True

    def setIdle(self):

        if self._cap:
            self._cap.stop()
            self._running = False

    def getPreview(self):

        self.setActive(self._preview_config)
        stream = io.BytesIO()
        self._cap.capture_file(stream, format='jpeg')
        stream.seek(0)
        return Image.open(stream)

    def getPicture(self):

        self.setActive(self._preview_config)
        stream = io.BytesIO()
        self._cap.capture_file(stream, format='jpeg')
        stream.seek(0)
        return Image.open(stream)
