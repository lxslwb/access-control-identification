import cv2

# 4096 15
img = cv2.imread('/home/wb/Code/lot/LOT_4_linux/images/xingchengka/带星测试图片1.jpg')
s = img.shape
if s[0] > 1024:
    k = 1 / (s[0] // 1024)
    img_new = cv2.resize(img, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    s_new = img_new.shape
    cv2.imwrite('/home/wb/Code/lot/LOT_4_linux/images/xingchengka/带星测试图片1_new.jpg', img_new)
    print(s)
    print(s_new)
