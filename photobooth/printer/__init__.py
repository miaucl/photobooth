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

# Available printer modules as tuples of (config name, module name, class name)
modules = (
    ('PyQt', 'PrinterPyQt', 'PrinterPyQt'),
    ('PyQt_PDF', 'PrinterPyQt_PDF', 'PrinterPyQt_PDF'),
    ('PyCUPS', 'PrinterPyCups', 'PrinterPyCups'))

import os

class Printer:

    def __init__(self, page_size, storage_dir):

        self.pageSize = page_size
        self.storageDir = storage_dir

    @property
    def pageSize(self):

        return self._page_size

    @pageSize.setter
    def pageSize(self, page_size):

        if not isinstance(page_size, (list, tuple)) or len(page_size) != 2:
            raise ValueError('page_size must be a list/tuple of length 2')

        self._page_size = page_size

    @property
    def storageDir(self):

        return self._storage_dir

    @storageDir.setter
    def storageDir(self, storage_dir):

        if not os.path.isdir(storage_dir):
            raise ValueError("'storage_dir' must exist")

        self._storage_dir = storage_dir

    def print(self, picture):

        raise NotImplementedError('print function not implemented!')
