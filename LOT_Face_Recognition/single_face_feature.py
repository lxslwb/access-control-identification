import cv2 as cv
import requests
import numpy as np
from ctypes import *
from LOT_Face_Recognition.arcface.engine import *

# 密钥
# windows
# APPID = b'EuHywXDfSnVomTUwe2ZPNL3Q1fJLPoK7PF6sr78WZAGf'
APPID = b'EzfcrVSSNCm33x8MLpkLi7dG4DKB72J5wy9AppiKgVYj'
# window
# SDKKey = b'EbfZJ4HPJaw7AgjZeEM3dVSjq1g5nC1dmSH755j1tveX'
SDKKey = b'DmBt5Aiz9XASi83VCN6gzohj7qbAmwwPC2yyZyEj5gUq'

# 需要引擎开启的功能
mask = ASF_FACE_DETECT | ASF_FACERECOGNITION | ASF_AGE | ASF_GENDER | ASF_FACE3DANGLE | ASF_LIVENESS | ASF_IR_LIVENESS


def face_init():
    res = ASFOnlineActivation(APPID, SDKKey)
    if MOK != res and MERR_ASF_ALREADY_ACTIVATED != res:
        print("ASFActivation fail: {}".format(res))
    else:
        pass
        # print("ASFActivation sucess: {}".format(res))
    res, activeFileInfo = ASFGetActiveFileInfo()
    if res != MOK:
        print("ASFGetActiveFileInfo fail: {}".format(res))
    else:
        pass
        # print(activeFileInfo)
    face_engine = ArcFace()
    res = face_engine.ASFInitEngine(ASF_DETECT_MODE_IMAGE, ASF_OP_0_ONLY, 30, 10, mask)
    if res != MOK:
        print("ASFInitEngine fail: {}".format(res))
    else:
        pass
        # print("ASFInitEngine sucess: {}".format(res))
    return face_engine


def imgresize(image):
    s = image.shape
    img_new = cv.resize(image, dsize=(s[1] // 4 * 4, s[0] // 4 * 4))
    return img_new


def single_face(img, face_engine):
    img_new = imgresize(img)
    res, detectedFaces = face_engine.ASFDetectFaces(img_new)
    if res == MOK:
        single_detected_face = ASF_SingleFaceInfo()
        single_detected_face.faceRect = detectedFaces.faceRect[0]
        single_detected_face.faceOrient = detectedFaces.faceOrient[0]
        res, face_feature = face_engine.ASFFaceFeatureExtract(img_new, single_detected_face)
        if res != MOK:
            print("ASFFaceFeatureExtract 1 fail: {}".format(res))
    else:
        print("ASFDetectFaces 1 fail: {}".format(res))
    return face_feature


def campare_face(face_engine, asf_face1, asf_face2):
    res, score = face_engine.ASFFaceFeatureCompare(asf_face1, asf_face2)
    return score

