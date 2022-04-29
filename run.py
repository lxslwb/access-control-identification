from LOT_Text_Recognition.TextRecongnition.TextRecongnitionOCR import text_identify
from LOT_Face_Recognition.single_face_feature import face_init
from LOT_Face_Recognition.single_face_feature import single_face
from LOT_Face_Recognition.single_face_feature import campare_face
from LOT_Face_Recognition.arcface.engine import *
from flask import Flask
from flask import request as frq
from io import BytesIO
import requests
import pymysql
import cv2 as cv
import numpy as np
import base64
import json
import time



# 预处理函数

# 图片处理
def preimg(url):
    response = requests.get(url)
    img_array = np.array(bytearray(response.content), dtype=np.uint8)
    img = cv.imdecode(img_array, cv.IMREAD_COLOR)
    return img


def urlimgto64(url):
    img = preimg(url)
    # 图片的高度裁剪
    s = img.shape
    if s[0] > 1024:
        k = 1 / (s[0] // 1024)
        img_new = cv.resize(img, None, fx=k, fy=k, interpolation=cv.INTER_AREA)
        image = cv.imencode('.jpg', img_new)[1]
    else:
        image = cv.imencode('.jpg',img)[1]
    ls_f = base64.b64encode(image)
    image64 = str(ls_f)[2:-1]
    return image64

# def urlimgto64(url):
#     response = requests.get(url)
#     ls_f = base64.b64encode(BytesIO(response.content).read())
#     image64 = str(ls_f)[2:-1]
#     return image64


def BytesToStr(b):
    b_64 = base64.b64encode(b)
    b_str = str(b_64, 'utf-8')
    return b_str


def StrToBytes(s):
    if s[1]:
        s_64 = s[1].encode('utf-8')
        s_bytes = base64.b64decode(s_64)
    else:
        s_bytes = None
    return [s[0], s_bytes]


# 数据库查找

def find_feature():
    db = pymysql.connect(host='121.36.32.21', user='root', password='UCAS.Light/1', port=3306,
                         database='iot_competetion')
    cursor = db.cursor()
    sql = "SELECT `visitor_id`, `feature` FROM `visitor`"
    cursor.execute(sql)
    res = cursor.fetchall()
    db.close()
    res2 = list(map(list, res))
    res3 = list(map(StrToBytes, res2))  # [['id',b''],[],]
    return res3


# 初始化
app = Flask(__name__)
face_engine = face_init()


# 后台交互
@app.route('/face', methods=['get'])
def get_face_url():
    url = frq.args.get('url')
    img = preimg(url)
    img_face = single_face(img, face_engine)
    # 原始
    visitor_id = '0'
    score = 0
    img_feature = BytesToStr(img_face.get_feature_bytes())
    # 获取数据库的所有人脸特征值
    sql_face = find_feature()
    # 特征值比对
    for p_id, p_f in sql_face:
        p = ASF_FaceFeature()
        p.set_feature(p_f)
        score_t = campare_face(face_engine, p, img_face)
        if score_t > score:
            score = score_t
            visitor_id = p_id
    if score < 0.9:
        visitor_id = '0'
    res = {'visitor_id': visitor_id, 'feature': img_feature}
    res_json = json.dumps(res, ensure_ascii=False)
    return res_json


@app.route('/trip', methods=['get'])
def get_trip_url():
    url = frq.args.get('url')
    image64 = urlimgto64(url)
    pho, t, loc = text_identify(image64)
    is_star = False
    for i in loc:
        if '*' in i:
            is_star = True
            break
    res = {'phone': pho, 'date': t, 'trips': loc, 'haveStar': is_star}
    res_json = json.dumps(res, ensure_ascii=False)
    return res_json


if __name__ == '__main__':
    app.run(debug=False)
    face_engine.ASFUninitEngine()  # 引擎反初始化
