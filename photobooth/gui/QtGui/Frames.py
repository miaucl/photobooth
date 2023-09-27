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
import subprocess
import sys

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

from .. import modules
from ... import camera
from ... import printer
from ... import template

from . import Widgets
from . import styles


class Welcome(QtWidgets.QFrame):

    def __init__(self, start_action, set_date_action, settings_action,
                 exit_action):

        super().__init__()
        self.setObjectName('WelcomeMessage')

        self.initFrame(start_action, set_date_action, settings_action,
                       exit_action)

    def initFrame(self, start_action, set_date_action, settings_action,
                  exit_action):

        btnStart = QtWidgets.QPushButton(_('Start photobooth'))
        btnStart.clicked.connect(start_action)

        btnSetDate = QtWidgets.QPushButton(_('Set date/time'))
        btnSetDate.clicked.connect(set_date_action)

        btnSettings = QtWidgets.QPushButton(_('Settings'))
        btnSettings.clicked.connect(settings_action)

        btnQuit = QtWidgets.QPushButton(_('Quit'))
        btnQuit.clicked.connect(exit_action)

        title = QtWidgets.QLabel(_('photobooth'))

        url = 'https://github.com/miaucl/photobooth'
        link = QtWidgets.QLabel('<a href="{0}">{0}</a>'.format(url))
        link.setObjectName('WelcomeMessageLink')

        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(title)
        lay.addWidget(btnStart)
        lay.addWidget(btnSetDate)
        lay.addWidget(btnSettings)
        lay.addWidget(btnQuit)
        lay.addWidget(link)
        self.setLayout(lay)

