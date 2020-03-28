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

import logging

from . import Template

from PIL import Image, ImageOps
from io import BytesIO


class FancyTemplate:

    def __init__(self, config):

        self._cfg = config
        self._totalNumPics = 0

    def startup(self, capture_size):
        raise NotImplementedError('template function not implemented!')

    def assemblePicture(self, pictures):
        raise NotImplementedError('template function not implemented!')
