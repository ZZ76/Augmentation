import os.path
import os
import xml.etree.ElementTree as ET
import numpy as np
from lxml.etree import Element, SubElement, tostring, ElementTree


def findelementbyname(name, obj):
    for i in obj.iter(name):
        #print(i.text)
        return i.text


def getcoordandname(filename):  # return a list with name and coord
    tree = ET.parse(filename)
    root = tree.getroot()
    returnlist = []
    for child in root.iter('object'):
        #print(child)
        #print(child.tag, child.attrib)
        name = findelementbyname('name', child)
        xmin = findelementbyname('xmin', child)
        ymin = findelementbyname('ymin', child)
        xmax = findelementbyname('xmax', child)
        ymax = findelementbyname('ymax', child)
        returnlist.append([name, int(xmin), int(ymin), int(xmax), int(ymax)])
    #print(returnlist)
    return returnlist


def checkbb(value, threshold):   # check and fix bounding box range
    if value < 0:
        value = 1
    if value > threshold:
        value = threshold - 1
    return value


def rewrite(imgname, imgpath, filepath, savepath, newcoordlist, img, save=False):
    h, w, _ = img.shape
    tree = ET.parse(filepath)
    root = tree.getroot()
    for ele in root.iter('folder'):
        ele.text = str('images')
    for ele in root.iter('filename'):
        ele.text = str(imgname)
    for ele in root.iter('path'):
        ele.text = str(imgpath)
    for i, ele in enumerate(root.iter('xmin')):
        xmin = np.amin(newcoordlist[i][0])
        ele.text = str(checkbb(xmin, w))
    for i, ele in enumerate(root.iter('ymin')):
        ymin = np.amin(newcoordlist[i][1])
        ele.text = str(checkbb(ymin, h))
    for i, ele in enumerate(root.iter('xmax')):
        xmax = np.amax(newcoordlist[i][0])
        ele.text = str(checkbb(xmax, w))
    for i, ele in enumerate(root.iter('ymax')):
        ymax = np.amax(newcoordlist[i][1])
        ele.text = str(checkbb(ymax, h))
    if save is True:
        #print(savepath)
        tree.write(savepath, xml_declaration=False, encoding='utf-8')


def rewriteheadlines(imgname, imgpath, filepath, savepath, save=False):
    tree = ET.parse(filepath)
    root = tree.getroot()
    for ele in root.iter('folder'):
        ele.text = str('images')
    for ele in root.iter('filename'):
        ele.text = str(imgname)
    for ele in root.iter('path'):
        ele.text = str(imgpath)
    if save is True:
        #print(savepath)
        tree.write(savepath, xml_declaration=False, encoding='utf-8')


def readfiles(folder):
    global cnt
    folder2 = os.listdir(folder)
    for file in folder2:
        if not os.path.isdir(file):
            if file[-4:] == '.xml':
                print(file)
                file = os.path.join(DIR_SRCLIST, file)
                getcoordandname(file)
                #break
            else:
                print('n', file)


#DIR_SRCLIST = './data/labels'

#readfiles(DIR_SRCLIST)
