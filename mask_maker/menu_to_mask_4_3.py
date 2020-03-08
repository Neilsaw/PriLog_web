import cv2
import numpy as np
from PIL import Image
import os, glob

# 画像が保存されているルートディレクトリのパス
root_dir = "../menu"
# 時間名
timers = [
    "menu",
]

# 画像データ用配列
X = []
# ラベルデータ用配列
Y = []


# 画像データごとにadd_sample()を呼び出し、X,Yの配列を返す関数
def make_sample(files):
    global X, Y
    X = []
    Y = []
    for cat, fname in files:
        add_sample(cat, fname)
    return np.array(X), np.array(Y)


# 渡された画像データを読み込んでXに格納し、また、
# 画像データに対応するcategoriesのidxをY格納する関数
def add_sample(cat, fname):
    img = Image.open(fname)
#    img = img.resize((10, 14))
    data = np.asarray(img)
    data_gray = cv2.cvtColor(data, cv2.COLOR_RGB2GRAY)
    ret, result = cv2.threshold(data_gray, 180, 255, cv2.THRESH_BINARY)
    invResult = cv2.bitwise_not(result)
    cv2.imwrite('../menu/ ' + str(cat) + '.png', invResult)
    X.append(invResult)
    Y.append(cat)


# 全データ格納用配列
allfiles = []

# カテゴリ配列の各値と、それに対応するidxを認識し、全データをallfilesにまとめる
for idx, cat in enumerate(timers):
    image_dir = root_dir + "/" + cat
    files = glob.glob(image_dir + "/*.png")
    for f in files:
        allfiles.append((idx, f))

X_train, y_train = make_sample(allfiles)
# データを保存する（データの名前を「menu.npy」としている）
np.save("../model/4_3/menu_4_3.npy", X_train[0])
