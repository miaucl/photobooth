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

import os
import logging
import boto3


from .PictureWorkerTask import PictureWorkerTask


class PictureUploadS3(PictureWorkerTask):

    def __init__(self, config):

        super().__init__()

        self._region = config.get('UploadS3', 'region')
        self._basepath = config.get('UploadS3', 'basepath')
        self._bucket = config.get('UploadS3', 'bucket')
        self._access_key = config.get('UploadS3', 'client_id')
        self._access_secret = config.get('UploadS3', 'client_secret')
        
        self._session = boto3.session.Session(
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._access_secret,
            region_name=self._region)
        
        self._client = self._session.client('s3', config=boto3.session.Config(signature_version='s3v4'))

        

    def do(self, picture, filename):

        p = os.path.join(self._basepath, os.path.basename(filename))
        logging.info('Uploading picture as %s', p)

        try:
            self._client.upload_file(filename, self._bucket, p, ExtraArgs={'ACL': 'public-read'})
        except Exception as e:
            logging.warn('PictureUploadS3: Upload failed')
            logging.error(e)
