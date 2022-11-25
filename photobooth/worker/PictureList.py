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

import os.path
from glob import glob
from time import localtime, strftime

import random

class PictureList:
    """A simple helper class.

    It provides the filenames for the assembled pictures and keeps count
    of taken and previously existing pictures.
    """

    def __init__(self, basename):
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
        pictures = glob(self.basename + count_pattern + self.suffix)
    
        # Get number of latest file
        if len(pictures) == 0:
            self.counter = 0
        else:
            pictures.sort()
            last_picture = pictures[-1]
            self.counter = int(last_picture[
                -(self.count_width + len(self.suffix)):-len(self.suffix)])

    @property
    def basename(self):
        """Return the basename for the files"""
        return self._basename

    @basename.setter
    def basename(self, basename):
        logging.info('New basename is {}'.format(basename))
        self._basename = basename
        
    def getFilename(self, count):
        """Return the file name for a given file number"""
        return self.basename + str(count).zfill(self.count_width) + self.suffix

    def getThumbnail(self, count):
        """Return the thumbnail name for a given file number"""
        return self.basename + str(count).zfill(self.count_width) + ".thumbnail" + self.suffix

    def getFilenameShot(self, count, shotCount):
        """Return the file name for a given shot & file number"""
        return self.getFilename(count+1)[:-len(self.suffix)] + \
            '_shot' + str(shotCount).zfill(3) + self.suffix

    def getLast(self):
        """Return the current filename"""
        return self.getFilename(self.counter)

    def getNextPic(self):
        """Update counter and return the next filename and thumbnail"""
        self.counter += 1
        self.shot_counter = 0
        return self.getFilename(self.counter), self.getThumbnail(self.counter)

    def getNextPicShot(self):
        """Update counter and return the next filename"""
        self.shot_counter += 1
        return self.getFilenameShot(self.counter, self.shot_counter)

    def getRandomPic(self):
        """Return a random filename """
        
        self.findExistingFiles()
        if self.counter == 0:
            return self.getFilename(0)
        else:
            return self.getFilename(random.randrange(self.counter)+1)
