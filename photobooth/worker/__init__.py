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

import os.path

from time import localtime, strftime

from .. import StateMachine
from ..Threading import Workers
import logging

from .PictureList import PictureList
from .PictureMailer import PictureMailer
from .PictureSaver import PictureSaver
from .PictureUploadWebdav import PictureUploadWebdav
from .Counter import Counter
from .PostprocessorPrinter import PostprocessorPrinter
from .EventLog import EventLog


class Worker:

    def __init__(self, config, comm):

        self._comm = comm
        
        # Picture naming convention for assembled pictures
        path = os.path.join(config.get('Storage', 'basedir'),
                            config.get('Storage', 'basename'))
        basename = strftime(path, localtime()) # Replace time placeholder in the storage path if available
        self._pictureList = PictureList(basename)

        # Counters
        self._pictureCounter = Counter(config, 'picture')
        self._printCounter = Counter(config, 'print')

        # Event loggers
        self._eventLogShot = EventLog(config, 'shot')
        self._eventLogPicture = EventLog(config, 'picture')
        self._eventLogPrint = EventLog(config, 'print')

        self.initReviewTasks(config)
        self.initPostprocessTasks(config)
        self.initShotTasks(config)

    def initReviewTasks(self, config):

        self._reviewPictureTasks = []
        self._reviewThumbnailTasks = []
        self._reviewWatermarkedTasks = []

        # Counter for assembled pictures
        self._reviewPictureTasks.append(self._pictureCounter)

        # Event log for assembled pictures
        self._reviewPictureTasks.append(self._eventLogPicture)

        # PictureSaver for assembled pictures
        self._reviewPictureTasks.append(PictureSaver())
        self._reviewThumbnailTasks.append(PictureSaver())
        self._reviewWatermarkedTasks.append(PictureSaver())

        # PictureMailer for assembled pictures
        if config.getBool('Mailer', 'enable'):
            self._reviewPictureTasks.append(PictureMailer(config))

        # PictureUploadWebdav to upload pictures to a webdav storage
        if config.getBool('UploadWebdav', 'enable'):
            self._reviewPictureTasks.append(PictureUploadWebdav(config))

    def initPostprocessTasks(self, config):

        self._postprocessPrintTasks = []
        self._postProcessAutomTasks = []

        # Check print configurations
        if config.getBool('Printer', 'enable'):
            module = config.get('Printer', 'module')
            paper_size = (config.getInt('Printer', 'width'),
                          config.getInt('Printer', 'height'))
            storage_dir = os.path.join(config.get('Storage', 'basedir'), 'pdf')
            if config.getBool('Printer', 'confirmation'):
                # Print with confirmation
                self._postprocessPrintTasks.append(
                    PostprocessorPrinter(module, paper_size, storage_dir))
                # Counter for printed pictures
                self._postprocessPrintTasks.append(self._printCounter)
                # Event log for printed pictures
                self._postprocessPrintTasks.append(self._eventLogPrint)
            else:
                # Print autom. without confirmation
                self._postProcessAutomTasks.append(
                    PostprocessorPrinter(module, paper_size, storage_dir))
                # Counter for printed pictures
                self._postProcessAutomTasks.append(self._printCounter)
                # Event log for printed pictures
                self._postprocessPrintTasks.append(self._eventLogPrint)

    def initShotTasks(self, config):

        self._shotTasks = []

        # PictureSaver for single shots
        self._shotTasks.append(PictureSaver())

        # Event log for shots
        self._shotTasks.append(self._eventLogShot)

    def run(self):

        for state in self._comm.iter(Workers.WORKER):
            self.handleState(state)

        return True

    def handleState(self, state):

        if isinstance(state, StateMachine.TeardownState):
            self.teardown(state)
        elif isinstance(state, StateMachine.ReviewState):
            picturename, thumbnailname, watermarkedname = self._pictureList.getNextPic()
            self.doReviewPictureTasks(state.picture, picturename)
            self.doReviewThumbnailTasks(state.thumbnail, thumbnailname)
            self.doReviewWatermarkedTasks(state.watermarked, watermarkedname)
        elif isinstance(state, StateMachine.PostprocessState) or isinstance(state, StateMachine.GallerySelectState):
            if not state.action:
                self.doPostprocessAutomTasks(state.pictureId)
            elif state.action == 'print':
                self.doPostprocessPrintTasks(state.pictureId)
        elif isinstance(state, StateMachine.CameraEvent):
            if state.name == 'capture':
                picturename = self._pictureList.getNextPicShot()
                self.doShotTasks(state.picture, picturename)
            else:
                raise ValueError('Unknown CameraEvent "{}"'.format(state))

    def teardown(self, state):

        pass

    def doReviewPictureTasks(self, picture, picturename):

        for task in self._reviewPictureTasks:
            task.do(picture=picture, filename=picturename)

    def doReviewThumbnailTasks(self, picture, picturename):

        for task in self._reviewThumbnailTasks:
            task.do(picture=picture, filename=picturename)

    def doReviewWatermarkedTasks(self, picture, picturename):

        for task in self._reviewWatermarkedTasks:
            task.do(picture=picture, filename=picturename)

    def doPostprocessPrintTasks(self, pictureId):

        for task in self._postprocessPrintTasks:
            task.do(pictureId=pictureId)

    def doPostprocessAutomTasks(self, pictureId):

        for task in self._postProcessAutomTasks:
            task.do(pictureId=pictureId)

    def doShotTasks(self, picture, picturename):

        for task in self._shotTasks:
            task.do(picture=picture, filename=picturename)
