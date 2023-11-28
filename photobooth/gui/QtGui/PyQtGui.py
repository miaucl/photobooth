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
import os
import signal
from typing import Callable
from photobooth.Config import Config

from photobooth.worker import AdList

try:
    from PyQt6 import QtCore
    from PyQt6 import QtGui
    from PyQt6 import QtWidgets
except ImportError:
    logging.info("PyQt6 not found, fallback to PyQt5")
    try:
        from PyQt5 import QtCore
        from PyQt5 import QtGui
        from PyQt5 import QtWidgets
    except ImportError:
        print("PyQt5 not found, no fallback available")
        raise ImportError("No supported PyQt found")

from PIL import Image, ImageQt

from time import localtime, strftime

from ...StateMachine import CameraEvent, CountdownState, Event, GallerySelectState, GalleryState, GreeterState, GuiEvent, IdleState, PostprocessState, ReviewState, SlideshowState, StartupState, State, TeardownEvent, WelcomeState
from ...Threading import Communicator, Workers
from ...worker.PictureList import PictureList
from ...worker.Count import Count

from ..GuiSkeleton import GuiSkeleton
from ..GuiPostprocessor import GuiPostprocessor

from . import styles
from . import Frames
from . import Receiver
from . import Worker


class PyQtGui(GuiSkeleton):

    def __init__(self, argv, config: Config, comm: Communicator):

        super().__init__(comm)

        self._cfg = config

        self._initUI(argv)
        self._initReceiver()
        self._initWorker()

        # self._pictureRef = None
        # self._picture = None
        self._postprocess = GuiPostprocessor(self._cfg)


        self._createTimer()

        # Picture naming convention for assembled pictures
        path = os.path.join(config.get('Storage', 'basedir'),
                            config.get('Storage', 'basename'))
        basename = strftime(path, localtime())
        self._pictureList = PictureList(basename)
        self._adList = AdList(config.get('Storage', 'ad_prefix'), config.get('Storage', 'basedir'))
        self._pictureCount = Count(config, 'picture')
        self._printCount = Count(config, 'print')
        self._ad_every_nth_slide = config.getInt('Slideshow', 'ad_every_nth_slide')

        self._default_size = (640,440)
        self._lastslide = None
        self._slides_since_last_ad = self._ad_every_nth_slide
        
    def run(self):

        exit_code = self._app.exec()
        self._gui = None
        return exit_code

    def _initUI(self, argv):

        self._disableTrigger()

        # Load stylesheet
        style = self._cfg.get('Gui', 'style')
        filename = next((file for name, file in styles if name == style))
        with open(os.path.join(os.path.dirname(__file__), filename), 'r') as f:
            stylesheet = f.read()

        # Create application and main window
        self._app = QtWidgets.QApplication(argv)
        self._app.setStyleSheet(stylesheet)
        self._gui = PyQtMainWindow(self._cfg, self._handleKeypressEvent)

        # Listen to signals to correctly abort on ctrl+c
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Load additional fonts
        fonts = [os.path.join(os.path.dirname(__file__), 'fonts/AmaticSC-Regular.ttf'),
                 os.path.join(os.path.dirname(__file__), 'fonts/AmaticSC-Bold.ttf')]
        for font in fonts:
            id = QtGui.QFontDatabase.addApplicationFont(font)
            if id < 0:
                logging.warning(f"Font '{font}' not loaded")

    def _initReceiver(self):

        # Create receiver thread
        self._receiver = Receiver.Receiver(self._comm)
        self._receiver.notify.connect(self.handleState)
        self._receiver.start()

    def _initWorker(self):

        # Create worker thread for time consuming tasks to keep gui responsive
        self._worker = Worker.Worker(self._comm)
        self._worker.start()

    def _enableEscape(self):

        self._is_escape = True

    def _disableEscape(self):

        self._is_escape = False

    def _enableTrigger(self):

        self._is_trigger = True

    def _disableTrigger(self):

        self._is_trigger = False

    def _setWidget(self, widget):

        self._gui.setCentralWidget(widget)

    def _createTimer(self):

        self._timerStartSlideshow = QtCore.QTimer()
        self._timerStartSlideshow.timeout.connect(lambda: self._comm.send(Workers.MASTER, GuiEvent('slideshow')))
        self._timerViewSlides = QtCore.QTimer()
        self._timerViewSlides.timeout.connect(lambda: self._comm.send(Workers.GUI, GuiEvent('updateslideshow')))

    def _destroyTimer(self):
        
         QtCore.QObject.killTimer(self, self._timerStartSlideshow)
         QtCore.QObject.killTimer(self, self._timerViewSlides)

    def _newslideshowMedia(self):
        
        if (self._pictureList.counter == 0 and self._ad_every_nth_slide == 0):
            show_media = Image.new('RGBA',self._default_size,(128,128,128,0))
            text = _('No slideshow yet...')
        else:
            if (self._ad_every_nth_slide == 0 or self._slides_since_last_ad < self._ad_every_nth_slide and self._pictureList.counter > 0):
                self._slides_since_last_ad += 1
                pictureRef, _x = self._pictureList.getRandomPicture()
                while (not os.path.isfile(pictureRef.original)):
                    pictureRef, _x = self._pictureList.getRandomPicture()
                logging.debug('Picture name for slideshow {}'.format(pictureRef.original))
                show_media = Image.open(pictureRef.original)
            else:
                self._slides_since_last_ad = 0
                adname, _x = self._adList.getRandomAd()
                while (not os.path.isfile(adname)):
                    adname, _x = self._adList.getRandomAd()
                logging.debug('Add name for slideshow {}'.format(adname))
                show_media = Image.open(adname)
            text = ('')
            
        return(show_media, text)
        
    def close(self):

        if self._gui.close():
            self._comm.send(Workers.MASTER, TeardownEvent(TeardownEvent.EXIT))

    def teardown(self, state: State):

        if state.target == TeardownEvent.WELCOME:
            self._comm.send(Workers.MASTER, GuiEvent('welcome'))
        elif state.target in (TeardownEvent.EXIT, TeardownEvent.RESTART):
            self._worker.put(None)
            self._app.exit(0)

    def showError(self, state: State):

        logging.error('%s: %s', state.origin, state.message)

        err_msg = self._cfg.get('Photobooth', 'overwrite_error_message')
        if len(err_msg) > 0:
            message = err_msg
        else:
            message = 'Error: ' + state.message

        reply = QtWidgets.QMessageBox.critical(
            self._gui, state.origin, message,
            QtWidgets.QMessageBox.StandardButton.Retry | QtWidgets.QMessageBox.StandardButton.Cancel,
            QtWidgets.QMessageBox.StandardButton.Cancel)

        if reply == QtWidgets.QMessageBox.StandardButton.Retry:
            self._comm.send(Workers.MASTER, GuiEvent('retry'))
        else:
            self._comm.send(Workers.MASTER, GuiEvent('abort'))

    def showWelcome(self, state: WelcomeState):

        self._disableTrigger()
        self._disableEscape()
        self._timerViewSlides.stop()
        self._timerStartSlideshow.stop()
        version = self._cfg.get('System', 'version')
        build = self._cfg.get('System', 'build')
        event = self._cfg.get('Event', 'event')
        self._setWidget(Frames.Welcome(version, build, event,
            lambda: self._comm.send(Workers.MASTER, GuiEvent('start')),
            self._showSetDateTime, self._showSettings, self.close))
        if QtWidgets.QApplication.overrideCursor() != 0:
            QtWidgets.QApplication.restoreOverrideCursor()

    def showStartup(self, state: StartupState):

        self._disableTrigger()
        self._enableEscape()
        self._setWidget(Frames.WaitMessage(_('Starting the photobooth...')))
        if self._cfg.getBool('Gui', 'hide_cursor'):
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BlankCursor)

    def showIdle(self, state: IdleState):

        logging.info('Start Idle')

        self._enableEscape()
        self._enableTrigger()
        self._timerViewSlides.stop()
        
        event = self._cfg.get('Event', 'event')
        slideshow_time = self._cfg.getInt('Slideshow', 'start_slideshow_time') * 1000
        show_printed_counter = self._cfg.getBool('Printer', 'enable')

        self._setWidget(Frames.IdleMessage(
            event,
            self._pictureCount.get(),
            self._printCount.get() if show_printed_counter else None,
            lambda: self._comm.send(Workers.MASTER, GuiEvent('trigger')), 
            lambda: self._comm.send(Workers.MASTER, GuiEvent('gallery'))))
        
        self._timerStartSlideshow.setSingleShot(True)
        self._timerStartSlideshow.start(slideshow_time)
    
    def showSlideshow(self, state: SlideshowState):

        logging.info('Start Slideshow')

        self._timerStartSlideshow.stop()
        view_time = self._cfg.getInt('Slideshow', 'pic_slideshow_time') * 1000

        logging.info('Picture Time {}'.format(view_time) )

        self._timerViewSlides.setSingleShot(False)
        self._timerViewSlides.start(view_time)
        media, text = self._newslideshowMedia()
                
        self._setWidget(Frames.SlideshowMessage(media, text, self._cfg.getBool('Slideshow', 'fade'),
                                                lambda: self._comm.send(Workers.MASTER, GuiEvent('trigger'))))
        
    def updateSlideshow(self, event: Event):
                
        picture, _ = self._newslideshowMedia()            
        self._gui.centralWidget().alpha = 0.0
        self._gui.centralWidget().slide = picture
        self._gui.centralWidget().update()
                
    def showGallery(self, state: GalleryState):

        logging.info('Start Gallery')

        self._enableEscape()
        self._enableTrigger()

        slideshow_time = self._cfg.getInt('Slideshow', 'start_slideshow_time') * 1000

        self._timerStartSlideshow.setSingleShot(True)
        self._timerStartSlideshow.start(slideshow_time)

        if not isinstance(self._gui.centralWidget(), Frames.GalleryMessage):
            self._setWidget(Frames.GalleryMessage(self._pictureList, self._cfg.getInt("Gallery", "columns"),
                                                    lambda: self._comm.send(Workers.MASTER, GuiEvent('trigger')),
                                                    lambda x: self._comm.send(Workers.MASTER, GuiEvent('galleryselect', pictureRef=x))))
        else:
            logging.info('Skip Reinitializing Gallery')


    def showGallerySelect(self, state: GallerySelectState):

        slideshow_time = self._cfg.getInt('Slideshow', 'start_slideshow_time') * 1000
        uploads3 = {
            "enable": self._cfg.getBool('UploadS3', 'enable'),
            "link": os.path.join(self._cfg.get('UploadS3', 'bucket'), self._cfg.get('UploadS3', 'basepath'))
        }

        self._timerStartSlideshow.setSingleShot(True)
        self._timerStartSlideshow.start(slideshow_time)

        if state.action is None:
            items = self._postprocess.getAllItems()

            Frames.GallerySelectMessage(
                self._gui.centralWidget(), self._pictureList, items, self._worker, state.pictureRef, uploads3,
                lambda x: self._comm.send(Workers.MASTER, GuiEvent('postprocess', pictureRef=state.pictureRef, postprocessAction=x)),
                lambda: self._comm.send(Workers.MASTER, GuiEvent('close')),
                lambda x: self._timerStartSlideshow.start(slideshow_time))
        else:
            logging.info('Skip Reinitializing Gallery Select')
      
    def showGreeter(self, state: GreeterState):

        logging.info('Timer Remaining time"{}" '.format(self._timerStartSlideshow.remainingTime()))
        self._timerStartSlideshow.stop()
        self._enableEscape()
        self._disableTrigger()
        greeter_time = self._cfg.getInt('Photobooth', 'greeter_time') * 1000
        num_pics = state.num_shots
        # Only show something for greeter time > 0
        if greeter_time > 0: 
            self._setWidget(Frames.GreeterMessage(
                num_pics,
                lambda: self._comm.send(Workers.MASTER, GuiEvent('countdown'))))
        QtCore.QTimer.singleShot(
            greeter_time,
            lambda: self._comm.send(Workers.MASTER, GuiEvent('countdown')))

    def showCountdown(self, state: CountdownState):

        countdown_time = self._cfg.getInt('Photobooth', 'countdown_time')
        self._setWidget(Frames.CountdownMessage(
            countdown_time,
            lambda: self._comm.send(Workers.MASTER, GuiEvent('capture'))))

    def updatePreview(self, event: CameraEvent):
        shot = Image.open(event.shot)
        self._gui.centralWidget().picture = ImageQt.ImageQt(shot)
        self._gui.centralWidget().update()

    def showCapture(self, state: CameraEvent):

        self._setWidget(Frames.CaptureMessage(state.num_picture, state.num_shots))

    def showAssemble(self, state: CameraEvent):

        self._setWidget(Frames.WaitMessage(_('Processing picture...')))

    def showReview(self, state: ReviewState):

        picture = Image.open(state.picture.original)
        self._picture = ImageQt.ImageQt(picture)
        self._pictureList.findExistingFiles()
        review_time = self._cfg.getInt('Photobooth', 'display_time') * 1000
        self._setWidget(Frames.PictureMessage(self._picture))
        QtCore.QTimer.singleShot(
            review_time,
            lambda: self._comm.send(Workers.MASTER, GuiEvent('postprocess')))

    def showPostprocess(self, state: PostprocessState):

        # Refresh list, as here the new image has been saved
        self._pictureList.findExistingFiles()

        items = self._postprocess.getOptionalItems()
        postproc_t = self._cfg.getInt('Photobooth', 'postprocess_time')
        uploads3 = {
            "enable": self._cfg.getBool('UploadS3', 'enable'),
            "link": os.path.join(self._cfg.get('UploadS3', 'bucket'), self._cfg.get('UploadS3', 'basepath'))
        }

        Frames.PostprocessMessage(
            self._gui.centralWidget(), self._pictureList, items, self._worker, uploads3,
            lambda x: self._comm.send(Workers.MASTER, GuiEvent('postprocess', pictureRef=self._pictureList.getLast(), postprocessAction=x)),
            lambda: self._comm.send(Workers.MASTER, GuiEvent('idle')),
            postproc_t * 1000)

    def _handleKeypressEvent(self, event: Event):

        if self._is_escape and event.key() == QtCore.Qt.Key.Key_Escape:
            self._comm.send(Workers.MASTER,
                            TeardownEvent(TeardownEvent.WELCOME))
        elif self._is_trigger and event.key() == QtCore.Qt.Key.Key_Space:
            self._comm.send(Workers.MASTER, GuiEvent('trigger'))

    def _showSetDateTime(self):

        self._disableTrigger()
        self._disableEscape()
        self._setWidget(Frames.SetDateTime(
            self.showWelcome,
            lambda: self._comm.send(Workers.MASTER,
                                    TeardownEvent(TeardownEvent.RESTART))))

    def _showSettings(self):

        self._disableTrigger()
        self._disableEscape()
        self._setWidget(Frames.Settings(
            self._cfg, self._showSettings, self.showWelcome,
            lambda: self._comm.send(Workers.MASTER,
                                    TeardownEvent(TeardownEvent.RESTART))))


class PyQtMainWindow(QtWidgets.QMainWindow):

    def __init__(self, config: Config, keypress_handler: Callable[[Event], None]):

        super().__init__()

        self._cfg = config
        self._handle_key = keypress_handler
        self._initUI()

    def _initUI(self):

        self.setWindowTitle('Photobooth')

        if self._cfg.getBool('Gui', 'fullscreen'):
            self.showFullScreen()
        else:
            self.setFixedSize(self._cfg.getInt('Gui', 'width'),
                              self._cfg.getInt('Gui', 'height'))
            self.show()

    def closeEvent(self, e):

        reply = QtWidgets.QMessageBox.question(self, _('Confirmation'),
                                               _('Quit Photobooth?'),
                                               QtWidgets.QMessageBox.StandardButton.Yes |
                                               QtWidgets.QMessageBox.StandardButton.No,
                                               QtWidgets.QMessageBox.StandardButton.No)

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            e.accept()
        else:
            e.ignore()

    def keyPressEvent(self, event: Event):

        self._handle_key(event)
