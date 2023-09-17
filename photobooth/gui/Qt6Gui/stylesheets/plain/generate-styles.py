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

import glob
import csv 
import os

# Output
output = []

# Find all template files
files = glob.glob('**/*.qss.template')
print(f'Following templates found: {files}')

colorPairs = []
# Load csv file
with open('colors.csv', encoding='utf-8') as csvf: 
  # Load csv file data using csv library's dictionary reader
  csvReader = csv.DictReader(csvf) 
  # Convert each csv row into python dict
  for row in csvReader: 
    # Add this python dict to json array
    colorPairs.append(row)

print(f'Following color pairs found: {colorPairs}')

# Loop all colors
for colorPair in colorPairs:
  print(f'> Color pair: {colorPair}')

  # Loop all template files
  for t in files:
    # Create new file name
    f = t.replace('plain-color.qss.template', f'plain-{colorPair["LABEL"]}.qss')
    print(f'> > Style: {f}')
    output.append(f'(\'plain-{os.path.split(f)[0]}-{colorPair["LABEL"]}\', \'stylesheets/plain/{f}\'),')
   
    # Read template file
    with open(t, 'r') as templatefile:
      template = templatefile.read()

      # Write file
      with open(f, 'w+') as writefile:
        template = template.replace('$STRONG', colorPair["STRONG"])
        template = template.replace('$WEAK', colorPair["WEAK"])
        writefile.write(template)

# Print output
print("Add following lines to the '../Qt6Gui/__init__.py' file:")
print('\n'.join(output))