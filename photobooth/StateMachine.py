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
from photobooth.Threading import Communicator
from photobooth.worker.PictureList import Picture, PictureRef, Shot


class Context:

    def __init__(self, communicator: Communicator, omit_welcome=False):

        super().__init__()
        self._comm = communicator
        self.is_running = False
        if omit_welcome:
            self.state = StartupState()
        else:
            self.state = WelcomeState()

    @property
    def is_running(self):

        return self._is_running

    @is_running.setter
    def is_running(self, running: bool):

        if not isinstance(running, bool):
            raise TypeError('is_running must be a bool')

        self._is_running = running

    @property
    def state(self):

        return self._state

    @state.setter
    def state(self, new_state):

        if not isinstance(new_state, State):
            raise TypeError('state must implement State')

        logging.debug('Context: New state is "{}"'.format(new_state))

        self._state = new_state
        self._comm.bcast(self._state)

    def handleEvent(self, event):

        if not isinstance(event, Event):
            raise TypeError('event must implement Event')

        logging.debug('Context: Handling event "{}"'.format(event))

        if isinstance(event, ErrorEvent):
            self.state = ErrorState(event.origin, event.message, self.state,
                                    self.is_running)
        elif isinstance(event, TeardownEvent):
            self.is_running = False
            self.state = TeardownState(event.target)
            if event.target == TeardownEvent.EXIT:
                self._comm.bcast(None)
                return 0
            elif event.target == TeardownEvent.RESTART:
                self._comm.bcast(None)
                return 123
        else:
            self.state.handleEvent(event, self)


class Event:

    def __init__(self, name: str):

        super().__init__()
        self.name = name

    def __str__(self):

        return self.name

    @property
    def name(self):

        return self._name

    @name.setter
    def name(self, name: str):

        if not isinstance(name, str):
            raise TypeError('name must be a str')

        self._name = name


class ErrorEvent(Event):

    def __init__(self, origin: str, message: str):

        super().__init__('Error')
        self.origin = origin
        self.message = message

    def __str__(self):

        return self.origin + ': ' + self.message

    @property
    def origin(self):

        return self._origin

    @origin.setter
    def origin(self, origin: str):

        if not isinstance(origin, str):
            raise TypeError('origin must be a string')

        self._origin = origin

    @property
    def message(self):

        return self._message

    @message.setter
    def message(self, message: str):

        if not isinstance(message, str):
            raise TypeError('message must be a string')

        self._message = message


class TeardownEvent(Event):

    EXIT = 0
    RESTART = 1
    WELCOME = 2

    def __init__(self, target: str):

        self._target = target
        super().__init__('Teardown({})'.format(target))

    @property
    def target(self):

        return self._target


class GuiEvent(Event):

    def __init__(self, name: str, pictureRef: PictureRef=None, postprocessAction: str=None):

        super().__init__(name)
        self._pictureRef = pictureRef
        self._postprocessAction = postprocessAction

    @property
    def pictureRef(self):

        return self._pictureRef

    @property
    def postprocessAction(self):

        return self._postprocessAction

class GpioEvent(Event):

    pass

class WebEvent(Event):

    pass


class CameraEvent(Event):

    def __init__(self, name, picture: Picture=None, shot: Shot=None, num_shots: int=None):

        super().__init__(name)
        self._picture = picture
        self._shot = shot
        self._num_shots = num_shots

    @property
    def picture(self):

        return self._picture

    @property
    def shot(self):

        return self._shot

    @property
    def num_shots(self):

        return self._num_shots

class WorkerEvent(Event):

    pass


class State:

    def __init__(self):

        super().__init__()
        self.update()

    def __str__(self):

        return type(self).__name__

    def update(self):

        pass

    def handleEvent(self, event: Event, context: Context):

        raise NotImplementedError()


class ErrorState(State):

    def __init__(self, origin, message, old_state, is_running):

        self.origin = origin
        self.message = message
        self.old_state = old_state
        self.is_running = is_running
        super().__init__()

    @property
    def origin(self):

        return self._origin

    @origin.setter
    def origin(self, origin):

        if not isinstance(origin, str):
            raise TypeError('origin must be a string')

        self._origin = origin

    @property
    def message(self):

        return self._message

    @message.setter
    def message(self, message):

        if not isinstance(message, str):
            raise TypeError('message must be a string')

        self._message = message

    @property
    def old_state(self):

        return self._old_state

    @old_state.setter
    def old_state(self, old_state):

        if not isinstance(old_state, State):
            raise TypeError('old_state must be derived from State')

        self._old_state = old_state

    @property
    def is_running(self):

        return self._is_running

    @is_running.setter
    def is_running(self, running):

        if not isinstance(running, bool):
            raise TypeError('is_running must be a bool')

        self._is_running = running

    def handleEvent(self, event: Event, context: Context):

        if isinstance(event, GuiEvent) and event.name == 'retry':
            context.state = self.old_state
            context.state.update()
        elif isinstance(event, GuiEvent) and event.name == 'abort':
            if self.is_running:
                context.state = IdleState()
            else:
                context.state = TeardownState(TeardownEvent.WELCOME)
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class TeardownState(State):

    def __init__(self, target):

        super().__init__()
        self._target = target

    @property
    def target(self):

        return self._target

    def handleEvent(self, event: Event, context: Context):

        if self._target == TeardownEvent.WELCOME:
            if isinstance(event, GuiEvent) and event.name == 'welcome':
                context.state = WelcomeState()
            else:
                raise ValueError('Unknown GuiEvent "{}"'.format(event.name))
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class WelcomeState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event: Event, context: Context):

        if isinstance(event, GuiEvent):
            if event.name == 'start':
                context.state = StartupState()
            elif event.name == 'exit':
                context.state = TeardownState(TeardownEvent.EXIT)
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class StartupState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event: Event, context: Context):

        if isinstance(event, CameraEvent) and event.name == 'ready':
            context.num_shots = event.num_shots
            context.is_running = True
            context.state = IdleState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class IdleState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event: Event, context: Context):

        if ((isinstance(event, GuiEvent) or isinstance(event, GpioEvent)) and
           event.name == 'trigger'):
            context.state = GreeterState(num_shots=context.num_shots)
        elif isinstance(event, GuiEvent) and event.name == 'slideshow':
            context.state = SlideshowState()
        elif isinstance(event, GuiEvent) and event.name == 'gallery':
            context.state = GalleryState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))

