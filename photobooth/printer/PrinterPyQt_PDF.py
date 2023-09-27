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

try:
    from PyQt6.QtPrintSupport import QPrinter
except ImportError:
    logging.info("PyQt6 not found, fallback to PyQt5")
    try:
        from PyQt5.QtPrintSupport import QPrinter
    except ImportError:
        print("PyQt5 not found, no fallback available")
        raise ImportError("No supported PyQt found")


from .PrinterPyQt import PrinterPyQt


class PrinterPyQt_PDF(PrinterPyQt):

    def __init__(self, page_size, storage_dir):

        super().__init__(page_size, storage_dir)

        logging.info('Using printer "%s"', self._printer.printerName())

        self._counter = 0
        self._printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)

    def print(self, picture):

        outputFileName = os.path.join(self.storageDir, 'print_{}.pdf'.format(self._counter))
        self._printer.setOutputFileName(outputFileName)
        logging.info('Save as PDF: %s' % outputFileName)
        self._counter += 1

        super().print(picture)

