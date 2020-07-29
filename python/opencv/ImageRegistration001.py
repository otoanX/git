#Pythonを使ったずれ補正
#https://lp-tech.net/articles/SSUMl

import numpy as np
import matplotlib.pyplot as plt
#%matplotlib inline
import cv2

filename_li = ["a.png", "b.png", "c.png"]
img_li = []
for i in filename_li:
    img = cv2.imread(i, 0)    # 第二引数を 0 にすることでグレースケールで読み込む
    img_float = np.float32(img)    # cv2.phaseCorrelate で指定されている型に変換
    img_li.append(img_float)
    

dxdy_li = []
for img in img_li[1:]:
    d, etc = cv2.phaseCorrelate(img, img_li[0])    # d にx方向およびy方向のズレが格納されている
    dx, dy = d
    dxdy_li.append([dx, dy])
    
rows, cols = img_li[0].shape
img_after_li = [img_li[0]]
for dxdy, img in zip(dxdy_li, img_li[1:]):
    dx, dy = dxdy
    M = np.float32([[1, 0, dx],[0, 1, dy]])
    img = cv2.warpAffine(img, M, (cols,rows))
    img_after_li.append(img)
    
fig = plt.figure(figsize = (6, 6))    

subplot_li = [321, 323, 325]
for subplot, img in zip(subplot_li, img_li):
    ax = fig.add_subplot(subplot)
    ax.imshow(img)

subplot_after_li = [322, 324, 326]
for subplot_after, img_after in zip(subplot_after_li, img_after_li):
    ax = fig.add_subplot(subplot_after)
    ax.imshow(img_after)

plt.savefig('test.png', format = 'png', dpi=300)
plt.show()