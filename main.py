import cv2
import numpy as np
import xmlopt
import matplotlib.cm as mpcm
import random
import os
import filters
import sys
import getopt
import transform
from shutil import copyfile


def colors_subselect(colors, num_classes=10):
    dt = len(colors) // num_classes
    sub_colors = []
    for i in range(num_classes):
        color = colors[i*dt]
        if isinstance(color[0], float):
            sub_colors.append([int(c * 255) for c in color])
        else:
            sub_colors.append([c for c in color])
    return sub_colors


def getobjectlist(elelist_ori):  # get four points for each object as an array, build a list with array in it
    objlist = []
    for i in elelist_ori:  # each repeat for one object
        xmin, ymin, xmax, ymax = i[1], i[2], i[3], i[4]
        #cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (255, 255, 0), 1)
        p1, p2, p3, p4 = [[xmin], [ymin]], [[xmax], [ymin]], [[xmax], [ymax]], [[xmin], [ymax]]
        pointarray = np.hstack([p1, p2])
        pointarray = np.hstack([pointarray, p3])
        pointarray = np.hstack([pointarray, p4])
        objlist.append(pointarray)
    return objlist


def visulisebb(img, dstimg, newcoordlist):  # get new max min, draw new bb
    for i in newcoordlist:
        xmin = np.amin(i[0])
        xmax = np.amax(i[0])
        ymin = np.amin(i[1])
        ymax = np.amax(i[1])
        cv2.rectangle(dstimg, (xmin, ymin), (xmax, ymax), tuple(colors_plasma[random.randint(0, 14)]), 1)
    cv2.imshow('img', img)
    cv2.imshow('dst', dstimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def randomrun(func, img, p=0.5):  # random run a function in filter.py. with probability p
    if p == 0:
        return img
    elif p >= random.uniform(0, 1):
        img = func(img)
    return img


def randomchar(num):
    list = ''
    for i in range(num):
        char = random.randint(0x0061, 0x007A)
        list = list + chr(char)
    return list


def showprogress(CNT, total):
    global CHARLIST
    all = 50
    filled = int(all * (CNT+1)/total)
    if len(CHARLIST) <= 3:
        CHARLIST = randomchar(filled)
    else:
        CHARLIST = CHARLIST[:-3] + randomchar(filled-len(CHARLIST)+3)
    print('\r[' + CHARLIST + '_' * (all - filled) + ']', end=' ')
    print(str(2 * filled).ljust(3), '/', 100, end='')
    print(', ', CNT, end='', flush=True)


def operator(img_path, xml_path, repeat=1, save=False, vasulise=False):   # Transform and save
    global CNT, TOTAL
    for i in range(repeat):
        img = cv2.imread(img_path)
        elelist_ori = xmlopt.getcoordandname(xml_path)
        objlist = getobjectlist(elelist_ori)
        dst, newcoordlist = transform.randomperspect(img, objlist)
        dst = randomrun(filters.invert, dst, p=pinvert)
        dst = randomrun(filters.randomhsv, dst, p=pcolor)
        dst = randomrun(filters.blurcontroller, dst, p=pblur)
        dst = randomrun(filters.noisecontroller, dst, p=pnoise)
        dst = randomrun(filters.togray, dst, p=pgray)
        #dst = randomrun(filters.linecirclecontroller, dst, p=pnoise)
        if save is True:
            # save img
            img_save_path = save_image_folder + '/' + str(CNT).zfill(5) + '.' + format
            cv2.imwrite(img_save_path, dst)
            # save xml
            xml_save_path = save_anno_folder + '/' + str(CNT).zfill(5) + '.xml'
            xmlopt.rewrite((str(CNT).zfill(5) + '.' + format), img_save_path, xml_path, xml_save_path, newcoordlist, img, save=True)
        showprogress(CNT, TOTAL)  # show progress bar
        CNT += 1
        if vasulise is True:
            visulisebb(img, dst, newcoordlist)


def readfilesandoprt(repeat=1, save=False):   # walk through the folder to find xml and check jpg
    global CNT, TOTAL
    TOTAL = CNT
    anno_path = anno_folder  # source Annotations path
    jpg_path = image_folder   # source Img folder path
    if save is True:
        if not os.path.isdir(save_image_folder):
            os.makedirs(save_image_folder)
        if not os.path.isdir(save_anno_folder):
            os.makedirs(save_anno_folder)
    for file in os.listdir(anno_path):
        if os.path.isfile(os.path.join(anno_path, file)) and file[-4:]=='.xml':
            TOTAL += 1
    TOTAL = TOTAL*(repeat+1)
    for file in os.listdir(anno_path):   # scan in Annotations folder
        try:
            if os.path.isfile(os.path.join(anno_path, file)):
                if file[-4:] == '.xml':   # check xml file
                    jpg_name = file[:-4]+'.'+format
                    jpg_file_path = os.path.join(jpg_path, jpg_name)
                    #print('jpg', jpg_file_path)
                    xml_file_path = os.path.join(anno_path, file)
                    #print('xml', xml_file_path)
                    if os.path.exists(jpg_file_path):   # check if jpg file exists
                        if save is True:
                            img_copy_path = save_image_folder + '/' + str(CNT).zfill(5) + '.' + format
                            copyfile(jpg_file_path, img_copy_path)   # copy jpg
                            save_path = save_anno_folder + '/' + str(CNT).zfill(5) + '.xml'
                            #xmlopt.rewriteheadlines((str(CNT).zfill(5) + '.' + format), img_copy_path, xml_file_path, save_path, save=True)  # rewrite xml headlines
                            #copyfile(xml_file_path, copy_path)   # copy xml
                            #xml_file_path = save_path
                            showprogress(CNT, TOTAL)
                            CNT += 1
                            operator(jpg_file_path, xml_file_path, repeat, save=True, vasulise=False)
                        else:
                            operator(jpg_file_path, xml_file_path, repeat, vasulise=True)
                    else:
                        print(jpg_file_path, 'not exists')
                #else:
                    #print('\n', file, 'is not a xml file')   
        except Exception as e:
            print(str(e))
    print('\ngenerated {} images'.format(CNT))


CHARLIST = ''   # for progressbar
format = 'jpg'


colors_plasma = colors_subselect(mpcm.plasma.colors, num_classes=15)
# windows
anno_folder = './Dataset_Vehicle/labels'
image_folder = './Dataset_Vehicle/images'
save_anno_folder = './Dataset_Vehicle/augmented/labels'
save_image_folder = './Dataset_Vehicle/augmented/images'
repeat = 1
# ubuntu
# anno_folder = '/home/user/dataset/annotations'   # annotations folder
# image_folder = '/home/user/dataset/images'   # image folder
# save_anno_folder = '/home/user/dataset/augmented/annotations'  # save annotations folder
# save_image_folder = '/home/user/dataset/augmented/images'  # save image folder
# repeat = 4

CNT = 0  # used by procress bar
pcolor = 0.4
pblur = 0.4
pnoise = 0.4
pinvert = 0
pgray = 0.3
save = True

if __name__ == "__main__":
    try:
        options, args = getopt.getopt(sys.argv[1:], "", ["save_anno_folder=", "save_image_folder=", "anno_folder=",
                                                         "image_folder=", "repeat=", "pcolor=",
                                                         "pblur=", "pnoise=", "pinvert=", "pgray=", "format=", "CNT=", "save="])
    except getopt.GetoptError:
        sys.exit()
    for name, value in options:
        if name in ("--save_anno_folder"):
            save_anno_folder = value
        if name in ("--save_image_folder"):
            save_image_folder = value
        if name in ("--anno_folder"):
            anno_folder = value
        if name in ("--image_folder"):
            image_folder = value
        if name in ("--repeat"):
            repeat = int(value)
        if name in ("--pcolor"):
            pcolor = float(value)
        if name in ("--pblur"):
            pblur = float(value)
        if name in ("--pnoise"):
            pnoise = float(value)
        if name in ("--pinvert"):
            pinvert = float(value)
        if name in ("--pgray"):
            pgray = float(value)
        if name in ("--save"):
            save = value
        if name in ("--format"):
            format = value
        if name in ("--CNT"):
            CNT = int(value)
    print("anno_folder =", anno_folder)
    print("image_folder =", image_folder)
    print("save_anno_folder =", save_anno_folder)
    print("save_image_folder =", save_image_folder)
    print("repeat =", repeat)
    print('p_color =', pcolor)
    print('p_blur =', pblur)
    print('p_noise =', pnoise)
    print('p_invert =', pinvert)
    print('pgray =', pgray)
    print('format =', format)
    print('CNT =', CNT)
    print('save =', save, "\n")
    if save is True:
        readfilesandoprt(repeat=repeat, save=True)
    else:
        readfilesandoprt(repeat=repeat, save=False)

