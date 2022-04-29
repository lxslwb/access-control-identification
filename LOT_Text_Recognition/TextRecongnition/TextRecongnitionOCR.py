from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkocr.v1.region.ocr_region import OcrRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkocr.v1 import *
import re

# 密钥
ak = "3CBKUTN3NETU76TDY1BJ"
sk = "i7RwY5QMOfdk6L21aU2MzfOn4zsfAqnefmUn6k03"

# 手机号码 可能会识别为两行
pattern1 = re.compile(
    '([0-9]{3}[*]{4}[0-9]{4})|([0-9]{3}[*]{4})|([*]{4}[0-9]{4})|([0-9]{4}[\u7684][\u52a8][\u6001][\u884c][\u7a0b][\u5361])')  # 123****1234 or 123**** or ****1234 or 5678的动态行程卡
# 时间 直接匹配
pattern2 = re.compile(
    '([0-9]{4}[.][0-9]{2}[.][0-9]{2}[ ][0-9]{2}[:][0-9]{2}[:][0-9]{2})|([0-9]{4}[.][0-9]{2}[.][0-9]{2}[ ][0-9]{2}[：][0-9]{2}[：][0-9]{2})')  # 1234.12.12 12:12:12 or 1234.12.12 12：12：12
# 地点
pattern3 = re.compile(
    '(([\u4e00-\u9fa5]{0,8}[\u7701])?([\u4e00-\u9fa5]{0,8}[\u5e02]))|([\u4e00-\u9fa5]{0,2}[\u7701])')  # xx省xx市 or xx市 or xx省


def text_identify(image64):
    credentials = BasicCredentials(ak, sk)
    client = OcrClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(OcrRegion.value_of("cn-north-4")) \
        .build()

    try:
        request = RecognizeGeneralTextRequest()
        request.body = GeneralTextRequestBody(
            image=image64
            # url=url
        )
        response = client.recognize_general_text(request)
        dataset = response.result.words_block_list
        phonenumber = []
        now_time = ''
        loc = []
        f_p = False
        f_t = False
        f_l = False
        for data in dataset:
            # 手机
            if not f_p:
                match1 = pattern1.search(data.words)
                if match1:
                    tmp = ''.join(pattern1.findall(data.words)[0])
                    if '动' in tmp:  # 匹配的为group(3)
                        phonenumber.append(tmp[:4])
                    else:
                        phonenumber.append(tmp)
                    if len(''.join(phonenumber)) == 11:
                        f_p = True
                    continue
            # 时间
            if not f_t:
                match2 = pattern2.search(data.words)
                if match2:
                    now_time = ''.join(pattern2.findall(data.words)[0])
                    f_t = True
                    continue
            # 地点
            if not f_l:
                match3 = pattern3.search(data.words)
                if match3:
                    if '或途' in data.words:  # 开始
                        loc.append(data.words)
                    elif '(' in data.words and (not '4' in data.words):  # (注：*表示)
                        loc.append(data.words[:data.words.index('(')])
                        f_l = True
                        break
                    elif not '4' in data.words:  # 非结束语句
                        loc.append(data.words)
                    else:
                        f_l = True
                        break
        if loc:
            f_l = True
        if not f_p or not f_t or not f_l:
            print('无法识别，请重试')
            return None, None, None

        loc_1 = ''.join(loc)
        if ':' in loc_1 or '：' in loc_1:
            # 冒号可能被识别为两种形式
            if loc_1.split('：')[1:]:
                loc_2 = loc_1.split('：')[1:]
            elif loc_1.split(':')[1:]:
                loc_2 = loc_1.split(':')[1:]
        else:
            loc_2 = loc_1

        loc_3 = ''.join(loc_2).replace('，', ',')
        locations = loc_3.split(',')
        phonenumber = ''.join(phonenumber)
        now_time_2 = now_time.replace('：', ':')

        return phonenumber, now_time_2, locations
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)
        print('服务错误')
