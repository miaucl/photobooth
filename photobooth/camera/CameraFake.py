#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2023  <photobooth-lausanne at gmail dot com>
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

import logging
import os

from PIL import Image

from .CameraInterface import CameraInterface


class CameraFake(CameraInterface):

    def __init__(self):

        super().__init__()

        self.hasPreview = True
        self.hasIdle = False
        self._size = (1920, 1280)


        dirname, _ = os.path.split(os.path.abspath(__file__))
        self._im = Image.open(f"{dirname}/fake.jpg") 


        logging.info('Using CameraFake')

    def getPreview(self):

        logging.debug('Get preview')

        return self.getPicture()

    def getPicture(self):

        logging.debug('Get picture')

        return self._im
