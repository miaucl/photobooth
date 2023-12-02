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

import configparser
import logging
import os


class Config:

    def __init__(self, filename: str):

        self._filename = filename

        self._cfg = configparser.ConfigParser(interpolation=None)
        self.defaults()
        self.read()

    @property
    def filename(self) -> str:

        return self._filename

    @filename.setter
    def filename(self, value: str):

        self._filename = value

    def defaults(self):

        filename = os.path.join(os.path.dirname(__file__), 'defaults.cfg')
        logging.info('Reading config file "%s"', filename)
        self._cfg.read(filename)

    def read(self):

        logging.info('Reading config file "%s"', self._filename)
        self._cfg.read(self._filename)

    def write(self):

        logging.info('Writing config file "%s"', self._filename)
        with open(self._filename, 'w') as configfile:
            self._cfg.write(configfile)

    def get(self, section: str, key: str) -> str:

        return self._cfg[section][key]

    def getInt(self, section: str, key: str) -> int:

        return self._cfg.getint(section, key)

    def getFloat(self, section: str, key: str) -> float:

        return self._cfg.getfloat(section, key)

    def getBool(self, section: str, key: str) -> bool:

        return self._cfg.getboolean(section, key)

    def getIntList(self, section: str, key: str) -> list[int]:

        if len(self._cfg[section][key].strip()) > 0:
            return [int(i) for i in self._cfg[section][key].split(',')]
        else:
            return []

    def set(self, section: str, key: str, value: str or int or bool or list[str]):

        self._cfg[section][key] = value
