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

try:
    from PyQt6 import QtCore
except ImportError:
    logging.info("PyQt6 not found, fallback to PyQt5")
    try:
        from PyQt5 import QtCore
    except ImportError:
        print("PyQt5 not found, no fallback available")
        raise ImportError("No supported PyQt found")


from ...Threading import Workers


class Receiver(QtCore.QThread):

    notify = QtCore.pyqtSignal(object)

    def __init__(self, comm):

        super().__init__()
        self._comm = comm

    def handle(self, state):

        self.notify.emit(state)

    def run(self):

        for state in self._comm.iter(Workers.GUI):
            self.handle(state)
