import cv2
import numpy as np
from PIL import Image
import os, glob

# 画像が保存されているルートディレクトリのパス
root_dir = "../damage_data_2_1"
# 数値名
damages = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
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
    data = cv2.imread(fname)
    data_hsv = cv2.cvtColor(data, cv2.COLOR_BGR2HSV)
    result = cv2.inRange(data_hsv, np.array([10, 120, 160]), np.array([40, 255, 255]))
    cv2.imwrite('../save_damage_data/ ' + str(cat) + '.png', result)
    X.append(result)
    Y.append(cat)


# 全データ格納用配列
allfiles = []

# カテゴリ配列の各値と、それに対応するidxを認識し、全データをallfilesにまとめる
for idx, cat in enumerate(damages):
    image_dir = root_dir + "/" + cat
    files = glob.glob(image_dir + "/*.png")
    for f in files:
        allfiles.append((idx, f))

X_train, y_train = make_sample(allfiles)
# データを保存する（データの名前を「damage_data.npy」としている）
np.save("../model/2_1/damage_data_2_1.npy", X_train)
