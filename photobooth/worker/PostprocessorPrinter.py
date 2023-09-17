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

from .. import printer
from ..util import lookup_and_import
from PIL import Image, ImageQt
from .PostprocessorWorkerTask import PostprocessorWorkerTask


class PostprocessorPrinter(PostprocessorWorkerTask):

    def __init__(self, printer_module, paper_size, storage_dir, **kwargs):

        super().__init__(**kwargs)

        Printer = lookup_and_import(printer.modules, printer_module, 'printer')
        self._printer = Printer(paper_size, storage_dir)

    def do(self, pictureId):
        self._printer.print(ImageQt.ImageQt(Image.open(pictureId)))
