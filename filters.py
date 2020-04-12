import cv2
import numpy as np
import xmlopt
import matplotlib.cm as mpcm
import random
import os

# change color, blur, add noise...
def randomhsv(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    hv, sv, cts, brt = random.randint(-128, 128), random.uniform(0.5, 1.5), random.uniform(0.5, 1.5), random.randint(-50, 50)
    h[:] = h[:] + hv
    s = np.uint8(np.clip((cts * (s + 2)), 0, 255))
    v = np.uint8(np.clip((cts * v - brt), 0, 255))
    #print(hv, sv, vv)
    hsv = cv2.merge([h, s, v])
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    '''cv2.imshow('h', h)
    cv2.imshow('s', s)
    cv2.imshow('v', v)
    cv2.imshow('trans', img)'''
    return img


def randomgaussian(img):
    k = 2*random.randint(2, 3)-1
    img = cv2.GaussianBlur(img, (k, k), 1)
    #print(k)
    #cv2.imshow('gau', img)
    return img


def randomnoise(img):
    h, w = img.shape[0], img.shape[1]
    b, g, r = np.zeros((h, w)), np.zeros((h, w)), np.zeros((h, w))
    b, g, r = cv2.randn(b, 16, 16), cv2.randn(g, 16, 16), cv2.randn(r, 16, 16)
    noise = cv2.merge([b, g, r])
    img = cv2.add(img, noise, dtype=cv2.CV_8UC3)
    #cv2.imshow('ori', img)
    return img


def randomnoisevalue(img):
    height, width = img.shape[0], img.shape[1]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    random_m = np.random.randint(low=85, high=115, size=(height, width))  # + - 15% value
    random_m = (random_m/100)
    h, s, v = cv2.split(hsv)
    v = np.clip((np.multiply(random_m, v)), 0, 255).astype(np.uint8)
    hsv = cv2.merge([h, s, v])
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    #cv2.imshow('img', img)
    #cv2.imshow('hsv', hsv)
    return img


def horizontalblur(img):
    w = 7
    h = 1
    #j = 50
    kernel = np.ones((h, w), np.float32)
    #kernel[int((h+1)/2-1), :] = j
    #print(kernel)
    kernel = kernel / np.sum(kernel)
    img = cv2.filter2D(img, -1, kernel)
    #cv2.imshow('h1', img)
    return img


def verticalblur(img):
    w = 1
    h = 7
    #j = 50
    kernel = np.ones((h, w), np.float32)
    #kernel[int((h+1)/2-1)][:] = j
    #print(kernel)
    kernel = kernel / np.sum(kernel)
    img = cv2.filter2D(img, -1, kernel)
    #cv2.imshow('v1', img)
    return img


def verticalgau(img):
    k = 5
    sigma = 1.0
    M = cv2.getGaussianKernel(k, sigma)
    kernel = np.ones((k, k), np.float32)
    kernel[:, int((k + 1) / 2 - 1)] = M[:, 0]
    #print(kernel)
    kernel = kernel/np.sum(kernel)
    #kernelx = np.transpose(M)
    #kernelx = np.ones((1, k)) / k
    img = cv2.filter2D(img, -1, kernel)
    #img = cv2.sepFilter2D(img, -1, kernelx, M)
    #cv2.imshow('vg', img)
    return img


def horizontalgau(img):
    k = 5
    sigma = 1.0
    M = np.transpose(cv2.getGaussianKernel(k, sigma))
    kernel = np.ones((k, k), np.float32)
    kernel[int((k + 1) / 2 - 1), :] = M[:]
    kernel = kernel/np.sum(kernel)
    img = cv2.filter2D(img, -1, kernel)
    #img = cv2.sepFilter2D(img, -1, kernelx, M)
    #cv2.imshow('hg', img)
    return img


def randomline(img):
    h, w, _ = img.shape
    for i in range(8):   # how many lines
        for j in range(2):
            x = random.randint(0, w)
            y = random.randint(0, h)
            if j == 0:
                pt1 = (x, y)
            else:
                pt2 = (x, y)
        color = np.random.randint(0, high=255, size=3)
        color = (int(color[0]), int(color[1]), int(color[2]))
        cv2.line(img, tuple(pt1), tuple(pt2), color, 1)
        #cv2.imshow('randomline', img)
    return img


def randomcircle(img):
    h, w, _ = img.shape
    for i in range(8):   # how many circles
        x = random.randint(0, w)
        y = random.randint(0, h)
        color = np.random.randint(0, high=255, size=3)
        color = (int(color[0]), int(color[1]), int(color[2]))
        cv2.circle(img, (x, y), 2, color, -1, lineType=4)
        #cv2.imshow('randomcircle', img)
    return img


def linecirclecontroller(img):
    p = random.uniform(0, 1)
    if p <= 0.5:
        return randomcircle(img)
    else:
        return randomline(img)


def noisecontroller(img):
    p = random.uniform(0, 1)
    if p <= 0.45:
        return randomnoise(img)
    elif p <= 0.9:
        return randomnoisevalue(img)
    else:
        return randomnoisevalue(randomnoise(img))


def blurcontroller(img):
    p = random.uniform(0, 1)
    if p <= 0.1:
        img = randomgaussian(img)
    elif p <= 0.325:
        img = horizontalblur(img)
    elif p <= 0.55:
        img = verticalblur(img)
    elif p <= 0.775:
        img = horizontalgau(img)
    else:
        img = verticalgau(img)
    #cv2.imshow('bc', img)
    return img


def invert(img):
    img = ~img
    return img


# img = cv2.imread('./test_data_real/JPEGImages/00000.jpg')

#randomnoisevalue(img)
#randomhsv(img)
#img = randomgaussian(img)
#verticalblur(img)
#verticalgau(img)
#horizontalblur(img)
#horizontalgau(img)
#blurcontroller(img)
#randomnoise(img)
#randomline(img)
#randomcircle(img)
#linecirclecontroller(img)
#brightnessandcontrast(img)

# cv2.imshow('img', cv2.resize(img, (300, int(img.shape[0]*300/img.shape[1]))))
# cv2.imshow('img2', cv2.resize(randomnoisevalue(img), (300, int(img.shape[0]*300/img.shape[1]))))
# cv2.waitKey(0)
# cv2.destroyAllWindows()
