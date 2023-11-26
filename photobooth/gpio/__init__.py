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

from .. import StateMachine
from ..Threading import Workers


class Gpio:

    def __init__(self, config, comm):

        super().__init__()

        self._comm = comm
        self._gpio = None

        self._is_trigger = False
        self._is_enabled_button = config.getBool('Gpio', 'enable_button')
        self._is_enabled_light = config.getBool('Gpio', 'enable_light')

        self.initGpio(config)

    def initGpio(self, config):

        if self._is_enabled_button or self._is_enabled_light:
            self._gpio = Entities()

        if self._is_enabled_button:
            trigger_pin = config.getInt('Gpio', 'trigger_pin')
            exit_pin = config.getInt('Gpio', 'exit_pin')
            
            self._gpio.setTriggerButton(trigger_pin, self.triggerEvent)
            self._gpio.setExitButton(exit_pin, trigger_handler = self.triggerEvent, 
                                               exit_handler = self.exitEvent)
            
            logging.info(('GPIO enabled (trigger_pin=%d, '
                          'exit_pin=%d)'), trigger_pin, exit_pin)

        else:
            logging.info('GPIO buttons disabled')

        if self._is_enabled_light:
            lamp_pin = config.getInt('Gpio', 'lamp_pin')

            self._lamp = self._gpio.setLamp(lamp_pin)

            logging.info(('GPIO enabled (lamp_pin=%d)'), lamp_pin)

        else:
            logging.info('GPIO light disabled')

    def run(self):

        for state in self._comm.iter(Workers.GPIO):
            self.handleState(state)

        return True

    def handleState(self, state):

        if isinstance(state, StateMachine.IdleState):
            self.showIdle()
        elif isinstance(state, StateMachine.SlideshowState):
            self.showSlideshow()
        elif isinstance(state, StateMachine.GalleryState):
            self.showGallery()
        elif isinstance(state, StateMachine.GallerySelectState):
            self.showGallerySelect()
        elif isinstance(state, StateMachine.GreeterState):
            self.showGreeter()
        elif isinstance(state, StateMachine.CountdownState):
            self.showCountdown()
        elif isinstance(state, StateMachine.CaptureState):
            self.showCapture()
        elif isinstance(state, StateMachine.AssembleState):
            self.showAssemble()
        elif isinstance(state, StateMachine.ReviewState):
            self.showReview()
        elif isinstance(state, StateMachine.PostprocessState):
            self.showPostprocess()
        elif isinstance(state, StateMachine.TeardownState):
            self.teardown(state)

    def teardown(self, state):

        if self._is_enabled_light:
            self._gpio.teardown()

    def enableTrigger(self):

        if self._is_enabled_button:
            self._is_trigger = True

    def disableTrigger(self):

        if self._is_enabled_button:
            self._is_trigger = False

    def enableLamp(self):
            
        if self._is_enabled_light:
            self._gpio.lampOn(self._lamp)

    def disableLamp(self):
            
        if self._is_enabled_light:
            self._gpio.lampOff(self._lamp)

    def triggerEvent(self):

        if self._is_trigger:
            self.disableTrigger()
            self._comm.send(Workers.MASTER, StateMachine.GpioEvent('trigger'))

    def exitEvent(self):

        self.disableTrigger()
        self._comm.send(
            Workers.MASTER,
            StateMachine.TeardownEvent(StateMachine.TeardownEvent.WELCOME))

    def showIdle(self):

        self.enableTrigger()
        self.disableLamp()

    def showSlideshow(self):

        self.enableTrigger()
        self.disableLamp()

    def showGallery(self):

        self.disableTrigger()
        self.disableLamp()

    def showGallerySelect(self):

        self.disableTrigger()
        self.disableLamp()

    def showGreeter(self):

        self.disableTrigger()
        self.disableLamp()

    def showCountdown(self):

        self.disableTrigger()
        self.enableLamp()

    def showCapture(self):

        self.disableTrigger()
        self.enableLamp()

    def showAssemble(self):

        self.disableTrigger()
        self.disableLamp()

    def showReview(self):

        self.disableTrigger()
        self.disableLamp()

    def showPostprocess(self):

        self.disableTrigger()
        self.disableLamp()


class Entities:

    def __init__(self):

        super().__init__()

        import gpiozero
        self.LED = gpiozero.LED
        self.Button = gpiozero.Button
        self.GPIOPinInUse = gpiozero.GPIOPinInUse

        self._buttons = []
        self._lamps = []

    def teardown(self):

        for l in self._lamps:
            l.off()

    def setTriggerButton(self, bcm_pin, trigger_handler):

        try:
            self._buttons.append(self.Button(bcm_pin))
            self._buttons[-1].when_pressed = trigger_handler
        except self.GPIOPinInUse:
            logging.error('Pin {} already in use!'.format(bcm_pin))

    def setExitButton(self, bcm_pin, trigger_handler, exit_handler):

        try:
            self._buttons.append(self.Button(pin=bcm_pin, hold_time = 5))
            self._buttons[-1].when_released = trigger_handler
            self._buttons[-1].when_held = exit_handler
        except self.GPIOPinInUse:
            logging.error('Pin {} already in use!'.format(bcm_pin))

    def setLamp(self, bcm_pin):

        try:
            self._lamps.append(self.LED(bcm_pin))
            return len(self._lamps) - 1
        except self.GPIOPinInUse:
            logging.error('Pin {} already in use!'.format(bcm_pin))
            return None

    def lampOn(self, index):

        if index is not None:
            self._lamps[index].on()

    def lampOff(self, index):

        if index is not None:
            self._lamps[index].off()
