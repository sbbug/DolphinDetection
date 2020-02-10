#!/usr/bin/env python
# encoding: utf-8
"""
@author: Shanda Lau 刘祥德
@license: (C) Copyright 2019-now, Node Supply Chain Manager Corporation Limited.
@contact: shandalaulv@gmail.com
@software: 
@file: test.py
@time: 2019/11/15 14:49
@version 1.0
@desc:
"""

from multiprocessing import Manager
from multiprocessing import Pool

# import interface as I
from config import *
from detection.manager import DetectionMonitor, EmbeddingControlBasedTaskMonitor
from detection.detect_funcs import detect
from utils import *
from skimage.measure import compare_ssim
import cv2


def test_video_config():
    cfg = I.load_video_config(VIDEO_CONFIG_DIR / 'video.json')
    cfg = VideoConfig.from_json(cfg[0])
    print(cfg.resize)


def test_load_label_json():
    cfg_key, cfg_val = I.load_label_config(LABEL_SAVE_PATH / 'samples.json')
    print(cfg_key[0], cfg_val[0].center)


def test_load_video_json():
    cfg = I.load_video_config(VIDEO_CONFIG_DIR / 'video.json')
    print(cfg[0].url)


def test_adaptive_thresh():
    frames = test_read_frame()
    cfg = I.load_video_config(VIDEO_CONFIG_DIR / 'video.json')
    for f in frames:
        binary = I.thresh(f, cfg[0])
        cv2.imshow('binary', binary)
        cv2.waitKey(0)


def test_read_steam():
    # clean all exist streams
    q = Manager().Queue()
    cfg = I.load_video_config(VIDEO_CONFIG_DIR / 'video.json')
    I.read_stream(STREAM_SAVE_DIR / str(cfg.index), cfg[0], q)
    p = Pool()
    p.apply_async(I.read_stream, (STREAM_SAVE_DIR / str(cfg.index), cfg, q,))
    # I.read_stream(STREAM_SAVE_DIR, cfg['videos'][0], q)


def test_detect():
    clean_dir(STREAM_SAVE_DIR)
    cfgs = I.load_video_config(VIDEO_CONFIG_DIR / 'video.json')
    # for i, cfg in enumerate(cfgs[:1]):
    p = Pool()
    qs = [Manager().Queue(), Manager().Queue()]
    for i, cfg in enumerate(cfgs):
        time.sleep(1)
        # q = Queue()
        p.apply_async(I.read_stream, (STREAM_SAVE_DIR / str(cfg.index), cfg, qs[i],))
        p.apply_async(I.detect, (STREAM_SAVE_DIR / str(cfg.index), CANDIDATE_SAVE_DIR, qs[i], cfg,))
        # p.apply_async(init_detect, (STREAM_SAVE_DIR / str(cfg.index), cfg,))
    p.close()
    p.join()
    print('Init Done')


def test_detect_monitor():
    monitor = DetectionMonitor(VIDEO_CONFIG_DIR / 'video.json', STREAM_SAVE_DIR, None, CANDIDATE_SAVE_DIR, )
    monitor.monitor()


def test_read_frame():
    data = STREAM_SAVE_DIR / str(0) / '139.ts'
    samples = I.read_frame(data, FRAME_SAVE_DIR / str(0))
    return samples


def test_task_monitor():
    monitor = build_task_monitor()
    # monitor.shut_down_after(5)
    monitor.monitor()

    # time.sleep(3)

    # monitor = build_task_monitor()
    # monitor.shut_down_after(5)
    # monitor.monitor()

    # p = Process(target=monitor.monitor, args=())


def build_task_monitor():
    return EmbeddingControlBasedTaskMonitor(VIDEO_CONFIG_DIR / 'video.json', STREAM_SAVE_DIR,
                                            SAMPLE_SAVE_DIR,
                                            FRAME_SAVE_DIR,
                                            CANDIDATE_SAVE_DIR, OFFLINE_STREAM_SAVE_DIR)


def GMG_substractor():
    # cap = cv2.VideoCapture('/Users/luvletteru/Documents/dolphin/2-1/render-streams/02-01-13-08-31-1014.mp4')
    cap = cv2.VideoCapture('/Users/luvletteru/Documents/GitHub/DolphinDetection/data/offline/5/1202.mp4')
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
    while (1):
        ret, frame = cap.read()
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        fgmask = fgbg.apply(frame)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        cv2.imshow('frame', fgmask)
        cv2.waitKey(1)
    # k = cv2.waitKey()
    cap.release()
    cv2.destroyAllWindows()


def MOG2_substractor():
    cap = cv2.VideoCapture('/Users/luvletteru/Documents/GitHub/DolphinDetection/data/offline/5/0201.mov')
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    while (1):
        ret, frame = cap.read()
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        cv2.imshow('frame', frame)
        fgmask = fgbg.apply(frame)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        cv2.imshow('mask', fgmask)
        cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()


def crop_from_frame():
    frame_names = list(Path('/Users/luvletteru/Documents/dolphin/label/negatives').glob('*'))
    output_dir = '/Users/luvletteru/Documents/dolphin/label/crops-sample/other'
    cfg = {}
    for idx, f in enumerate(frame_names):
        frame = cv2.imread(str(f))
        if frame is None:
            continue
        rects = detect(frame)
        print(f)
        if len(rects):
            for rect in rects:
                bbox = crop_by_rect_wh(224, 224, rect, frame)
                cv2.imwrite(os.path.join(output_dir, str(idx) + '.png'), bbox)


def test_hist():
    img1 = cv2.imread('data/test/1202/3.png')
    img2 = cv2.imread('data/test/1202/4.png')
    test_continuous_dir = 'data/test/1202/5'
    frame_names = os.listdir(test_continuous_dir)
    first = cv2.imread(os.path.join(test_continuous_dir, frame_names[0]))
    ssim_res = []
    hist_res = []
    for idx in range(1, len(frame_names)):
        post = cv2.imread(os.path.join(test_continuous_dir, frame_names[idx]))
        if post is None:
            continue
        ssim_res.append(cal_rgb_similarity(first, post, 'ssim'))
        hist_res.append(cal_rgb_similarity(first, post))

    print(cal_std_similarity(ssim_res))
    print(cal_std_similarity(hist_res))

    # img2 = cv2.GaussianBlur(img2, (5, 5), 0, 0)
    # print(cal_hist_cosin_similarity(img1, img2))


if __name__ == '__main__':
    # MOG2_substractor()
    # crop_from_frame()
    test_hist()
    # test_task_monitor(k)
    # test_load_video_json()
    # test_load_label_json()
    # test_video_config()
    # test_read_steam()
    # test_read_frame()
    # test_detect()
    # test_detect_monitor()
    # test_adaptive_thresh()
    # test_pool()