class WaitMessage(QtWidgets.QFrame):

    def __init__(self, message):

        super().__init__()
        self.setObjectName('WaitMessage')

        self._text = message
        self._clock = Widgets.SpinningWaitClock()

        self.initFrame()

    def initFrame(self):

        lbl = QtWidgets.QLabel(self._text)
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(lbl)
        self.setLayout(lay)

    def showEvent(self, event):

        self.startTimer(100)

    def timerEvent(self, event):

        self._clock.value += 1
        self.update()

    def paintEvent(self, event):

        offset = ((self.width() - self._clock.width()) // 2,
                  (self.height() - self._clock.height()) // 2)

        painter = QtGui.QPainter(self)
        self._clock.render(painter, QtCore.QPoint(*offset),
                           self._clock.visibleRegion(),
                           QtWidgets.QWidget.RenderFlag.DrawChildren)
        painter.end()

class IdleMessage(QtWidgets.QFrame):

    def __init__(self, pictureCount, printCount, trigger_action, gallery_action):

        super().__init__()
        self.setObjectName('IdleMessage')

        self._gallery_button = _('Gallery ({})').format(pictureCount)
        self._message_label = _('Take a')
        self._message_button = _('Photo!')
        self._print_label = _('Pictures printed: {}').format(printCount) if printCount else None
        
        self._picture = None

        self.initFrame(trigger_action, gallery_action)
    
    @property
    def picture(self):

        return self._picture

    @picture.setter
    def picture(self, picture):

        if not isinstance(picture, ImageQt.ImageQt):
            self._picture = None
            raise ValueError('picture must be a ImageQt.ImageQt')
        else:
            self._picture = picture

    def initFrame(self, trigger_action, gallery_action):

        galleryBtn = QtWidgets.QPushButton(self._gallery_button)
        galleryBtn.clicked.connect(gallery_action)
        galleryBtn.setObjectName('GalleryButton')
        btnHeaderLbl = QtWidgets.QLabel(self._message_label)
        btnHeaderLbl.setObjectName('GalleryButtonHeaderLabel')
        btn = QtWidgets.QPushButton(self._message_button)
        btn.clicked.connect(trigger_action)
        if self._print_label:
            printCountLbl = QtWidgets.QLabel(self._print_label)
            printCountLbl.setObjectName('PrintLabel')

        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(btnHeaderLbl)
        lay.addWidget(btn)
        lay.addStretch(1)
        lay.addWidget(galleryBtn)
        if self._print_label:
            lay.addWidget(printCountLbl)

        container = QtWidgets.QFrame()
        container.setObjectName('IdleContainer')
        container.setLayout(lay)
        containerLay = QtWidgets.QVBoxLayout()
        containerLay.addWidget(container)
        self.setLayout(containerLay)

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)

        # background image
        if self.picture is not None:

            pix = QtGui.QPixmap.fromImage(self.picture)
            pix = pix.scaled(self.contentsRect().size(),
                             QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                             QtCore.Qt.TransformationMode.FastTransformation)
            origin = ((self.width() - pix.width()) // 2,
                  (self.height() - pix.height()) // 2)

            painter.drawPixmap(QtCore.QPoint(*origin), pix)

        painter.end()


class GreeterMessage(QtWidgets.QFrame):

    def __init__(self, num_pictures, countdown_action):

        super().__init__()
        self.setObjectName('GreeterMessage')

        self._text_label1 = _('Get ready')
        self._text_button = _('Go!')

        self._picture = None

        if num_pictures > 1:
            self._text_label2 = _('for {} photos...').format(num_pictures)
        else:
            self._text_label2 = _('for the photo')

        self.initFrame(countdown_action)

    @property
    def picture(self):

        return self._picture

    @picture.setter
    def picture(self, picture):

        if not isinstance(picture, ImageQt.ImageQt):
            self._picture = None
            raise ValueError('picture must be a ImageQt.ImageQt')
        else:
            self._picture = picture

    def initFrame(self, countdown_action):

        lbl = QtWidgets.QLabel('{} {}'.format(self._text_label1, self._text_label2))
        lbl.setObjectName('Message')
        btn = QtWidgets.QPushButton(self._text_button)
        btn.setObjectName('Button')
        btn.clicked.connect(countdown_action)

        lay = QtWidgets.QVBoxLayout()
        lay.addStretch(1)
        lay.addWidget(lbl)
        lay.addStretch(1)
        lay.addWidget(btn)

        container = QtWidgets.QFrame()
        container.setObjectName('GreeterContainer')
        container.setLayout(lay)
        containerLay = QtWidgets.QVBoxLayout()
        containerLay.addWidget(container)

        self.setLayout(containerLay)

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)

        # background image
        if self.picture is not None:

            pix = QtGui.QPixmap.fromImage(self.picture)
            pix = pix.scaled(self.contentsRect().size(),
                             QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                             QtCore.Qt.TransformationMode.FastTransformation)
            origin = ((self.width() - pix.width()) // 2,
                  (self.height() - pix.height()) // 2)

            painter.drawPixmap(QtCore.QPoint(*origin), pix)

        painter.end()


class CaptureMessage(QtWidgets.QFrame):

    def __init__(self, num_picture, num_pictures):

        super().__init__()
        self.setObjectName('PoseMessage')

        if num_pictures > 1:
            self._text = _('Photo {} of {}...').format(num_picture,
                                                         num_pictures)
        else:
            self._text = _('Taking a photo...')

        self.initFrame()

    def initFrame(self):

        lbl = QtWidgets.QLabel(self._text)
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(lbl)
        self.setLayout(lay)


class PictureMessage(QtWidgets.QFrame):

    def __init__(self, picture):

        super().__init__()
        self.setObjectName('PictureMessage')

        self._picture = picture

    def _paintPicture(self, painter):

        if isinstance(self._picture, QtGui.QImage):
            pix = QtGui.QPixmap.fromImage(self._picture)
        else:
            pix = QtGui.QPixmap(self._picture)
        pix = pix.scaled(self.contentsRect().size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                         QtCore.Qt.TransformationMode.SmoothTransformation)

        origin = ((self.width() - pix.width()) // 2,
                  (self.height() - pix.height()) // 2)
        painter.drawPixmap(QtCore.QPoint(*origin), pix)

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)
        self._paintPicture(painter)
        painter.end()


class SlideshowMessage(QtWidgets.QFrame):

    def __init__(self, slide, text, fade, trigger_action):

        super().__init__()
        self.setObjectName('SlideshowMessage')

        self._start_label = _('Touch to exit slideshow')

        self._slide = slide
        self._newslide = slide
        self._lastslide = slide
        self._text = text
        self._fade = fade
        self._alpha = 0.0
        self._trigger_action = trigger_action
        self.initFrame()
        
    def initFrame(self):
        
        startLbl = QtWidgets.QLabel(self._start_label)
        startLbl.setObjectName('StartLabel')

        lay = QtWidgets.QVBoxLayout()
        lay.addStretch(1)
        lay.addWidget(startLbl)
        self.setLayout(lay)

    def mousePressEvent(self, event):
        self._trigger_action()
            
    @property
    def slide(self):

        return self._slide

    @slide.setter
    def slide(self, slide):

        if not isinstance(slide, Image.Image):
            self._slide = None
            raise ValueError('slide must be a QtGui.QImage')
        else:
            self._slide = slide

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, alpha):
        self._alpha = alpha

    def showEvent(self, event):
        self.startTimer(25)

    def timerEvent(self, event):

        if self._slide is not None:
            if (self._fade):
                if ((self.alpha < 1.0) and 
                    (getattr(self._lastslide,"size") == getattr(self.slide,"size"))):
                    self._newslide = Image.blend(self._lastslide, self.slide, round(self.alpha,1))
                    self.alpha = round(self.alpha,1) + 0.1
                else:
                    self._newslide = self.slide 
                    self._lastslide = self.slide 
            else:
                self._newslide = self.slide 
            self.update()

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)

        if self._newslide:
            slide = ImageQt.ImageQt(self._newslide)
            slide = slide.scaled(self.contentsRect().size(),
                             QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                             QtCore.Qt.TransformationMode.FastTransformation)

            origin = ((self.width() - slide.width()) // 2,
                    (self.height() - slide.height()) // 2)
            painter.drawImage(QtCore.QPoint(*origin), slide )
            
        painter.end()


class GalleryMessage(QtWidgets.QFrame):

    def __init__(self, pictureList, columns, trigger_action, gallery_select_action):

        super().__init__()
        self.setObjectName('GalleryMessage')

        self._pictureList = pictureList
        self._columns = columns
        self._gallery_label = _('Gallery')
        self._gallery_back_button = _('← Back')

        # Reload picture list
        self._pictureList.findExistingFiles()

        self.initFrame(trigger_action, gallery_select_action)
        
    def initFrame(self, trigger_action, gallery_select_action):

        tbl = QtWidgets.QTableView()
        tbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        tbl.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tbl.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tbl.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        tbl.verticalScrollBar().setSingleStep(5)
        tbl.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        tbl.horizontalHeader().hide()
        tbl.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        tbl.verticalHeader().hide()
        QtWidgets.QScroller.grabGesture(tbl.viewport(), QtWidgets.QScroller.ScrollerGestureType.LeftMouseButtonGesture)

        dlgt = Widgets.GalleryThumbnailDelegate(gallery_select_action=gallery_select_action)

        tbl.setItemDelegate(dlgt)

        mdl = Widgets.GalleryThumbnailModel(pictureList=self._pictureList, columns=self._columns)

        tbl.setModel(mdl)

        lbl = QtWidgets.QLabel(self._gallery_label)
        btn = QtWidgets.QPushButton(self._gallery_back_button)
        btn.clicked.connect(trigger_action)
        btn.setObjectName('GalleryBackButton')

        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(btn)
        hlay.addStretch(1)
        hlay.addWidget(lbl)

        vlay = QtWidgets.QVBoxLayout()
        vlay.addLayout(hlay)
        vlay.addWidget(tbl, stretch=1)
        self.setLayout(vlay)



class GallerySelectMessage(Widgets.GallerySelectOverlay):

    def __init__(self,  parent, pictureList, items, worker, pictureId, postprocess_handle, close_handle, show_picture_handle):


        super().__init__(parent)
        self.setObjectName('GallerySelectMessage')

        self._pictureList = pictureList
        self._pictureId = pictureId
        self._previousPictureId = None
        self._nextPictureId = None
        self._info = ""

        self.initFrame(items, postprocess_handle, close_handle, show_picture_handle, worker)

    def initFrame(self, items, postprocess_handle, close_handle, show_picture_handle, worker):

        def disableAndCall(button, action):
            for i, b in enumerate(self._buttons[:-1]):
                logging.info('Disable button {}'.format(b.text()))
                b.setEnabled(False)
                b.update()
            self._label.setText(_('{} in progress'.format(button.text())))
            self._label.update()
            worker.put(lambda: postprocess_handle(action))

        def createButton(item):
            button = QtWidgets.QPushButton(item.label)
            button.clicked.connect(lambda: disableAndCall(button, item.action))
            return button

        self._buttons = [createButton(item) for item in items]
        self._buttons.append(QtWidgets.QPushButton(_('Close')))
        self._buttons[-1].clicked.connect(close_handle)
        self._buttons[-1].clicked.connect(self.close)

        button_lay = QtWidgets.QGridLayout()
        for i, button in enumerate(self._buttons):
            pos = divmod(i, 2)
            button_lay.addWidget(button, *pos)


        nextBtn = QtWidgets.QPushButton('←')
        previousBtn = QtWidgets.QPushButton('→')
        self._label = QtWidgets.QLabel(self._info)

        def updatePicture(newPictureId):
            if newPictureId:
                self._pictureId = newPictureId
                self._previousPictureId = self._pictureList.getPreviousFilename(newPictureId)
                self._nextPictureId = self._pictureList.getNextFilename(newPictureId)
                nextBtn.setEnabled(self._nextPictureId != None)
                previousBtn.setEnabled(self._previousPictureId != None)
                self.update()
                show_picture_handle(newPictureId)
        updatePicture(self._pictureId)

        nextBtn.clicked.connect(lambda: updatePicture(self._nextPictureId))            
        previousBtn.clicked.connect(lambda: updatePicture(self._previousPictureId))

        headerLayout = QtWidgets.QHBoxLayout()
        headerLayout.addWidget(nextBtn)
        headerLayout.addWidget(self._label, stretch=1)
        headerLayout.addWidget(previousBtn)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(headerLayout, stretch=0)
        layout.addStretch(1)
        layout.addLayout(button_lay)
        self.setLayout(layout)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)

        try:
            image = ImageQt.ImageQt(Image.open(self._pictureId))
            image = image.scaled(self.contentsRect().size(),
                             QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                             QtCore.Qt.TransformationMode.FastTransformation)

            origin = ((self.width() - image.width()) // 2,
                    (self.height() - image.height()) // 2)
            painter.drawImage(QtCore.QPoint(*origin), image)
        except:
            return None
            
        painter.end()



class CountdownMessage(QtWidgets.QFrame):

    def __init__(self, time, action):

        super().__init__()
        self.setObjectName('CountdownMessage')

        self._step_size = 50
        self._value = time * (1000 // self._step_size)
        self._action = action
        self._picture = None

        self._initProgressBar(time)

    @property
    def value(self):

        return self._value

    @value.setter
    def value(self, value):

        self._value = value

    @property
    def picture(self):

        return self._picture

    @picture.setter
    def picture(self, picture):

        if not isinstance(picture, ImageQt.ImageQt):
            self._picture = None
            raise ValueError('picture must be a ImageQt.ImageQt')
        else:
            self._picture = picture

    def _initProgressBar(self, time):

        self._bar = Widgets.RoundProgressBar(0, time, time)
        self._bar.setFixedSize(160, 160)

    def _updateProgressBar(self):

        self._bar.value = self._value / (1000 // self._step_size)

    def showEvent(self, event):

        self._timer = self.startTimer(self._step_size)

    def timerEvent(self, event):

        self.value -= 1

        if self.value == 0:
            self.killTimer(self._timer)
            self._action()
        else:
            self._updateProgressBar()
            self.update()

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)

        # background image and countdown
        if self.picture is not None:

            pix = QtGui.QPixmap.fromImage(self.picture)
            pix = pix.scaled(self.contentsRect().size(),
                             QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                             QtCore.Qt.TransformationMode.FastTransformation)
            origin = ((self.width() - pix.width()) // 2,
                      (self.height() - pix.height()) // 2)
            painter.drawPixmap(QtCore.QPoint(*origin), pix)

            # Center (old implementation)
            # offset = ((self.width() - self._bar.width()) // 2,
            #           (self.height() - self._bar.height()) // 2)
            
            # Bottom right of the preview
            offset = ((self.width() - ((self.width() - pix.width()) // 2) - self._bar.width()),
                      (self.height() - ((self.height() - pix.height()) // 2) - self._bar.height()))
            self._bar.render(painter, QtCore.QPoint(*offset),
                            self._bar.visibleRegion(),
                            QtWidgets.QWidget.RenderFlag.DrawChildren)

        painter.end()


class PostprocessMessage(Widgets.TransparentOverlay):

    def __init__(self, parent, items, worker, postprocess_handle, idle_handle,
                 timeout=None, timeout_handle=None):

        if timeout_handle is None:
            timeout_handle = idle_handle

        super().__init__(parent, timeout, timeout_handle)
        self.setObjectName('PostprocessMessage')
        self.initFrame(items, postprocess_handle, idle_handle, worker)

    def initFrame(self, items, postprocess_handle, idle_handle, worker):

        def disableAndCall(button, action):
            for i, b in enumerate(self._buttons):
                logging.info('Disable button {}'.format(b.text()))
                b.setEnabled(False)
                b.update()
            self._label.setText(_('{} in progress'.format(button.text())))
            self._label.update()
            worker.put(lambda: postprocess_handle(action))
            worker.put(idle_handle)
            # worker.put(self.close)

        def createButton(item):
            button = QtWidgets.QPushButton(item.label)
            button.clicked.connect(lambda: disableAndCall(button, item.action))
            return button

        self._buttons = [createButton(item) for item in items]
        self._buttons.append(QtWidgets.QPushButton(_('Next photo')))
        self._buttons[-1].clicked.connect(idle_handle)

        button_lay = QtWidgets.QGridLayout()
        for i, button in enumerate(self._buttons):
            pos = divmod(i, 2)
            button_lay.addWidget(button, *pos)

        layout = QtWidgets.QVBoxLayout()
        self._label = QtWidgets.QLabel(_('Happy with your picture?'))
        layout.addWidget(self._label, stretch=0)
        layout.addStretch(1)
        layout.addLayout(button_lay)
        self.setLayout(layout)


class SetDateTime(QtWidgets.QFrame):

    def __init__(self, cancel_action, restart_action):

        super().__init__()

        self._cancelAction = cancel_action
        self._restartAction = restart_action

        self.initFrame()

    def initFrame(self):

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.createForm())
        layout.addStretch(1)
        layout.addWidget(self.createButtons())
        self.setLayout(layout)

    def createForm(self):

        self._date_widget = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self._date_widget.setCalendarPopup(True)

        self._time_widget = QtWidgets.QTimeEdit(QtCore.QTime.currentTime())

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Date:'), self._date_widget)
        layout.addRow(_('Time:'), self._time_widget)

        widget = QtWidgets.QGroupBox()
        widget.setTitle(_('Set system date and time:'))
        widget.setLayout(layout)
        return widget

    def createButtons(self):

        layout = QtWidgets.QHBoxLayout()
        layout.addStretch(1)

        btnSave = QtWidgets.QPushButton(_('Save and restart'))
        btnSave.clicked.connect(self.saveAndRestart)
        layout.addWidget(btnSave)

        btnCancel = QtWidgets.QPushButton(_('Cancel'))
        btnCancel.clicked.connect(self._cancelAction)
        layout.addWidget(btnCancel)

        widget = QtWidgets.QGroupBox()
        widget.setLayout(layout)
        return widget

    def saveAndRestart(self):

        if os.name != 'posix':
            raise NotImplementedError(('Setting time/date not yet implemented '
                                       'for OS type "{}"'.format(os.name)))

        date = self._date_widget.date()
        time = self._time_widget.time()
        datetime = '{:04d}{:02d}{:02d} {:02d}:{:02d}'.format(date.year(),
                                                             date.month(),
                                                             date.day(),
                                                             time.hour(),
                                                             time.minute())
        logging.info(['sudo', '-A', 'date', '-s', datetime])
        logging.info('Setting date to "{}"'.format(datetime))

        try:
            subprocess.run(['sudo', '-A', 'date', '-s', datetime],
                           stderr=subprocess.PIPE).check_returncode()
        except subprocess.CalledProcessError as e:
            cmd = ' '.join(e.cmd)
            msg = e.stderr.decode(sys.stdout.encoding)
            logging.error('Failed to execute "{}": "{}"'.format(cmd, msg))

        self._restartAction()


class Settings(QtWidgets.QFrame):

    def __init__(self, config, reload_action, cancel_action, restart_action):

        super().__init__()

        self._cfg = config
        self._reloadAction = reload_action
        self._cancelAction = cancel_action
        self._restartAction = restart_action

        self.initFrame()

    def init(self, category):

        self._widgets[category] = {}

    def add(self, category, key, value):

        self._widgets[category][key] = value

    def get(self, category, key):

        return self._widgets[category][key]

    def initFrame(self):

        self._widgets = {}

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.createTabs())
        layout.addWidget(self.createButtons())
        self.setLayout(layout)

    def createTabs(self):

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.createGuiSettings(), _('Interface'))
        tabs.addTab(self.createPhotoboothSettings(), _('Photobooth'))
        tabs.addTab(self.createCameraSettings(), _('Camera'))
        tabs.addTab(self.createTemplateSettings(), _('Template'))
        tabs.addTab(self.createPictureSettings(), _('Picture'))
        tabs.addTab(self.createSlideshowSettings(), _('Slideshow'))
        tabs.addTab(self.createGallerySettings(), _('Gallery'))
        tabs.addTab(self.createStorageSettings(), _('Storage'))
        tabs.addTab(self.createGpioSettings(), _('GPIO'))
        tabs.addTab(self.createPrinterSettings(), _('Printer'))
        tabs.addTab(self.createMailerSettings(), _('Mailer'))
        tabs.addTab(self.createUploadSettings(), _('Upload'))
        return tabs

    def createButtons(self):

        layout = QtWidgets.QHBoxLayout()
        layout.addStretch(1)

        btnSave = QtWidgets.QPushButton(_('Save and restart'))
        btnSave.clicked.connect(self.storeConfigAndRestart)
        layout.addWidget(btnSave)

        btnCancel = QtWidgets.QPushButton(_('Cancel'))
        btnCancel.clicked.connect(self._cancelAction)
        layout.addWidget(btnCancel)

        btnRestore = QtWidgets.QPushButton(_('Restore defaults'))
        btnRestore.clicked.connect(self.restoreDefaults)
        layout.addWidget(btnRestore)

        widget = QtWidgets.QGroupBox()
        widget.setLayout(layout)
        return widget

    def createModuleComboBox(self, module_list, current_module):

        cb = QtWidgets.QComboBox()
        for m in module_list:
            cb.addItem(m[0])

        idx = [x for x, m in enumerate(module_list) if m[0] == current_module]
        cb.setCurrentIndex(idx[0] if len(idx) > 0 else -1)

        # Fix bug in Qt to allow changing the items in a stylesheet
        delegate = QtWidgets.QStyledItemDelegate()
        cb.setItemDelegate(delegate)

        return cb

    def createGuiSettings(self):

        self.init('Gui')

        fullscreen = QtWidgets.QCheckBox()
        fullscreen.setChecked(self._cfg.getBool('Gui', 'fullscreen'))
        self.add('Gui', 'fullscreen', fullscreen)

        module = self.createModuleComboBox(modules,
                                           self._cfg.get('Gui', 'module'))
        self.add('Gui', 'module', module)

        width = QtWidgets.QSpinBox()
        width.setRange(100, 999999)
        width.setValue(self._cfg.getInt('Gui', 'width'))
        self.add('Gui', 'width', width)

        height = QtWidgets.QSpinBox()
        height.setRange(100, 999999)
        height.setValue(self._cfg.getInt('Gui', 'height'))
        self.add('Gui', 'height', height)

        cursor = QtWidgets.QCheckBox()
        cursor.setChecked(self._cfg.getBool('Gui', 'hide_cursor'))
        self.add('Gui', 'hide_cursor', cursor)

        style = self.createModuleComboBox(styles,
                                          self._cfg.get('Gui', 'style'))
        self.add('Gui', 'style', style)

        lay_size = QtWidgets.QHBoxLayout()
        lay_size.addWidget(width)
        lay_size.addWidget(QtWidgets.QLabel('x'))
        lay_size.addWidget(height)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Enable fullscreen:'), fullscreen)
        layout.addRow(_('Gui module:'), module)
        layout.addRow(_('Window size [px]:'), lay_size)
        layout.addRow(_('Hide cursor:'), cursor)
        layout.addRow(_('Appearance:'), style)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createPhotoboothSettings(self):

        self.init('Photobooth')

        preview = QtWidgets.QCheckBox()
        preview.setChecked(self._cfg.getBool('Photobooth', 'show_preview'))
        self.add('Photobooth', 'show_preview', preview)

        greet_time = QtWidgets.QSpinBox()
        greet_time.setRange(0, 1000)
        greet_time.setValue(self._cfg.getInt('Photobooth', 'greeter_time'))
        self.add('Photobooth', 'greeter_time', greet_time)

        count_time = QtWidgets.QSpinBox()
        count_time.setRange(0, 1000)
        count_time.setValue(self._cfg.getInt('Photobooth', 'countdown_time'))
        self.add('Photobooth', 'countdown_time', count_time)

        displ_time = QtWidgets.QSpinBox()
        displ_time.setRange(0, 1000)
        displ_time.setValue(self._cfg.getInt('Photobooth', 'display_time'))
        self.add('Photobooth', 'display_time', displ_time)

        postproc_time = QtWidgets.QSpinBox()
        postproc_time.setRange(0, 1000)
        postproc_time.setValue(self._cfg.getInt('Photobooth',
                                                'postprocess_time'))
        self.add('Photobooth', 'postprocess_time', postproc_time)

        err_msg = QtWidgets.QLineEdit(
            self._cfg.get('Photobooth', 'overwrite_error_message'))
        self.add('Photobooth', 'overwrite_error_message', err_msg)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Show preview during countdown:'), preview)
        layout.addRow(_('Greeter time before countdown [s]:'), greet_time)
        layout.addRow(_('Countdown time [s]:'), count_time)
        layout.addRow(_('Picture display time [s]:'), displ_time)
        layout.addRow(_('Postprocess timeout [s]:'), postproc_time)
        layout.addRow(_('Overwrite displayed error message:'), err_msg)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createCameraSettings(self):

        self.init('Camera')

        module = self.createModuleComboBox(camera.modules,
                                           self._cfg.get('Camera', 'module'))
        self.add('Camera', 'module', module)

        self.rot_vals_ = (0, 90, 180, 270)
        cur_rot = self._cfg.getInt('Camera', 'rotation')

        rotation = QtWidgets.QComboBox()
        for r in self.rot_vals_:
            rotation.addItem(str(r))

        idx = [x for x, r in enumerate(self.rot_vals_) if r == cur_rot]
        rotation.setCurrentIndex(idx[0] if len(idx) > 0 else -1)

        # Fix bug in Qt to allow changing the items in a stylesheet
        delegate = QtWidgets.QStyledItemDelegate()
        rotation.setItemDelegate(delegate)

        self.add('Camera', 'rotation', rotation)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Camera module:'), module)
        layout.addRow(_('Camera rotation:'), rotation)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createTemplateSettings(self):

        self.init('Template')

        module = self.createModuleComboBox(template.modules,
                                           self._cfg.get('Template', 'module'))
        self.add('Template', 'module', module)

        tf_widget = QtWidgets.QLineEdit(self._cfg.get('Template', 'template'))
        self.add('Template', 'template', tf_widget)

        def file_dialog():
            dialog = QtWidgets.QFileDialog.getOpenFileName
            tf_widget.setText(dialog(self, _('Select file'), os.path.expanduser('~'),
                              'XML Templates (*.xml)')[0])

        file_button = QtWidgets.QPushButton(_('Select file'))
        file_button.clicked.connect(file_dialog)

        lay_templ_file = QtWidgets.QHBoxLayout()
        lay_templ_file.addWidget(tf_widget)
        lay_templ_file.addWidget(file_button)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Template module:'), module)
        layout.addRow(_('Fancy template file:'), lay_templ_file)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createPictureSettings(self):

        self.init('Picture')

        num_x = QtWidgets.QSpinBox()
        num_x.setRange(1, 99)
        num_x.setValue(self._cfg.getInt('Picture', 'num_x'))
        self.add('Picture', 'num_x', num_x)

        num_y = QtWidgets.QSpinBox()
        num_y.setRange(1, 99)
        num_y.setValue(self._cfg.getInt('Picture', 'num_y'))
        self.add('Picture', 'num_y', num_y)

        size_x = QtWidgets.QSpinBox()
        size_x.setRange(1, 999999)
        size_x.setValue(self._cfg.getInt('Picture', 'size_x'))
        self.add('Picture', 'size_x', size_x)

        size_y = QtWidgets.QSpinBox()
        size_y.setRange(1, 999999)
        size_y.setValue(self._cfg.getInt('Picture', 'size_y'))
        self.add('Picture', 'size_y', size_y)

        inner_dist_x = QtWidgets.QSpinBox()
        inner_dist_x.setRange(0, 999999)
        inner_dist_x.setValue(self._cfg.getInt('Picture', 'inner_dist_x'))
        self.add('Picture', 'inner_dist_x', inner_dist_x)

        inner_dist_y = QtWidgets.QSpinBox()
        inner_dist_y.setRange(0, 999999)
        inner_dist_y.setValue(self._cfg.getInt('Picture', 'inner_dist_y'))
        self.add('Picture', 'inner_dist_y', inner_dist_y)

        outer_dist_x = QtWidgets.QSpinBox()
        outer_dist_x.setRange(0, 999999)
        outer_dist_x.setValue(self._cfg.getInt('Picture', 'outer_dist_x'))
        self.add('Picture', 'outer_dist_x', outer_dist_x)

        outer_dist_y = QtWidgets.QSpinBox()
        outer_dist_y.setRange(0, 999999)
        outer_dist_y.setValue(self._cfg.getInt('Picture', 'outer_dist_y'))
        self.add('Picture', 'outer_dist_y', outer_dist_y)

        skip = QtWidgets.QLineEdit(self._cfg.get('Picture', 'skip'))
        self.add('Picture', 'skip', skip)

        bg = QtWidgets.QLineEdit(self._cfg.get('Picture', 'background'))
        self.add('Picture', 'background', bg)

        lay_num = QtWidgets.QHBoxLayout()
        lay_num.addWidget(num_x)
        lay_num.addWidget(QtWidgets.QLabel('x'))
        lay_num.addWidget(num_y)

        lay_size = QtWidgets.QHBoxLayout()
        lay_size.addWidget(size_x)
        lay_size.addWidget(QtWidgets.QLabel('x'))
        lay_size.addWidget(size_y)

        lay_inner_dist = QtWidgets.QHBoxLayout()
        lay_inner_dist.addWidget(inner_dist_x)
        lay_inner_dist.addWidget(QtWidgets.QLabel('x'))
        lay_inner_dist.addWidget(inner_dist_y)

        lay_outer_dist = QtWidgets.QHBoxLayout()
        lay_outer_dist.addWidget(outer_dist_x)
        lay_outer_dist.addWidget(QtWidgets.QLabel('x'))
        lay_outer_dist.addWidget(outer_dist_y)

        def file_dialog():
            dialog = QtWidgets.QFileDialog.getOpenFileName
            bg.setText(dialog(self, _('Select file'), os.path.expanduser('~'),
                              'Images (*.jpg *.png)')[0])

        file_button = QtWidgets.QPushButton(_('Select file'))
        file_button.clicked.connect(file_dialog)

        lay_file = QtWidgets.QHBoxLayout()
        lay_file.addWidget(bg)
        lay_file.addWidget(file_button)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Number of shots per picture:'), lay_num)
        layout.addRow(_('Size of assembled picture [px]:'), lay_size)
        layout.addRow(_('Min. distance between shots [px]:'), lay_inner_dist)
        layout.addRow(_('Min. distance border to shots [px]:'), lay_outer_dist)
        layout.addRow(_('Skip pictures:'), skip)
        layout.addRow(_('Background image:'), lay_file)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createSlideshowSettings(self):

        self.init('Slideshow')
        
        box_start_slideshow_time = QtWidgets.QSpinBox()
        box_start_slideshow_time.setRange(3, 100)
        box_start_slideshow_time.setValue(self._cfg.getInt('Slideshow', 'start_slideshow_time'))
        self.add('Slideshow', 'start_slideshow_time', box_start_slideshow_time)

        box_pic_slideshow_time = QtWidgets.QSpinBox()
        box_pic_slideshow_time.setRange(5, 100)
        box_pic_slideshow_time.setValue(self._cfg.getInt('Slideshow', 'pic_slideshow_time'))
        self.add('Slideshow', 'pic_slideshow_time', box_pic_slideshow_time)


        fade_slideshow = QtWidgets.QCheckBox()
        fade_slideshow.setChecked(self._cfg.getBool('Slideshow', 'fade'))
        self.add('Slideshow', 'fade', fade_slideshow)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Wait for Slideshow time [s]:'), box_start_slideshow_time)
        layout.addRow(_('Wait for change pictures time [s]:'), box_pic_slideshow_time)
        layout.addRow(_('Wait for change pictures time [s]:'), fade_slideshow)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createGallerySettings(self):

        self.init('Gallery')
        
        gallery_columns = QtWidgets.QSpinBox()
        gallery_columns.setRange(1, 18)
        gallery_columns.setValue(self._cfg.getInt('Gallery', 'columns'))
        self.add('Gallery', 'columns', gallery_columns)

        size_x = QtWidgets.QSpinBox()
        size_x.setRange(1, 999999)
        size_x.setValue(self._cfg.getInt('Gallery', 'size_x'))
        self.add('Gallery', 'size_x', size_x)

        size_y = QtWidgets.QSpinBox()
        size_y.setRange(1, 999999)
        size_y.setValue(self._cfg.getInt('Gallery', 'size_y'))
        self.add('Gallery', 'size_y', size_y)

        lay_size = QtWidgets.QHBoxLayout()
        lay_size.addWidget(size_x)
        lay_size.addWidget(QtWidgets.QLabel('x'))
        lay_size.addWidget(size_y)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Columns to show in gallery:'), gallery_columns)
        layout.addRow(_('Size of assembled picture [px]:'), lay_size)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createStorageSettings(self):

        self.init('Storage')

        basedir = QtWidgets.QLineEdit(self._cfg.get('Storage', 'basedir'))
        basename = QtWidgets.QLineEdit(self._cfg.get('Storage', 'basename'))
        self.add('Storage', 'basedir', basedir)
        self.add('Storage', 'basename', basename)

        keep_pictures = QtWidgets.QCheckBox()
        keep_pictures.setChecked(self._cfg.getBool('Storage', 'keep_pictures'))
        self.add('Storage', 'keep_pictures', keep_pictures)

        def directory_dialog():
            dialog = QtWidgets.QFileDialog.getExistingDirectory
            basedir.setText(dialog(self, _('Select directory'),
                                   os.path.expanduser('~'),
                                   QtWidgets.QFileDialog.ShowDirsOnly))

        dir_button = QtWidgets.QPushButton(_('Select directory'))
        dir_button.clicked.connect(directory_dialog)

        lay_dir = QtWidgets.QHBoxLayout()
        lay_dir.addWidget(basedir)
        lay_dir.addWidget(dir_button)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Output directory (strftime possible):'), lay_dir)
        layout.addRow(_('Basename of files (strftime possible):'), basename)
        layout.addRow(_('Keep single shots:'), keep_pictures)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createGpioSettings(self):

        self.init('Gpio')

        enable_button = QtWidgets.QCheckBox()
        enable_button.setChecked(self._cfg.getBool('Gpio', 'enable_button'))
        self.add('Gpio', 'enable_button', enable_button)

        exit_pin = QtWidgets.QSpinBox()
        exit_pin.setRange(1, 40)
        exit_pin.setValue(self._cfg.getInt('Gpio', 'exit_pin'))
        self.add('Gpio', 'exit_pin', exit_pin)

        trig_pin = QtWidgets.QSpinBox()
        trig_pin.setRange(1, 40)
        trig_pin.setValue(self._cfg.getInt('Gpio', 'trigger_pin'))
        self.add('Gpio', 'trigger_pin', trig_pin)

        enable_light = QtWidgets.QCheckBox()
        enable_light.setChecked(self._cfg.getBool('Gpio', 'enable_light'))
        self.add('Gpio', 'enable_light', enable_light)

        lamp_pin = QtWidgets.QSpinBox()
        lamp_pin.setRange(1, 40)
        lamp_pin.setValue(self._cfg.getInt('Gpio', 'lamp_pin'))
        self.add('Gpio', 'lamp_pin', lamp_pin)

        chan_r_pin = QtWidgets.QSpinBox()
        chan_r_pin.setRange(1, 40)
        chan_r_pin.setValue(self._cfg.getInt('Gpio', 'chan_r_pin'))
        self.add('Gpio', 'chan_r_pin', chan_r_pin)

        chan_g_pin = QtWidgets.QSpinBox()
        chan_g_pin.setRange(1, 40)
        chan_g_pin.setValue(self._cfg.getInt('Gpio', 'chan_g_pin'))
        self.add('Gpio', 'chan_g_pin', chan_g_pin)

        chan_b_pin = QtWidgets.QSpinBox()
        chan_b_pin.setRange(1, 40)
        chan_b_pin.setValue(self._cfg.getInt('Gpio', 'chan_b_pin'))
        self.add('Gpio', 'chan_b_pin', chan_b_pin)

        lay_rgb = QtWidgets.QHBoxLayout()
        lay_rgb.addWidget(chan_r_pin)
        lay_rgb.addWidget(chan_g_pin)
        lay_rgb.addWidget(chan_b_pin)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Enable GPIO buttons:'), enable_button)
        layout.addRow(_('Exit button pin (BCM numbering):'), exit_pin)
        layout.addRow(_('Trigger button pin (BCM numbering):'), trig_pin)
        layout.addRow(_('Enable GPIO light:'), enable_light)
        layout.addRow(_('Idle lamp pin (BCM numbering):'), lamp_pin)
        layout.addRow(_('RGB LED pins (BCM numbering):'), lay_rgb)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createPrinterSettings(self):

        self.init('Printer')

        enable = QtWidgets.QCheckBox()
        enable.setChecked(self._cfg.getBool('Printer', 'enable'))
        self.add('Printer', 'enable', enable)

        confirmation = QtWidgets.QCheckBox()
        confirmation.setChecked(self._cfg.getBool('Printer', 'confirmation'))
        self.add('Printer', 'confirmation', confirmation)

        module = self.createModuleComboBox(printer.modules,
                                           self._cfg.get('Printer', 'module'))
        self.add('Printer', 'module', module)

        width = QtWidgets.QSpinBox()
        width.setRange(0, 999999)
        width.setValue(self._cfg.getInt('Printer', 'width'))
        height = QtWidgets.QSpinBox()
        height.setRange(0, 999999)
        height.setValue(self._cfg.getInt('Printer', 'height'))
        self.add('Printer', 'width', width)
        self.add('Printer', 'height', height)

        lay_size = QtWidgets.QHBoxLayout()
        lay_size.addWidget(width)
        lay_size.addWidget(QtWidgets.QLabel('x'))
        lay_size.addWidget(height)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Enable printing:'), enable)
        layout.addRow(_('Module:'), module)
        layout.addRow(_('Ask for confirmation before printing:'), confirmation)
        layout.addRow(_('Paper size [mm]:'), lay_size)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createMailerSettings(self):

        self.init('Mailer')

        enable = QtWidgets.QCheckBox()
        enable.setChecked(self._cfg.getBool('Mailer', 'enable'))
        self.add('Mailer', 'enable', enable)

        sender = QtWidgets.QLineEdit(self._cfg.get('Mailer', 'sender'))
        self.add('Mailer', 'sender', sender)
        recipient = QtWidgets.QLineEdit(self._cfg.get('Mailer', 'recipient'))
        self.add('Mailer', 'recipient', recipient)

        subject = QtWidgets.QLineEdit(self._cfg.get('Mailer', 'subject'))
        self.add('Mailer', 'subject', subject)
        message = QtWidgets.QLineEdit(self._cfg.get('Mailer', 'message'))
        self.add('Mailer', 'message', message)

        server = QtWidgets.QLineEdit(self._cfg.get('Mailer', 'server'))
        self.add('Mailer', 'server', server)
        port = QtWidgets.QSpinBox()
        port.setRange(1, 999999)
        port.setValue(self._cfg.getInt('Mailer', 'port'))
        self.add('Mailer', 'port', port)
        use_tls = QtWidgets.QCheckBox()
        use_tls.setChecked(self._cfg.getBool('Mailer', 'use_tls'))
        self.add('Mailer', 'use_tls', use_tls)

        use_auth = QtWidgets.QCheckBox()
        use_auth.setChecked(self._cfg.getBool('Mailer', 'use_auth'))
        self.add('Mailer', 'use_auth', use_auth)
        user = QtWidgets.QLineEdit(self._cfg.get('Mailer', 'user'))
        self.add('Mailer', 'user', user)
        password = QtWidgets.QLineEdit(self._cfg.get('Mailer', 'password'))
        self.add('Mailer', 'password', password)

        lay_server = QtWidgets.QHBoxLayout()
        lay_server.addWidget(server)
        lay_server.addWidget(QtWidgets.QLabel('Port:'))
        lay_server.addWidget(port)
        lay_server.addWidget(QtWidgets.QLabel('Use TLS:'))
        lay_server.addWidget(use_tls)

        lay_auth = QtWidgets.QHBoxLayout()
        lay_auth.addWidget(use_auth)
        lay_auth.addWidget(QtWidgets.QLabel('Username:'))
        lay_auth.addWidget(user)
        lay_auth.addWidget(QtWidgets.QLabel('Password:'))
        lay_auth.addWidget(password)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Enable Mailer:'), enable)
        layout.addRow(_('Sender mail address:'), sender)
        layout.addRow(_('Recipient mail address:'), recipient)
        layout.addRow(_('Mail subject'), subject)
        layout.addRow(_('Mail message:'), message)
        layout.addRow(_('SMTP server:'), lay_server)
        layout.addRow(_('Server requires auth:'), lay_auth)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def createUploadSettings(self):

        self.init('UploadWebdav')

        enable = QtWidgets.QCheckBox()
        enable.setChecked(self._cfg.getBool('UploadWebdav', 'enable'))
        self.add('UploadWebdav', 'enable', enable)

        url = QtWidgets.QLineEdit(self._cfg.get('UploadWebdav', 'url'))
        self.add('UploadWebdav', 'url', url)

        use_auth = QtWidgets.QCheckBox()
        use_auth.setChecked(self._cfg.getBool('UploadWebdav', 'use_auth'))
        self.add('UploadWebdav', 'use_auth', use_auth)
        user = QtWidgets.QLineEdit(self._cfg.get('UploadWebdav', 'user'))
        self.add('UploadWebdav', 'user', user)
        password = QtWidgets.QLineEdit(self._cfg.get('UploadWebdav',
                                                     'password'))
        self.add('UploadWebdav', 'password', password)

        lay_auth = QtWidgets.QHBoxLayout()
        lay_auth.addWidget(use_auth)
        lay_auth.addWidget(QtWidgets.QLabel('Username:'))
        lay_auth.addWidget(user)
        lay_auth.addWidget(QtWidgets.QLabel('Password:'))
        lay_auth.addWidget(password)

        layout = QtWidgets.QFormLayout()
        layout.addRow(_('Enable WebDAV upload:'), enable)
        layout.addRow(_('URL (folder must exist):'), url)
        layout.addRow(_('Server requires auth:'), lay_auth)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def storeConfigAndRestart(self):

        self._cfg.set('Gui', 'fullscreen',
                      str(self.get('Gui', 'fullscreen').isChecked()))
        self._cfg.set('Gui', 'module',
                      modules[self.get('Gui', 'module').currentIndex()][0])
        self._cfg.set('Gui', 'width', self.get('Gui', 'width').text())
        self._cfg.set('Gui', 'height', self.get('Gui', 'height').text())
        self._cfg.set('Gui', 'hide_cursor',
                      str(self.get('Gui', 'hide_cursor').isChecked()))
        self._cfg.set('Gui', 'style',
                      styles[self.get('Gui', 'style').currentIndex()][0])

        self._cfg.set('Photobooth', 'show_preview',
                      str(self.get('Photobooth', 'show_preview').isChecked()))
        self._cfg.set('Photobooth', 'greeter_time',
                      str(self.get('Photobooth', 'greeter_time').text()))
        self._cfg.set('Photobooth', 'countdown_time',
                      str(self.get('Photobooth', 'countdown_time').text()))
        self._cfg.set('Photobooth', 'display_time',
                      str(self.get('Photobooth', 'display_time').text()))
        self._cfg.set('Photobooth', 'postprocess_time',
                      str(self.get('Photobooth', 'postprocess_time').text()))
        self._cfg.set('Photobooth', 'overwrite_error_message',
                      self.get('Photobooth', 'overwrite_error_message').text())

        self._cfg.set('Camera', 'module',
                      camera.modules[self.get('Camera',
                                              'module').currentIndex()][0])
        self._cfg.set('Camera', 'rotation', str(
            self.rot_vals_[self.get('Camera', 'rotation').currentIndex()]))

        self._cfg.set('Template', 'module', template.modules[self.get('Template',
                                              'module').currentIndex()][0])
        self._cfg.set('Template', 'template', self.get('Template', 'template').text())

        self._cfg.set('Picture', 'num_x', self.get('Picture', 'num_x').text())
        self._cfg.set('Picture', 'num_y', self.get('Picture', 'num_y').text())
        self._cfg.set('Picture', 'size_x',
                      self.get('Picture', 'size_x').text())
        self._cfg.set('Picture', 'size_y',
                      self.get('Picture', 'size_y').text())
        self._cfg.set('Picture', 'inner_dist_x',
                      self.get('Picture', 'inner_dist_x').text())
        self._cfg.set('Picture', 'inner_dist_y',
                      self.get('Picture', 'inner_dist_y').text())
        self._cfg.set('Picture', 'outer_dist_x',
                      self.get('Picture', 'outer_dist_x').text())
        self._cfg.set('Picture', 'outer_dist_y',
                      self.get('Picture', 'outer_dist_y').text())
        self._cfg.set('Picture', 'skip', self.get('Picture', 'skip').text())
        self._cfg.set('Picture', 'background',
                      self.get('Picture', 'background').text())

        self._cfg.set('Slideshow', 'start_slideshow_time',
                      str(self.get('Slideshow', 'start_slideshow_time').text()))
        self._cfg.set('Slideshow', 'pic_slideshow_time',
                      str(self.get('Slideshow', 'pic_slideshow_time').text()))
        self._cfg.set('Slideshow', 'fade',
                      str(self.get('Slideshow', 'fade').isChecked()))

        self._cfg.set('Gallery', 'columns',
                      str(self.get('Gallery', 'columns').text()))
        self._cfg.set('Gallery', 'size_x',
                      str(self.get('Gallery', 'size_x').text()))
        self._cfg.set('Gallery', 'size_y',
                      str(self.get('Gallery', 'size_y').text()))

        self._cfg.set('Storage', 'basedir',
                      self.get('Storage', 'basedir').text())
        self._cfg.set('Storage', 'basename',
                      self.get('Storage', 'basename').text())
        self._cfg.set('Storage', 'keep_pictures',
                      str(self.get('Storage', 'keep_pictures').isChecked()))

        self._cfg.set('Gpio', 'enable_button',
                      str(self.get('Gpio', 'enable_button').isChecked()))
        self._cfg.set('Gpio', 'exit_pin', self.get('Gpio', 'exit_pin').text())
        self._cfg.set('Gpio', 'trigger_pin',
                      self.get('Gpio', 'trigger_pin').text())

        self._cfg.set('Gpio', 'enable_light',
                      str(self.get('Gpio', 'enable_light').isChecked()))
        self._cfg.set('Gpio', 'lamp_pin', self.get('Gpio', 'lamp_pin').text())
        self._cfg.set('Gpio', 'chan_r_pin',
                      self.get('Gpio', 'chan_r_pin').text())
        self._cfg.set('Gpio', 'chan_g_pin',
                      self.get('Gpio', 'chan_g_pin').text())
        self._cfg.set('Gpio', 'chan_b_pin',
                      self.get('Gpio', 'chan_b_pin').text())

        self._cfg.set('Printer', 'enable',
                      str(self.get('Printer', 'enable').isChecked()))
        self._cfg.set('Printer', 'confirmation',
                      str(self.get('Printer', 'confirmation').isChecked()))
        self._cfg.set('Printer', 'module',
                      printer.modules[self.get('Printer',
                                               'module').currentIndex()][0])
        self._cfg.set('Printer', 'width', self.get('Printer', 'width').text())
        self._cfg.set('Printer', 'height',
                      self.get('Printer', 'height').text())

        self._cfg.set('Mailer', 'enable',
                      str(self.get('Mailer', 'enable').isChecked()))
        self._cfg.set('Mailer', 'sender', self.get('Mailer', 'sender').text())
        self._cfg.set('Mailer', 'recipient',
                      self.get('Mailer', 'recipient').text())
        self._cfg.set('Mailer', 'subject',
                      self.get('Mailer', 'subject').text())
        self._cfg.set('Mailer', 'message',
                      self.get('Mailer', 'message').text())
        self._cfg.set('Mailer', 'server', self.get('Mailer', 'server').text())
        self._cfg.set('Mailer', 'port', self.get('Mailer', 'port').text())
        self._cfg.set('Mailer', 'use_auth',
                      str(self.get('Mailer', 'use_auth').isChecked()))
        self._cfg.set('Mailer', 'use_tls',
                      str(self.get('Mailer', 'use_tls').isChecked()))
        self._cfg.set('Mailer', 'user', self.get('Mailer', 'user').text())
        self._cfg.set('Mailer', 'password',
                      self.get('Mailer', 'password').text())

        self._cfg.set('UploadWebdav', 'enable',
                      str(self.get('UploadWebdav', 'enable').isChecked()))
        self._cfg.set('UploadWebdav', 'url',
                      self.get('UploadWebdav', 'url').text())
        self._cfg.set('UploadWebdav', 'use_auth',
                      str(self.get('UploadWebdav', 'use_auth').isChecked()))
        self._cfg.set('UploadWebdav', 'user',
                      self.get('UploadWebdav', 'user').text())
        self._cfg.set('UploadWebdav', 'password',
                      self.get('UploadWebdav', 'password').text())

        self._cfg.write()
        self._restartAction()

    def restoreDefaults(self):

        self._cfg.defaults()
        self._reloadAction()
