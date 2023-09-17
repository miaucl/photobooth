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
from time import sleep

from PyQt6 import QtCore, QtGui
from PyQt6.QtPrintSupport import QPrinter

from . import Printer


class PrinterPyQt6(Printer):

    def __init__(self, page_size, print_pdf=False):

        super().__init__(page_size)

        self._app = QtCore.QCoreApplication([]) # Separate QApplication for the printer
        self._printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        self._printer.setFullPage(True)
        self._printer.setPageSize(QtGui.QPageSize(QtCore.QSizeF(*page_size),
                                                  QtGui.QPageSize.Unit.Millimeter))
        self._printer.setColorMode(QPrinter.ColorMode.Color)

        logging.info('Using printer "%s"', self._printer.printerName())

        self._print_pdf = print_pdf
        if self._print_pdf:
            logging.info('Using PDF printer')
            self._counter = 0
            self._printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)

    def print(self, picture):

        if self._print_pdf:
            outputFileName = 'print_%d.pdf' % self._counter
            self._printer.setOutputFileName(outputFileName)
            logging.info('Save as PDF: %s' % outputFileName)
            self._counter += 1

        logging.info('Printing picture')
        logging.debug('Page Size: {}, Print Size: {}, PictureSize: {} '.format(
            self._printer.paperRect(QPrinter.Unit.Millimeter), self._printer.pageRect(QPrinter.Unit.Millimeter),
            picture.rect()))

        painter = QtGui.QPainter(self._printer)
        print(type(picture), type(QtGui.QImage(picture)))
        painter.drawImage(self._printer.pageRect(QPrinter.Unit.Millimeter).toAlignedRect(), QtGui.QImage(picture), picture.rect())
        painter.end()
