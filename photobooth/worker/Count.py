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

from photobooth.Config import Config


class Count():

    def __init__(self, config: Config, subject: str):

        # Counter file
        filename = 'counter_{}.txt'.format(subject)
        self._counterFile = os.path.join(config.get('Storage', 'basedir'),
                            filename)

    def get(self):
        with open(self._counterFile) as f:
            try:
                return int(f.read()) 
            except ValueError:
                logging.info('Cound not read content of counter file at {}'.format(self._counterFile))
                return 0        
