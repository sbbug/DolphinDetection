#!/usr/bin/env python
# encoding: utf-8
"""
@author: Shanda Lau 刘祥德
@license: (C) Copyright 2019-now, Node Supply Chain Manager Corporation Limited.
@contact: shandalaulv@gmail.com
@software: 
@file: test_bgsubstractor.py
@time: 3/20/20 11:12 AM
@version 1.0
@desc:
"""
import time
import numpy as np

import cv2
import imutils


def mog2(video_path, open_kernel_size=None, dilate_kernel_size=None, gaussian_size=None, dist2Threshold=54,
         block_size=51, width=480, sp=10):
    mog = cv2.createBackgroundSubtractorMOG2(100, dist2Threshold, False)
    # saliency = cv2.MotionSaliencyBinWangApr2014_create()
    cap = cv2.VideoCapture(video_path)
    # cap = cv2.VideoCapture(video_path)
    grabbed, blur = cap.read()
    cv2.namedWindow('Mog', cv2.WINDOW_FREERATIO)
    cv2.namedWindow('Original', cv2.WINDOW_FREERATIO)
    cv2.namedWindow('Blur', cv2.WINDOW_FREERATIO)
    # kernel_size = (10, 10)
    # gaussian_size = (5, 5)
    open_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_kernel_size, open_kernel_size))
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilate_kernel_size, dilate_kernel_size))
    cnt = 0
    while grabbed:
        frame = imutils.resize(blur, width=width)
        print(cv2.mean(frame))
        if cnt % 1 == 0:
            # frame = cv2.GaussianBlur(frame, gaussian_size, sigmaY=0, sigmaX=0)
            s = time.time()
            blur = cv2.pyrMeanShiftFiltering(frame, sp, 60)
            global_mean = cv2.mean(blur)
            # print(f'Global mean {global_mean}')
            # binary = mog.apply(frame)
            gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block_size, 40)
            # binary = mog.apply(blur)
            # _,binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, open_kernel)
            # contours = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
            frame_area = binary.shape[1] * binary.shape[0]
            # binary = cv2.dilate(binary, dilate_kernel)
            num_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(binary)
            e = 1 / (time.time() - s)
            # print(f'Operation Speed [{round(e, 2)}]/FPS')

            for i in range(1, num_labels):
                mask = (label_map == i).astype(np.uint8)
                block_pixels = mask.sum()
                mask = cv2.merge([mask, mask, mask]) * 255
                block = cv2.bitwise_and(frame, mask)
                # cv2.imshow('block', block)
                b_mean = np.sum(block[:, :, 0]) / block_pixels
                g_mean = np.sum(block[:, :, 1]) / block_pixels
                r_mean = np.sum(block[:, :, 2]) / block_pixels
                print(f'block mean {b_mean, g_mean, r_mean}')
                diff = np.array([b_mean, g_mean, r_mean, 0]) - global_mean
                print(f'mean diff {abs(diff)}')
                print(f'Area {stats[i][cv2.CC_STAT_AREA]}')
                print(f'Width {stats[i][cv2.CC_STAT_WIDTH]}')
                print(f'Height {stats[i][cv2.CC_STAT_HEIGHT]}')
                cv2.imshow('Mask', block)

            cv2.imshow('Mog', binary)
            cv2.imshow('Blur', blur)
            cv2.imshow('Original', frame)
            cv2.waitKey(0)
            grabbed, blur = cap.read()
        cnt += 1


if __name__ == '__main__':
    # video_path = '/Users/luvletteru/Documents/GitHub/DolphinDetection/data/offline/6/22_1080P.mp4'
    # mog2(video_path, (10, 10), (5, 5),)
    video_path = '/Users/luvletteru/Documents/GitHub/DolphinDetection/data/offline/9/0316115208_merged.mp4'
    # video_path = '/Users/luvletteru/Documents/GitHub/DolphinDetection/data/offline/6/bird15.mp4'
    # mog2(video_path, (3, 3), (3, 3), 54, block_size=51, width=960)
    # mog2(video_path, (3, 3), (3, 3), 54, block_size=101, width=1920, sp=10)
    # mog2(video_path, (3, 3), (3, 3), 54)
    # video_path = '/Users/luvletteru/Documents/GitHub/DolphinDetection/data/offline/6x/0225_merged.mp4'
    # video_path = '/Users/luvletteru/Documents/GitHub/DolphinDetection/data/candidates/0325_cvam_21.mp4'
    # video_path = '/Users/luvletteru/Documents/GitHub/DolphinDetection/data/candidates/0325110728_0.mp4'
    # video_path = '/Users/luvletteru/Documents/GitHub/DolphinDetection/data/candidates/0321164540_0.mp4'
    # video_path = '/Users/luvletteru/Documents/GitHub/DolphinDetection/data/candidates/0325110728_0.mp4'
    # video_path = '/Users/luvletteru/Documents/GitHub/DolphinDetection/data/candidates/0325151208_303.mp4'
    video_path = '/Users/luvletteru/Downloads/20200221/15点14分  23 2.58-3.03近.mp4'
    # mog2(video_path, open_kernel_size=3, dilate_kernel_size=5, block_size=51, width=1000, sp=10)
    mog2(video_path, open_kernel_size=3, dilate_kernel_size=5, block_size=101, width=1000, sp=20)
