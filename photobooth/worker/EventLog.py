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
from datetime import datetime

from .WorkerTask import WorkerTask


class EventLog(WorkerTask):

    def __init__(self, config, event):

        super().__init__()

        # Event name
        self._event = event

        # Event log file
        filename = 'events.log'
        self._eventLog = os.path.join(config.get('Storage', 'basedir'),
                            filename)

        # Ensure directory exists 
        dirname = os.path.dirname(self._eventLog)
        logging.info('Dirname {}'.format(dirname))
        if not os.path.exists(dirname):
            # Create default directory if dirname don't work
            try: 
                os.makedirs(dirname)
            except OSError as error:
                logging.info('Dirname {} not possible.'.format(dirname))
                path = os.path.join("%Y-%m-%d",
                                    os.path.basename(self._eventLog))
                self._eventLog = strftime(path, localtime(), filename)
                dirname = os.path.dirname(self._eventLog)
                logging.info('New dirname {}'.format(dirname))
                if not os.path.exists(dirname):
                    os.makedirs(dirname)


    def assembleEventLog(self, message):
        """Assemble an event log for a message"""
        return '({}) {}\n'.format(datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"), message)

    def do(self, **kwargs):
        with open(self._eventLog, 'a') as f:
            f.write(self.assembleEventLog('[{}]: {}'.format(self._event, ", ".join(f"{key}={value}" for key, value in kwargs.items()))))
            logging.info('Log event [{}]'.format(self._event))
