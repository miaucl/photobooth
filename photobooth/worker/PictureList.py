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

from io import BytesIO
import logging

import os.path
from glob import glob
from time import localtime, strftime

import random
from typing import NamedTuple

PictureData = BytesIO
Shot = PictureData
ShotRef = str

class Picture(NamedTuple):
    original: PictureData
    watermarked: PictureData
    thumbnail: PictureData

class PictureRef(NamedTuple):
    original: str
    watermarked: str
    thumbnail: str


class PictureList:
    """A simple helper class.

    It provides the filenames for the assembled pictures and keeps count
    of taken and previously existing pictures.
    """

    def __init__(self, basename: str):
        """Initialize filenames to the given basename and search for
        existing files. Set the counter accordingly.
        """

        # Set basename and suffix
        self._basename = basename
        self.suffix = '.jpg'
        self.count_width = 5

        self.counter = 0
        self.shot_counter = 0

        # Ensure directory exists 
        dirname = os.path.dirname(self.basename)
        logging.info('Dirname {}'.format(dirname))
        if not os.path.exists(dirname):
            # Create default directory if basename don't work
            try: 
                os.makedirs(dirname)
            except OSError as error:
                logging.info('Dirname {} not possible.'.format(dirname))
                path = os.path.join("%Y-%m-%d",
                                    os.path.basename(self.basename))
                self.basename = strftime(path, localtime())
                dirname = os.path.dirname(self.basename)
                logging.info('New dirname {}'.format(dirname))
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                
        self.findExistingFiles()
        
        # Print initial infos
        logging.info('Number of last existing file: %d', self.counter)
        logging.info('Saving pictures as "%s%s.%s"', self.basename,
                     self.count_width * 'X', 'jpg')

    def findExistingFiles(self):
        """Count number of existing files matching the given basename
        """
        # Find existing files
        count_pattern = '[0-9]' * self.count_width
        found_pictures = glob(self.basename + count_pattern + self.suffix)
    
        # Get number of latest file
        if len(found_pictures) == 0:
            self.counter = 0
        else:
            found_pictures.sort()
            last_picture = found_pictures[-1]
            self.counter = int(last_picture[
                -(self.count_width + len(self.suffix)):-len(self.suffix)])

    @property
    def basename(self):
        """Return the basename for the files"""
        return self._basename

    @basename.setter
    def basename(self, basename: str):
        logging.info('New basename is {}'.format(basename))
        self._basename = basename

    def count(self):
        """Return the count"""
        return self.counter

    def getFilename(self, count: int):
        """Return the file name for a given file number"""
        return self.basename + str(count).zfill(self.count_width) + self.suffix

    def getThumbnail(self, count: int):
        """Return the thumbnail name for a given file number"""
        return self.basename + str(count).zfill(self.count_width) + ".thumbnail" + self.suffix

    def getWatermarked(self, count: str):
        """Return the watermarked name for a given file number"""
        return self.basename + str(count).zfill(self.count_width) + ".watermark" + self.suffix

    def getFilenameShot(self, count: str, shotCount: str):
        """Return the file name for a given shot & file number"""
        return self.getFilename(count+1)[:-len(self.suffix)] + \
            '_shot' + str(shotCount).zfill(3) + self.suffix

    def getNewPicture(self):
        """Update counter and return the next new filename and thumbnail"""
        self.counter += 1
        self.shot_counter = 0
        return self.getPicture(self.counter)

    def getNextPictureShot(self):
        """Update counter and return the next filename"""
        self.shot_counter += 1
        return self.getFilenameShot(self.counter, self.shot_counter)

    def getRandomPicture(self):
        """Return a random picture"""
        
        self.findExistingFiles()
        if self.counter == 0:
            return self.getPicture(0), 0
        else:
            r = random.randrange(self.counter)+1
            return self.getPicture(random.randrange(self.counter)+1), r

    def getPicture(self, count: str):
        """Return the picture for a given file number"""
        return PictureRef(self.getFilename(count), self.getWatermarked(count), self.getThumbnail(count))

    def getNextPicture(self, picture: PictureRef):
        """Return the next filename or None if not available"""
        index = int(picture.original[len(self.basename):-4])
        if index < self.counter:
            return self.getPicture(index+1)
        else:
            None

    def getPreviousPicture(self, picture: PictureRef):
        """Return the previous filename or None if not available"""
        index = int(picture.original[len(self.basename):-4])
        if index > 0:
            return self.getPicture(index-1)
        else:
            None

    def getLast(self):
        """Return the current filename"""
        return self.getPicture(self.counter)
