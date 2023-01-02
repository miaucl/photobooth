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


class GuiPostprocessor:

    def __init__(self, config):

        super().__init__()

        self._optionalItems = []
        self._automItems = []

        if config.getBool('Printer', 'enable'):
            if config.getBool('Printer', 'confirmation'):
                self._optionalItems.append(
                    PostprocessItem(_('Print'), 'print'))
            else:
                self._automItems.append(
                    PostprocessItem(_('Print'), 'print'))

    def getOptionalItems(self):
        """Get all optional postprocessing items"""
        return [task for task in self._optionalItems]


    def getAllItems(self):
        """Get all postprocessing items"""
        return [task for task in self._optionalItems + self._automItems] 


class PostprocessItem:

    def __init__(self, label, action):

        super().__init__()
        self.label = label
        self.action = action

    @property
    def label(self):

        return self._label

    @label.setter
    def label(self, label):

        if not isinstance(label, str):
            raise TypeError('Label must be a string')

        self._label = label

    @property
    def action(self):

        return self._action

    @action.setter
    def action(self, action):

        if not isinstance(action, str):
            raise TypeError('Action must be a string')

        self._action = action
