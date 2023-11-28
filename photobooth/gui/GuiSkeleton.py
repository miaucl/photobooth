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

from photobooth.Threading import Communicator
from .. import StateMachine


class GuiSkeleton:

    def __init__(self, communicator: Communicator):

        super().__init__()
        self._comm = communicator

    def updatePreview(self, state: StateMachine.State):

        raise NotImplementedError()

    def updateSlideshow(self, state: StateMachine.State):

        raise NotImplementedError()

    def showError(self, state: StateMachine.State):

        raise NotImplementedError()

    def showWelcome(self, state: StateMachine.State):

        raise NotImplementedError()

    def showStartup(self, state: StateMachine.State):

        raise NotImplementedError()

    def showSettings(self, state: StateMachine.State):

        raise NotImplementedError()

    def showIdle(self, state: StateMachine.State):

        raise NotImplementedError()

    def showSlideshow(self, state: StateMachine.State):

        raise NotImplementedError()

    def showGallery(self, state: StateMachine.State):

        raise NotImplementedError()

    def showGallerySelect(self, state: StateMachine.State):

        raise NotImplementedError()

    def showGreeter(self, state: StateMachine.State):

        raise NotImplementedError()

    def showCountdown(self, state: StateMachine.State):

        raise NotImplementedError()

    def showCapture(self, state: StateMachine.State):

        raise NotImplementedError()

    def showAssemble(self, state: StateMachine.State):

        raise NotImplementedError()

    def showReview(self, state: StateMachine.State):

        raise NotImplementedError()

    def showPostprocess(self, state: StateMachine.State):

        raise NotImplementedError()

    def teardown(self, state: StateMachine.State):

        raise NotImplementedError()

    def handleState(self, state):

        if isinstance(state, StateMachine.CameraEvent):
            self.updatePreview(state)
        elif isinstance(state, StateMachine.GuiEvent):
            self.updateSlideshow(state)


        elif isinstance(state, StateMachine.ErrorState):
            self.showError(state)
        elif isinstance(state, StateMachine.WelcomeState):
            self.showWelcome(state)
        elif isinstance(state, StateMachine.StartupState):
            self.showStartup(state)
        elif isinstance(state, StateMachine.IdleState):
            self.showIdle(state)
        elif isinstance(state, StateMachine.SlideshowState):
            self.showSlideshow(state)
        elif isinstance(state, StateMachine.GalleryState):
            self.showGallery(state)
        elif isinstance(state, StateMachine.GallerySelectState):
            self.showGallerySelect(state)
        elif isinstance(state, StateMachine.GreeterState):
            self.showGreeter(state)
        elif isinstance(state, StateMachine.CountdownState):
            self.showCountdown(state)
        elif isinstance(state, StateMachine.CaptureState):
            self.showCapture(state)
        elif isinstance(state, StateMachine.AssembleState):
            self.showAssemble(state)
        elif isinstance(state, StateMachine.ReviewState):
            self.showReview(state)
        elif isinstance(state, StateMachine.PostprocessState):
            self.showPostprocess(state)
        elif isinstance(state, StateMachine.TeardownState):
            self.teardown(state)
