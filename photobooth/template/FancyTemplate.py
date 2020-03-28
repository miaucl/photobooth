#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from PIL import Image, ImageOps, ImageFont, ImageDraw
from io import BytesIO
import os
import glob
from xml.etree import ElementTree

from . import Template

class AssemblyTask():
    def __init__(self):
        ...  # super.__init__()

    def do(self, image=None):
        raise NotImplementedError()

    @staticmethod
    def resize(image, size):
        """ 
        Resizing image to size maintaining the aspect ratio but cropping the image so it fills size.
        Crop before resizing for performance reasons.
        Resizes and retruns a copy
        """
        org_size = image.size
        org_aspect_ratio = org_size[0]/org_size[1]
        target_aspect_ratio = size[0]/size[1]

        img = image.copy()
        if org_aspect_ratio < target_aspect_ratio:
            # image is narrow -> cut top and bottom
            size_ratio = org_size[0]/size[0]
            new_height = int(size[1]*size_ratio)
            top_crop = (org_size[1] - new_height) / 2
            img = img.crop((0, top_crop, org_size[0], org_size[1]-top_crop))
            logging.debug("resize too tall: %s %s %s %s %s %s", org_size, size, size_ratio, new_height, top_crop, img.size)
        elif org_aspect_ratio > target_aspect_ratio:
            # image is too broad -> cut left and right
            size_ratio = org_size[1]/size[1]
            new_width = int(size[0]*size_ratio)
            left_crop = (org_size[0] - new_width) / 2
            img = img.crop((left_crop, 0, org_size[0]-left_crop, org_size[1]))
            logging.debug("resize too broad: %s %s %s %s %s %s", str(org_size), str(size), size_ratio, new_width, left_crop, str(img.size))
        img.thumbnail(size)
        return img


class ImageAssemblyTask(AssemblyTask):
    def __init__(self, name, filename, position, size, rotate=0):
        self._name = name
        self._img = Image.open(filename)
        if size is not None:
            self._size = size
            logging.info("Size not implemented - ignoring")
        self._img = self._img.convert('RGBA')
        if rotate != 0:
            self._img = self._img.rotate(rotate, expand=True)
        self._position = position

    def do(self, image, photos=None):
        image.paste(self._img, self._position, self._img)


class TextAssemblyTask(AssemblyTask):
    def __init__(self, name, text, position, size, color, font, rotate=0):
        self._name = name
        self._position = position
        self._font = ImageFont.truetype(font, size)
        self._txt = Image.new('RGBA',
                              self._font.getsize(text),
                              # ImageDraw.ImageDraw.textsize(text=text, font=self._font),
                              (255, 255, 255, 0))
        draw = ImageDraw.Draw(self._txt)
        draw.text((0, 0), text, fill=color, font=self._font)
        if rotate != 0:
            self._txt = self._txt.rotate(rotate, expand=True)

    def do(self, image, photos):
        # image = Image.alpha_composite(image, self._txt)
        image.paste(self._txt, self._position, self._txt)


class PhotoAssemblyTask(AssemblyTask):
    def __init__(self, name, photoNr, position, size, rotate=0):
        self._name = name
        self._photoNr = photoNr-1 # compensate index vs number
        self._position = position
        self._size = size
        self._rotate = rotate

    def do(self, image, photos):
        logging.debug("Assembling photoNr=%d", self._photoNr)
        photo = Image.open(photos[self._photoNr])
        if self._size is not None:
            photo = self.resize(photo, self._size)
            #photo.thumbnail(self._size)
        if self._rotate != 0:
            photo = photo.convert('RGBA')
            photo = photo.rotate(self._rotate, expand=True)
            image.paste(photo, self._position, photo)
        else:
            image.paste(photo, self._position)
