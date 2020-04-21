import cv2
import numpy as np
import random


def rd(num):
    return random.randint(-num, num)
    
    
def perspectivelist(objlist, M):
    newcoordlist = []  # get transformed 4 points
    for i in objlist:
        tmp = np.ones(len(i[0]))   # add new dimension with value 1
        i = np.vstack((i, tmp)).astype(int)
        #print('i', i)
        coord = np.dot(M, i)   # for perspective
        for j in range(4):
            coord[0][j] = coord[0][j]/coord[2][j]  # x = x/z
            coord[1][j] = coord[1][j]/coord[2][j]  # y = y/z
        coord = coord.astype(int)
        newcoordlist.append(coord)
    return newcoordlist


def affinelist(objlist, M):
    newcoordlist = []  # get transformed 4 points
    for i in objlist:
        tmp = np.ones(len(i[0]))  # add new dimension with value 1
        i = np.vstack((i, tmp)).astype(int)
        #print('i', i)
        coord = np.dot(M, i).astype(int)   # for affine
        #print('coord =', coord)
        newcoordlist.append(coord)
    return newcoordlist


def randomperspect(img, objlist):   # random perspective transform and generate new coord list
    h, w, _ = img.shape
    p = 1/30   # changing rate
    r_h, r_w = int(h*p), int(w*p)   # changing range of width and height
    startpts = np.float32([[r_w, r_h], [w-r_w, r_h], [w-r_w, h-r_h], [r_w, h-r_h]])
    endpts = np.float32([[r_w+rd(r_w), r_h+rd(r_h)], [w-r_w+rd(r_w), r_h+rd(r_h)], [w-r_w+rd(r_w), h-r_h+rd(r_h)], [r_w+rd(r_w), h-r_h+rd(r_h)]])
    M = cv2.getPerspectiveTransform(startpts, endpts)
    dst = cv2.warpPerspective(img, M, (w, h))
    newcoordlist = perspectivelist(objlist, M)
    return dst, newcoordlist

