#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from photobooth.Config import Config
from photobooth.worker.PictureList import Picture, ShotRef

# Available template modules as tuples of (config name, module name, class name)
modules = (
    ('standard', 'StandardTemplate', 'StandardTemplate'),
    ('fancy', 'FancyTemplate', 'FancyTemplate'))


class Template:

    def __init__(self, config: Config):

        self._cfg = config
        self._totalNumPics = 0

    def startup(self):
        raise NotImplementedError('template function not implemented!')

    def assemblePicture(self, pictures: list[ShotRef]) -> Picture:
        raise NotImplementedError('template function not implemented!')

    @property
    def totalNumPics(self):
        ### Number of pictures to be taken
        return self._totalNumPics