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

import os.path
from glob import glob

import random

class AdList:
    """A simple helper class.

    It provides the filenames for the ads
    """

    def __init__(self, ad_prefix, basedir):
        """Initialize filenames to the given ad prefix and search for
        existing files.
        """

        # Set basedir and ad prefix
        self._basedir = basedir
        self._ad_prefix = ad_prefix
        self._ads = []
        self._ads_count = 0

        # Ensure directory exists 
        logging.info('Dirname {}'.format(self._basedir))
        if not os.path.exists(self._basedir):
            # Create default directory if basename don't work
            try: 
                os.makedirs(self._basedir)
            except OSError as error:
                logging.info('Dirname {} not possible.'.format(self._basedir))
                logging.info('New basedir {}'.format(self._basedir))
                if not os.path.exists(self._basedir):
                    os.makedirs(self._basedir)
                
        self.findExistingAds()
        
    def findExistingAds(self):
        """Count number of ads with the given prefix
        """
        exp = self._basedir + "/" + self._ad_prefix + "*"
        logging.info('Loading ads with glob: {}'.format(exp))
        self._ads = glob(exp)
        self._ads_count = len(self._ads)
        logging.info('{} ads found'.format(self._ads_count))
    
    @property
    def ad_prefix(self):
        """Return the prefix for the ads"""
        return self._ad_prefix

    @ad_prefix.setter
    def ad_prefix(self, ad_prefix):
        logging.info('New ad_prefix is {}'.format(ad_prefix))
        self._ad_prefix = ad_prefix

    def getRandomAd(self):
        """Return a random ad filename"""
        if self._ads_count == 0:
            raise IndexError("No ads available")
        else:
            r = random.randrange(self._ads_count)
            return self._ads[(random.randrange(self._ads_count))], r
