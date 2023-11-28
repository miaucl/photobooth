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
from PIL import ImageQt

try:
    from PyQt6 import QtCore
    from PyQt6 import QtGui
    from PyQt6.QtPrintSupport import QPrinter
except ImportError:
    logging.info("PyQt6 not found, fallback to PyQt5")
    try:
        from PyQt5 import QtCore
        from PyQt5 import QtGui
        from PyQt5.QtPrintSupport import QPrinter
    except ImportError:
        print("PyQt5 not found, no fallback available")
        raise ImportError("No supported PyQt found")

from . import Printer


class PrinterPyQt(Printer):

    def __init__(self, page_size: tuple[int, int] | list[int], storage_dir: str):

        super().__init__(page_size, storage_dir)

        self._app = QtCore.QCoreApplication([]) # Separate QApplication for the printer
        self._printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        self._printer.setFullPage(True)
        self._printer.setPageSize(QtGui.QPageSize(QtCore.QSizeF(*page_size), QtGui.QPageSize.Unit.Millimeter))
        self._printer.setColorMode(QPrinter.ColorMode.Color)

        logging.info('Using printer "%s"', self._printer.printerName())

    def print(self, picture: ImageQt.ImageQt):

        logging.info('Printing picture')
        logging.debug('Page Size: {}, PictureSize: {}'.format(
            self._printer.pageLayout().paintRectPixels(self._printer.resolution()),
            picture.rect()))

        painter = QtGui.QPainter(self._printer)
        painter.drawImage(self._printer.pageLayout().paintRectPixels(self._printer.resolution()), QtGui.QImage(picture), QtGui.QImage(picture).rect())
        painter.end()
