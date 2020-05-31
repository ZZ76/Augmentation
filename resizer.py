import sys
import getopt
import argparse
import os
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from lxml.etree import Element, SubElement, tostring, ElementTree
import random


def randomchar(num):
    list = ''
    for i in range(num):
        char = random.randint(0x0061, 0x007A)
        list = list + chr(char)
    return list
    
    
def showprogress(CNT, total):
    global CHARLIST
    all = 50
    filled = int(all * (CNT)/total)
    if len(CHARLIST) <= 3:
        CHARLIST = randomchar(filled)
    else:
        CHARLIST = CHARLIST[:-3] + randomchar(filled-len(CHARLIST)+3)
    print('\r[' + CHARLIST + '_' * (all - filled) + ']', end=' ')
    print(str(2 * filled).ljust(3), '/', 100, end='')
    print(', {}/{}'.format(CNT, TOTAL), end='', flush=True)


def findelementbyname(obj, name):
    for i in obj.iter(name):
        #print(i.text)
        return i.text


def changetextbyname(obj, name, value):
    for i in obj.iter(name):
        i.text = str(value)


def xml_resize(file_path, file_name_only):
    global OUT_X, OUT_Y
    tree = ET.parse(file_path)
    root = tree.getroot()
    x_factor, y_factor = 1, 1
    try:
        for child in root.iter('size'):
            width = int(findelementbyname(child, 'width'))
            height = int(findelementbyname(child, 'height'))
            if MINIMUM_SIDE:  # decide which method to use
                if width >= height:  # use height as minimum side
                    x_factor, y_factor = MINIMUM_SIDE/height, MINIMUM_SIDE/height
                else:
                    x_factor, y_factor = MINIMUM_SIDE/width, MINIMUM_SIDE/width
            else:
                x_factor, y_factor = RESIZE_X/width, RESIZE_Y/height
            OUT_X, OUT_Y = int(width * x_factor), int(height * y_factor)
            changetextbyname(child, 'width', OUT_X)
            changetextbyname(child, 'height', OUT_Y)
        # print(width, height)
        # print(OUT_X, OUT_Y)
        for child in root.iter('object'):
            #for i in ['xmin', 'ymin', 'xmax', 'ymax']:
            #name = findelementbyname(child, 'name')
            xmin = int(findelementbyname(child, 'xmin'))
            changetextbyname(child, 'xmin', int(xmin * x_factor))
            ymin = int(findelementbyname(child, 'ymin'))
            changetextbyname(child, 'ymin', int(ymin * y_factor))
            xmax = int(findelementbyname(child, 'xmax'))
            changetextbyname(child, 'xmax', int(xmax * x_factor))
            ymax = int(findelementbyname(child, 'ymax'))
            changetextbyname(child, 'ymax', int(ymax * y_factor))
        tree.write(os.path.join(SAVE_ANNO_FOLDER, file_name_only), xml_declaration=False, encoding='utf-8')
    except Exception as e:
        print("\n", file_path)
        print(str(e))
    
    
def image_resize(file_path, file_name_only):
    global OUT_X, OUT_Y
    image = cv2.imread(file_path)
    image = cv2.resize(image, (OUT_X, OUT_Y))
    cv2.imwrite(os.path.join(SAVE_IMAGE_FOLDER, file_name_only), image)
    image = None
    
    
def main():
    global TOTAL, CNT, OUT_X, OUT_Y
    # create folder
    if not os.path.isdir(SAVE_IMAGE_FOLDER):
        os.makedirs(SAVE_IMAGE_FOLDER)
    if not os.path.isdir(SAVE_ANNO_FOLDER):
        os.makedirs(SAVE_ANNO_FOLDER)
    for file in os.listdir(ANNO_FOLDER):
        if os.path.isfile(os.path.join(ANNO_FOLDER, file)) and file[-4:] == '.xml':
            TOTAL += 1
    for file in os.listdir(ANNO_FOLDER):
        if os.path.isfile(os.path.join(ANNO_FOLDER, file)) and file[-4:] == '.xml':
            CNT += 1
            if os.path.isfile(os.path.join(IMAGE_FOLDER, file[:-4]+".jpg")):  # check image file exist
                try:
                    #print(file)
                    OUT_X, OUT_Y = None, None
                    xml_resize(os.path.join(ANNO_FOLDER, file), file)
                    image_resize(os.path.join(IMAGE_FOLDER, file[:-4]+".jpg"), file[:-4]+".jpg")
                except Exception as e:
                    print("\n", file)
                    print(str(e))
            showprogress(CNT, TOTAL)


# DEBUG
# ANNO_FOLDER = r".\Dataset_Vehicle\labels"
# IMAGE_FOLDER = r".\Dataset_Vehicle\images"
# SAVE_ANNO_FOLDER = r".\Dataset_Vehicle\resized\labels"
# SAVE_IMAGE_FOLDER = r".\Dataset_Vehicle\resized\images"
ANNO_FOLDER = None
IMAGE_FOLDER = None
SAVE_ANNO_FOLDER = None
SAVE_IMAGE_FOLDER = None
TOTAL = 0
RESIZE_X, RESIZE_Y = None, None
MINIMUM_SIDE = None
CHARLIST = ""
CNT = 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--anno_folder")
    parser.add_argument("--image_folder")
    parser.add_argument("--save_anno_folder")
    parser.add_argument("--save_image_folder")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--resize_xy", nargs=2, type=int)
    group.add_argument("--minimum_side", type=int)
    args = parser.parse_args()
    if args.anno_folder:
        ANNO_FOLDER = args.anno_folder
    if args.image_folder:
        IMAGE_FOLDER = args.image_folder
    if args.save_anno_folder:
        SAVE_ANNO_FOLDER = args.save_anno_folder
    if args.save_image_folder:
        SAVE_IMAGE_FOLDER = args.save_image_folder
    if args.resize_xy:
        RESIZE_X, RESIZE_Y = args.resize_xy[0], args.resize_xy[1]
    if args.minimum_side:
        MINIMUM_SIDE = args.minimum_side
    print("anno_folder = {}".format(ANNO_FOLDER))
    print("image_folder = {}".format(IMAGE_FOLDER))
    print("save_anno_folder = {}".format(SAVE_ANNO_FOLDER))
    print("save_image_folder = {}".format(SAVE_IMAGE_FOLDER))
    if RESIZE_X:
        print("resize_x = {}, resize_y = {}".format(RESIZE_X, RESIZE_Y))
    else:
        print("minimum_side = {}".format(MINIMUM_SIDE))
    #print('save =', SAVE, "\n")
    main()

