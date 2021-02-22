#データをOneClassSVMで学習する。
#フォルダを監視して、新規画像をOneClassSVMで予測して結果を返す

import numpy as np
import matplotlib.pyplot as plt

#scikit-learnの日本語ドキュメント：https://qh73xebitbucketorg.readthedocs.io/ja/latest/1.Programmings/python/LIB/scikit-learn/main/
from sklearn import svm

#watchdogによるフォルダ監視
# 「python入門ブログ python初心者による初心者のための入門ブログです！」2017/6/27 pythonでフォルダを監視する
# https://python-minutes.blogspot.com/2017/06/python.html
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import os
import time

def oneclasssvm_fix(train_data):
	clf = svm.OneClassSVM(nu=0.2, kernel="rbf", gamma=0.001)    #分類器宣言
	clf.fit(train_data) #学習実施
    return clf  #clfは分類器の略

def oneclasssvm_pred(test_data):
    pred = clf.predict(test_data)   #予測実施
    return pred #予測結果を返す

class ChangeHandler(FileSystemEventHandler、target_dir):
    self.target_dir = target_dir
    def on_created(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        print('%sができました' % filename)
        pred = oneclasssvm_pred(filename)
        print ("予測結果：",pred)

    def on_modified(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        print('%sを変更しました' % filename)

    def on_deleted(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        print('%sを削除しました' % filename)


if __name__ = "__main__":
    target_dir = "c:/"
    while 1:
        event_handler = ChangeHandler(,target_dir)
        observer = Observer()
        observer.schedule(event_handler, target_dir, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:   #Ctrl+Cが押されたときの処理
            observer.stop()
        observer.join()