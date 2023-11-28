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

from photobooth.Config import Config
from photobooth.worker.WorkerTask import WorkerTask

from .. import StateMachine
from ..Threading import Communicator, Workers

from .AdList import AdList
from .PictureList import Picture, PictureList, PictureRef, Shot, ShotRef
from .PictureMailer import PictureMailer
from .PictureSaver import PictureSaver
from .ShotSaver import ShotSaver
from .PictureUploadS3 import PictureUploadS3
from .PictureUploadWebdav import PictureUploadWebdav
from .Counter import Counter
from .PostprocessorPrinter import PostprocessorPrinter
from .EventLog import EventLog


class Worker:

    def __init__(self, config: Config, comm: Communicator):

        self._comm = comm
        
        # Picture naming convention for assembled pictures
        path = os.path.join(config.get('Storage', 'basedir'),
                            config.get('Storage', 'basename'))
        basename = strftime(path, localtime()) # Replace time placeholder in the storage path if available
        self._pictureList = PictureList(basename)
        self._adList = AdList(config.get('Storage', 'ad_prefix'), config.get('Storage', 'basedir'))

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

    def initReviewTasks(self, config: Config):

        self._reviewPictureTasks: list[WorkerTask] = []

        # Counter for assembled pictures
        self._reviewPictureTasks.append(self._pictureCounter)

        # Event log for assembled pictures
        self._reviewPictureTasks.append(self._eventLogPicture)

        # PictureSaver for assembled pictures
        self._reviewPictureTasks.append(PictureSaver())

        # PictureMailer for assembled pictures
        if config.getBool('Mailer', 'enable'):
            self._reviewPictureTasks.append(PictureMailer(config))

        # PictureUploadS3 to upload pictures to a s3 storage for direct download
        if config.getBool('UploadS3', 'enable'):
            self._reviewPictureTasks.append(PictureUploadS3(config))

        # PictureUploadWebdav to upload pictures to a webdav storage
        if config.getBool('UploadWebdav', 'enable'):
            self._reviewPictureTasks.append(PictureUploadWebdav(config))

    def initPostprocessTasks(self, config: Config):

        self._postprocessPrintTasks: list[WorkerTask] = []
        self._postProcessAutomTasks: list[WorkerTask] = []

        # Check print configurations
        if config.getBool('Printer', 'enable'):
            module = config.get('Printer', 'module')
            paper_size = (config.getInt('Printer', 'width'),
                          config.getInt('Printer', 'height'))
            storage_dir = config.get('Storage', 'basedir')
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
                self._postProcessAutomTasks.append(self._eventLogPrint)

    def initShotTasks(self, config: Config):

        self._shotTasks: list[WorkerTask] = []

        # PictureSaver for single shots
        self._shotTasks.append(ShotSaver())

        # Event log for shots
        self._shotTasks.append(self._eventLogShot)

    def run(self):

        for state in self._comm.iter(Workers.WORKER):
            self.handleState(state)

        return True

    def handleState(self, state: StateMachine.State):

        if isinstance(state, StateMachine.TeardownState):
            self.teardown(state)
        elif isinstance(state, StateMachine.ReviewState):
            pictureRef = self._pictureList.getNewPicture()
            self.doReviewPictureTasks(state.picture, pictureRef)
        elif isinstance(state, StateMachine.PostprocessState) or isinstance(state, StateMachine.GallerySelectState):
            if not state.action:
                self.doPostprocessAutomTasks(state.pictureRef)
            elif state.action == 'print':
                self.doPostprocessPrintTasks(state.pictureRef)
        elif isinstance(state, StateMachine.CameraEvent):
            if state.name == 'capture':
                shotRef = self._pictureList.getNextPictureShot()
                self.doShotTasks(state.shot, shotRef)
            else:
                raise ValueError('Unknown CameraEvent "{}"'.format(state))

    def teardown(self, state):

        pass

    def doReviewPictureTasks(self, picture: Picture, pictureRef: PictureRef):

        for task in self._reviewPictureTasks:
            task.do(picture=picture, pictureRef=pictureRef)

    def doPostprocessPrintTasks(self, pictureRef: PictureRef):

        for task in self._postprocessPrintTasks:
            task.do(pictureRef=pictureRef)

    def doPostprocessAutomTasks(self, pictureRef: PictureRef):

        for task in self._postProcessAutomTasks:
            task.do(pictureRef=pictureRef)

    def doShotTasks(self, shot: Shot, shotRef: ShotRef):

        for task in self._shotTasks:
            task.do(shot=shot, shotRef=shotRef)
