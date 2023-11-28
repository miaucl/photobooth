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
import requests

from pathlib import Path
from photobooth.Config import Config

from photobooth.worker.PictureList import Picture, PictureRef

from .PictureWorkerTask import PictureWorkerTask


class PictureUploadWebdav(PictureWorkerTask):

    def __init__(self, config: Config):

        super().__init__()

        self._baseurl = config.get('UploadWebdav', 'url')
        if config.getBool('UploadWebdav', 'use_auth'):
            self._auth = (config.get('UploadWebdav', 'user'),
                          config.get('UploadWebdav', 'password'))
        else:
            self._auth = None

    def do(self, picture: Picture, pictureRef: PictureRef):

        url = self._baseurl + '/' + Path(pictureRef.original).name
        logging.info('Uploading picture as %s', url)

        r = requests.put(url, data=picture.original.getbuffer(), auth=self._auth)
        if r.status_code in range(200, 300):
            logging.warn(('PictureUploadWebdav: Upload failed with '
                          'status code {}').format(r.status_code))