class SlideshowState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event: Event, context: Context):

        if ((isinstance(event, GuiEvent) or isinstance(event, GpioEvent)) and
           event.name == 'trigger'):
            context.state = IdleState()
        elif (isinstance(event, GuiEvent) and 
             ((event.name == 'slideshow') or (event.name == 'updateslideshow'))):
            logging.info('Picture ...' )
            pass
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))

class GalleryState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event: Event, context: Context):

        if ((isinstance(event, GuiEvent) or isinstance(event, GpioEvent)) and
           event.name == 'trigger'):
            context.state = IdleState()
        elif isinstance(event, GuiEvent) and event.name == 'slideshow':
            context.state = SlideshowState()
        elif (isinstance(event, GuiEvent) and event.name == 'galleryselect'):
            context.state = GallerySelectState(event.pictureRef)
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))

class GallerySelectState(State):

    def __init__(self, pictureRef: PictureRef=None, action: str=None):

        super().__init__()
        self._pictureRef = pictureRef
        self._action = action

    @property
    def pictureRef(self):

        return self._pictureRef

    @property
    def action(self):

        return self._action


    def handleEvent(self, event: Event, context: Context):

        if (isinstance(event, GuiEvent) and
           event.name == 'close'):
            context.state = GalleryState()
        elif isinstance(event, GuiEvent) and event.name == 'slideshow':
            context.state = SlideshowState()
        elif (isinstance(event, GuiEvent) and
           event.name == 'postprocess'):
            context.state = GallerySelectState(event.pictureRef, event.postprocessAction)
        elif (isinstance(event, GuiEvent) and event.name == 'galleryselect'):
            pass # Might be a double tap behind the popup
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))

class GreeterState(State):

    def __init__(self, num_shots: int=None):

        super().__init__()
        self._num_shots = num_shots

    def handleEvent(self, event: Event, context: Context):

        if ((isinstance(event, GuiEvent) or isinstance(event, GpioEvent)) and
           event.name == 'countdown'):
            context.state = CountdownState(1, num_shots=context.num_shots)
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))

    @property
    def num_shots(self):

        return self._num_shots

class CountdownState(State):

    def __init__(self, num_picture: int, num_shots: int=0):

        super().__init__()

        self._num_picture = num_picture
        self._num_shots = num_shots

    @property
    def num_picture(self):

        return self._num_picture

    @property
    def num_shots(self):

        return self._num_shots

    def handleEvent(self, event: Event, context: Context):

        if isinstance(event, GuiEvent) and event.name == 'countdown':
            pass
        elif isinstance(event, GuiEvent) and event.name == 'capture':
            context.state = CaptureState(self.num_picture, self.num_shots)
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class CaptureState(State):

    def __init__(self, num_picture: int, num_shots: int):

        super().__init__()

        self._num_picture = num_picture
        self._num_shots = num_shots

    @property
    def num_picture(self):

        return self._num_picture

    @property
    def num_shots(self):

        return self._num_shots

    def handleEvent(self, event: Event, context: Context):

        if isinstance(event, CameraEvent) and event.name == 'countdown':
            context.state = CountdownState(self.num_picture + 1, self._num_shots)
        elif isinstance(event, CameraEvent) and event.name == 'assemble':
            context.state = AssembleState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class AssembleState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event: Event, context: Context):

        if isinstance(event, CameraEvent) and event.name == 'review':
            context.state = ReviewState(event.picture)
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class ReviewState(State):

    def __init__(self, picture: Picture):

        super().__init__()
        self._picture = picture

    @property
    def picture(self) -> Picture:

        return self._picture

    def handleEvent(self, event: Event, context: Context):

        if isinstance(event, GuiEvent) and event.name == 'postprocess':
            context.state = PostprocessState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class PostprocessState(State):

    def __init__(self, pictureRef: PictureRef=None, action: str=None):

        super().__init__()
        self._pictureRef = pictureRef
        self._action = action

    @property
    def pictureRef(self) -> PictureRef:

        return self._pictureRef

    @property
    def action(self):

        return self._action


    def handleEvent(self, event: Event, context: Context):

        if ((isinstance(event, GuiEvent) or isinstance(event, GpioEvent)) and
           event.name == 'idle'):
            context.state = IdleState()
        elif (isinstance(event, GuiEvent) and
           event.name == 'postprocess'):
            context.state = PostprocessState(event.pictureRef, event.postprocessAction)
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))
