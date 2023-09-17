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

from PyQt6 import QtCore, QtGui
from PyQt6.QtPrintSupport import QPrinter

from . import Printer


class PrinterPyQt6(Printer):

    def __init__(self, page_size, storage_dir):

        super().__init__(page_size, storage_dir)

        self._app = QtCore.QCoreApplication([]) # Separate QApplication for the printer
        self._printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        self._printer.setFullPage(True)
        self._printer.setPageSize(QtGui.QPageSize(QtCore.QSizeF(*page_size), QtGui.QPageSize.Unit.Millimeter))
        self._printer.setColorMode(QPrinter.ColorMode.Color)

        logging.info('Using printer "%s"', self._printer.printerName())

    def print(self, picture):

        logging.info('Printing picture')
        logging.debug('Page Size: {}, PictureSize: {}'.format(
            self._printer.pageLayout().paintRectPixels(self._printer.resolution()),
            picture.rect()))

        painter = QtGui.QPainter(self._printer)
        painter.drawImage(self._printer.pageLayout().paintRectPixels(self._printer.resolution()), QtGui.QImage(picture), QtGui.QImage(picture).rect())
        painter.end()
