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
from flask import Flask, request, render_template, send_file
import os.path
from time import localtime, strftime, time

from photobooth.Config import Config

from ..worker.PictureList import PictureList
from .. import StateMachine
from ..Threading import Communicator, Workers
from threading import Thread

app = Flask(__name__)

index_data = None

picture_list = None

class Web:    
    def __init__(self, config: Config, comm: Communicator):

        super().__init__()

        self._comm = comm

        # Picture naming convention for assembled pictures
        path = os.path.join(config.get('Storage', 'basedir'),
                            config.get('Storage', 'basename'))
        basename = strftime(path, localtime())
        self._pictureList = PictureList(basename)

        self._app = None

        self._is_enabled_server = config.getBool('Web', 'enable_server')

        self.initWeb(config)

    def initWeb(self, config: Config):
        global index_data, picture_list

        if self._is_enabled_server:

            port = config.getInt('Web', 'port')
            host = config.get('Web', 'host')

            picture_list = self._pictureList

            index_data = {
                "name": config.get('Event', 'event'),
                "link": config.get('Web', 'link'),
                "count": self._pictureList.count(),
            }

            
            Thread(target=lambda: app.run(host=host, port=port, debug=False), daemon=True).start()
            logging.info(f'Web server enabled (http://{ host }:{ port })')
        else:
            logging.info('Web server disabled')

    def run(self):

        for state in self._comm.iter(Workers.WEB):
            self.handleState(state)            

        return True

    def handleState(self, state: StateMachine.State):

        if isinstance(state, StateMachine.TeardownState):
            self.teardown(state)

    def teardown(self, state: StateMachine.State):

        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

@app.route('/')
def index():
    logging.info('GET index page')
    picture_list.findExistingFiles()
    index_data['count'] = picture_list.count()
    return render_template('index.html', **index_data)

@app.route('/slideshow')
def slideshow():
    logging.info('GET slideshow page')
    picture_list.findExistingFiles()
    index_data['r'] = time()
    return render_template('slideshow.html', **index_data)

@app.route('/thumbnail/<int:index>')
def thumbnail(index):
    pictureRef = picture_list.getPicture(index)
    logging.info(f'GET picture thumbnail { index }: { pictureRef.thumbnail }')
    # For local paths, we need to go back to the cwd it has been based on, otherwise, just use the global path
    return send_file(pictureRef.thumbnail if pictureRef.thumbnail.startswith('/') else f'../../{ pictureRef.thumbnail }')

@app.route('/r')
def rpicture():
    pictureRef, _ = picture_list.getRandomPicture()
    logging.info(f'GET random picture: { pictureRef.watermarked }')
    # For local paths, we need to go back to the cwd it has been based on, otherwise, just use the global path
    return send_file(pictureRef.watermarked if pictureRef.watermarked.startswith('/') else f'../../{ pictureRef.watermarked }')

@app.route('/<int:index>')
def picture(index):
    pictureRef = picture_list.getPicture(index)
    logging.info(f'GET picture { index }: { pictureRef.watermarked }')
    # For local paths, we need to go back to the cwd it has been based on, otherwise, just use the global path
    return send_file(pictureRef.watermarked if pictureRef.watermarked.startswith('/') else f'../../{ pictureRef.watermarked }')
