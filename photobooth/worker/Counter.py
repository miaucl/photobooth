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
from time import localtime, strftime

from .WorkerTask import WorkerTask


class Counter(WorkerTask):

    def __init__(self, config, subject):

        super().__init__()

        # Counter file
        filename = 'counter_{}.txt'.format(subject)
        self._counterFile = os.path.join(config.get('Storage', 'basedir'),
                            filename)

        # Ensure directory exists 
        dirname = os.path.dirname(self._counterFile)
        logging.info('Dirname {}'.format(dirname))
        if not os.path.exists(dirname):
            # Create default directory if dirname don't work
            try: 
                os.makedirs(dirname)
            except OSError as error:
                logging.info('Dirname {} not possible.'.format(dirname))
                path = os.path.join("%Y-%m-%d",
                                    os.path.basename(self._counterFile))
                self._counterFile = strftime(path, localtime(), filename)
                dirname = os.path.dirname(self._counterFile)
                logging.info('New dirname {}'.format(dirname))
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

        if os.path.isfile(self._counterFile):
            with open(self._counterFile) as f:
                try:
                    self._counter = int(f.read()) 
                except ValueError:
                    logging.info('Cound not read content of counter file at {}'.format(self._counterFile))
                    self._counter = 0        
        else:
            self._counter = 0

        # Write back the counter
        with open(self._counterFile, 'w') as f:
            f.write(str(self._counter))
            logging.info('Counter successfully written: {} '.format(self._counter))


    def do(self, **kwargs):
        self._counter = self._counter + 1
        logging.info('Increase counter %s to %d', self._counterFile, self._counter)
        # Write the counter
        with open(self._counterFile, 'w') as f:
            f.write(str(self._counter))
