#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2019  Balthasar Reuter <photobooth at re - web dot eu>
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
#
# This class was contributed by
# @oelegeirnaert (https://github.com/oelegeirnaert)
# see https://github.com/reuterbal/photobooth/pull/113

import logging
import os
import re
from PIL import ImageQt

try:
    import cups
except ImportError:
    logging.error('pycups is not installed')
    cups = None

from PIL import ImageQt

from . import Printer


class PrinterPyCups(Printer):

    def __init__(self, page_size: tuple[int, int] or list[int], storage_dir: str):

        super().__init__(page_size, storage_dir)

        self._conn = cups.Connection() if cups else None
        self._printer = None

        if os.access('/dev/shm', os.W_OK):
            self._tmp_filename = '/dev/shm/print.jpg'
        else:
            self._tmp_filename = '/tmp/print.jpg'
        logging.debug('Storing temp files to "{}"'.format(self._tmp_filename))

        self.find_printer()
    
    def find_printer(self):

        # Find connected printer if not already
        if self._conn is not None and self._printer is None:
            printer_info = os.popen('lpinfo -v').read() # Use `lpinfo -v` to list current network info including printers
            network_printers = re.findall(r"(dnssd.+)", printer_info) # Find the network printers and extract the uri
            self._printer = next((name for name, item in self._conn.getPrinters().items() if item["device-uri"] in network_printers), None) # Take the first known printer available
            logging.info('Using printer "%s"', self._printer)


    def print(self, picture: ImageQt.ImageQt):

        self.find_printer()

        if self._conn is not None and self._printer is not None:            
            if isinstance(picture, ImageQt.ImageQt):
                picture.save(self._tmp_filename)
            else:
                picture.save(self._tmp_filename, format='JPEG')
            self._conn.printFile(self._printer, self._tmp_filename,
                                 "photobooth", {})