class FancyTemplate(Template):

    def __init__(self, config):

        self._cfg = config
        self._totalNumPics = 0
        self._templateFile = self._cfg.get("Template", "template")
        self._templateFolder = os.path.dirname(self._templateFile)
        logging.debug("template file = %s", self._templateFile)

        self._assemblytasks = []

    def _parseXMLTemplate(self, xmltemplate):
        assemblytasks = []
        root = ElementTree.parse(xmltemplate).getroot()

        width = int(root.get("width"))
        height = int(root.get("height"))
        background = root.get("background") if root.get("background") != None else "#000000"
        logging.debug("creating picture canvas: (%d,%d) %s",
                  width, height, background)
        self._back = Image.new('RGB', (width, height), color=background)

        for f in root.findall('.'):
            logging.debug("processing tag in xmltemplate: {f.tag}")
            for step in f.findall('./'):
                if step.tag == "image":
                    logging.debug("preparing image")
                    name = step.get("id")
                    filename = os.path.join(self._templateFolder, step.get("file"))
                    position = step.get("position")
                    if position is None:
                        position = (0, 0)
                    size = None  # Not implemented yet

                    iat = ImageAssemblyTask(name, filename, position, size)
                    assemblytasks.append(iat)
                    # Optimization: if no other photo-tasks in queue yet, execute immediately
                elif step.tag == "photo":
                    logging.debug("preparing photo")
                    # <photo id="left" shot="1" x="1" y="1" width="400" height="300" rotation="0"> </photo>
                    name = step.get("id")
                    shot = int(step.get("shot"))
                    position = (int(step.get("x")), int(step.get("y")))
                    size = (int(step.get("width")), int(step.get("height")))
                    rotation = int(step.get("rotation")) if step.get("rotation") else 0

                    pat = PhotoAssemblyTask(
                        name, shot, position, size, rotation)
                    assemblytasks.append(pat)
                else:
                    logging.debug("Assembly task not yet implemented. Unkown tag: %s", step.tag)

        return assemblytasks


    def startup(self, capture_size):
        xmltemplate = glob.glob(os.path.join(self._templateFolder, "*.xml"))[0]
        logging.debug("xmltemplate = %s", xmltemplate)
        self._assemblytasks = self._parseXMLTemplate(xmltemplate)
        # implement parser for JSON alternatively??

        # count required photo shots
        shots = set([t._photoNr for t in self._assemblytasks if isinstance(t, PhotoAssemblyTask)])
        logging.debug("Template: assembly tasks: %d, shots required: %s", len(self._assemblytasks), shots)
        self._totalNumPics = len(shots)


    def assemblePicture(self, pictures):
        logging.info("Assembling picture")

        image = self._back.copy()
        for task in self._assemblytasks:
            logging.debug("assembly Task: %s", str(task))
            task.do(image, pictures)
        
        byte_data = BytesIO()
        image.save(byte_data, format='jpeg')
        return byte_data


def testassemble(argv):
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d %(funcName)s]: %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    if argv.debug:
        logging.basicConfig(level=logging.DEBUG, handlers=[ch])
    else:
        logging.basicConfig(level=logging.INFO, handlers=[ch])

    #log = logging.getLogger(__name__)
    
    import configparser
    import os

    logging.debug(argv)
    cfg = configparser.ConfigParser()
    cfg.read_string("""[Template]
     template = {}
     """.format(argv.template))

    picsize = (3496,2362)
    ft = FancyTemplate(cfg)
    ft.startup(picsize)

    photos = []

    for picfile in argv.photos:
        logging.debug("opening file %s", str(picfile))
        with open(picfile, 'rb') as f:
            photo_ba = f.read()
        photos.append(BytesIO(photo_ba))

    logging.debug("photos read from file: %d", len(photos))
    for _ in range(len(photos),ft.totalNumPics):
        byte_data = BytesIO()
        Image.new('RGB', picsize, "#AABBCC").save(byte_data, format='jpeg')
        photos.append(byte_data)
    
    img_bytes = ft.assemblePicture(photos)
    img = Image.open(img_bytes)
    if argv.out:
        img.save(argv.out)
    else:
        img.show()


if __name__ == "__main__":
    import sys
    import argparse
    
    # Add parameter for direct startup
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='enable additional debug output')
    parser.add_argument('-t', '--template', type=str, help='template folder to be used', default="supplementals/templates/example")
    parser.add_argument('-o', '--out', type=str, help='output file name')
    parser.add_argument('photos', type=str, nargs='*', help='input photos file name')
    parsed_args = parser.parse_args(sys.argv[1:]) # script path included in argv[0] -> excluding
    testassemble(parsed_args)
