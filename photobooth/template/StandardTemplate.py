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

from .PictureDimensions import PictureDimensions


class StandardTemplate(Template):

    def __init__(self, config):

        super().__init__(config)

        logging.info('Using template "%s"', self)

        self._pic_dims = PictureDimensions(self._cfg)
        self._totalNumPics = self._pic_dims.totalNumPictures

        self._background = self._cfg.get('Picture', 'background')


    def startup(self, capture_size):
        
        self._pic_dims.computeThumbnailDimensions(capture_size)

        if len(self._background) > 0:
            logging.info('Using background "{}"'.format(self._background))
            bg_picture = Image.open(self._background)
            self._bg_template = bg_picture.resize(self._pic_dims.outputSize)
        else:
            self._bg_template = Image.new('RGB', self._pic_dims.outputSize,
                                       (255, 255, 255))


    def assemblePicture(self, pictures):

        logging.info('Assembling picture')

        picture = self._bg_template.copy()
        for i in range(self.totalNumPics):
            shot = Image.open(pictures[i])
            resized = shot.resize(self._pic_dims.thumbnailSize, Image.BICUBIC)
            picture.paste(resized, self._pic_dims.thumbnailOffset[i])

        byte_data = BytesIO()
        picture.save(byte_data, format='jpeg')

        return byte_data
