#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from . import Template

from PIL import Image
from io import BytesIO

from .PictureDimensions import PictureDimensions


class StandardTemplate(Template):

    def __init__(self, config):

        super().__init__(config)

        logging.info('Using template "%s"', self)

        self._pic_dims = PictureDimensions(self._cfg)
        self._totalNumPics = self._pic_dims.totalNumPictures

        self._background = self._cfg.get('Picture', 'background')
        self._foreground = self._cfg.get('Picture', 'foreground')
        self._watermark = self._cfg.get('Picture', 'watermark')

        self._fg_template = None
        self._bg_template = None
        self._wm_template = None


    def startup(self, capture_size):
        
        self._pic_dims.computeThumbnailDimensions(capture_size)

        if len(self._background) > 0:
            logging.info('Using background "{}"'.format(self._background))
            bg_picture = Image.open(self._background)
            self._bg_template = bg_picture.resize(self._pic_dims.outputSize)
        else:
            self._bg_template = Image.new('RGB', self._pic_dims.outputSize,
                                       (255, 255, 255))
            
        if len(self._foreground) > 0:
            logging.info('Using foreground "{}"'.format(self._foreground))
            fg_picture = Image.open(self._foreground)
            self._fg_template = fg_picture.resize(self._pic_dims.outputSize)

        if len(self._watermark) > 0:
            logging.info('Using watermark "{}"'.format(self._watermark))
            wm_picture = Image.open(self._watermark)
            self._wm_template = wm_picture.resize(self._pic_dims.outputSize)


    def assemblePicture(self, pictures):

        logging.info('Assembling picture')

        picture = self._bg_template.copy()
        for i in range(self.totalNumPics):
            shot = Image.open(pictures[i])
            resized = shot.resize(self._pic_dims.thumbnailSize, Image.BICUBIC)
            picture.paste(resized, self._pic_dims.thumbnailOffset[i])

        if self._fg_template: 
            picture.paste(self._fg_template, mask=self._fg_template) 

        byte_data = BytesIO()
        picture.save(byte_data, format='jpeg')

        thumbnail = picture.copy()
        thumbnail.thumbnail(((self._cfg.getInt("Gallery", "size_x"), self._cfg.getInt("Gallery", "size_y")))) 

        thumbnail_byte_data = BytesIO()
        thumbnail.save(thumbnail_byte_data, format='jpeg')

        watermarked = picture.copy()
        if self._wm_template: 
            watermarked.paste(self._wm_template, mask=self._wm_template) 

        watermarked_byte_data = BytesIO()
        watermarked.save(watermarked_byte_data, format='jpeg')

        return byte_data, thumbnail_byte_data, watermarked_byte_data
