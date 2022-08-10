#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

        MAX_SIZE = (180, 240) 
        picture.thumbnail(MAX_SIZE) 

        thumbnail_byte_data = BytesIO()
        picture.save(thumbnail_byte_data, format='jpeg')

        return byte_data, thumbnail_byte_data
