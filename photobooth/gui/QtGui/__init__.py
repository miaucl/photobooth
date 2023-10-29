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

# Available style sheets as tuples of (style name, style file)
styles = (('default', 'stylesheets/default.qss'),
          ('accent-orange', 'stylesheets/accent-orange.qss'),
          ('accent-blue', 'stylesheets/accent-blue.qss'),
          ('plain-orange', 'stylesheets/plain-orange.qss'),

          ('plain-800x480-Maroon', 'stylesheets/plain/800x480/plain-Maroon.qss'),
          ('plain-800x480-Salmon', 'stylesheets/plain/800x480/plain-Salmon.qss'),
          ('plain-800x480-HotCinnamon', 'stylesheets/plain/800x480/plain-HotCinnamon.qss'),
          ('plain-800x480-GoldenTainoi', 'stylesheets/plain/800x480/plain-GoldenTainoi.qss'),
          ('plain-800x480-VerdunGreen', 'stylesheets/plain/800x480/plain-VerdunGreen.qss'),
          ('plain-800x480-PastelGreen', 'stylesheets/plain/800x480/plain-PastelGreen.qss'),
          ('plain-800x480-Malibu', 'stylesheets/plain/800x480/plain-Malibu.qss'),
          ('plain-800x480-CongressBlue', 'stylesheets/plain/800x480/plain-CongressBlue.qss'),
          ('plain-800x480-CornflowerBlue', 'stylesheets/plain/800x480/plain-CornflowerBlue.qss'),
          ('plain-800x480-Lavender', 'stylesheets/plain/800x480/plain-Lavender.qss'),
          ('plain-800x480-Flirt', 'stylesheets/plain/800x480/plain-Flirt.qss'),  

          ('plain-1280x800-Maroon', 'stylesheets/plain/1280x800/plain-Maroon.qss'),
          ('plain-1280x800-Salmon', 'stylesheets/plain/1280x800/plain-Salmon.qss'),
          ('plain-1280x800-HotCinnamon', 'stylesheets/plain/1280x800/plain-HotCinnamon.qss'),
          ('plain-1280x800-GoldenTainoi', 'stylesheets/plain/1280x800/plain-GoldenTainoi.qss'),
          ('plain-1280x800-VerdunGreen', 'stylesheets/plain/1280x800/plain-VerdunGreen.qss'),
          ('plain-1280x800-PastelGreen', 'stylesheets/plain/1280x800/plain-PastelGreen.qss'),
          ('plain-1280x800-Malibu', 'stylesheets/plain/1280x800/plain-Malibu.qss'),
          ('plain-1280x800-CongressBlue', 'stylesheets/plain/1280x800/plain-CongressBlue.qss'),
          ('plain-1280x800-CornflowerBlue', 'stylesheets/plain/1280x800/plain-CornflowerBlue.qss'),
          ('plain-1280x800-Lavender', 'stylesheets/plain/1280x800/plain-Lavender.qss'),
          ('plain-1280x800-Flirt', 'stylesheets/plain/1280x800/plain-Flirt.qss'),  
          )

from .PyQtGui import PyQtGui  # noqa
