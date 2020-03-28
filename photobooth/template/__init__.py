#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

# Available template modules as tuples of (config name, module name, class name)
modules = (
    ('standard', 'StandardTemplate', 'StandardTemplate'),
    ('fancy', 'FancyTemplate', 'FancyTemplate'))


class Template:

    def __init__(self, config):

        self._cfg = config
        self._totalNumPics = 0

    def startup(self):
        raise NotImplementedError('template function not implemented!')

    def assemblePicture(self, pictures):
        raise NotImplementedError('template function not implemented!')

    @property
    def totalNumPics(self):
        ### Number of pictures to be taken
        return self._totalNumPics