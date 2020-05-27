#データをOneClassSVMで学習する。
#フォルダを監視して、新規画像をOneClassSVMで予測して結果を返す

import numpy as np
import matplotlib.pyplot as plt

#「Qiita」One Class SVMを使ってMNISTの数字画像の異常検知がしたい@satoshi_y
# https://qiita.com/satoshi_y/items/5573cacb64168a7a73ed
# https://github.com/mituki-suzu/OneClassSVM.git
#scikit-learnの日本語ドキュメント
# https://qh73xebitbucketorg.readthedocs.io/ja/latest/1.Programmings/python/LIB/scikit-learn/main/
from sklearn import svm

#System.IO.FileSystemWatcherによるフォルダ監視
#「日曜プログラマーの休日」フォルダ、ファイルの変更を監視する
#http://www.ops.dti.ne.jp/ironpython.beginner/FileSystemWatcher.html
import System
from System.IO import FileSystemWatcher
from System.IO.NotifyFilters import FileName, DirectoryName, LastWrite
from System.IO.WatcherChangeTypes import All
from System.IO.WatcherChangeTypes import Created, Changed, Renamed,　Deleted

def oneclasssvm_fix(train_data):
	clf = svm.OneClassSVM(nu=0.2, kernel="rbf", gamma=0.001)    #分類器宣言
	clf.fit(train_data) #学習実施
    return clf  #clfは分類器の略

def oneclasssvm_pred(test_data):
    pred = clf.predict(test_data)   #予測実施
    return pred #予測結果を返す

def fileadd_check():
    watch = FileSystemWatcher()
    watch.Path = "C:/" #監視するディレクトリのパス
    watch.Filter = "*.jpg"  #監視するファイルの拡張子
    watch.IncludeSubdirectories = False #サブディレクトリを監視するのかを指定
    watch.NotifyFilters = FileName | DirectoryName | LastWrite  #どんな変更を監視するか指定する
        #監視できる変更リスト(importが必要)
        #Attributes	ファイルまたはフォルダの属性。
        #CreationTime	ファイルまたはフォルダが作成された時刻。
        #DirectoryName	ディレクトリ名。
        #FileName	ファイルの名前。
        #LastAccess	ファイルまたはフォルダを最後に開いた日付。
        #LastWrite	ファイルまたはフォルダへの最終書き込み日付。
        #Security	ファイルまたはフォルダのセキュリティ設定。
        #Size	ファイルまたはフォルダのサイズ。

if __name__ = "__main__":
    fileadd_check() #System.IO.FileSystemWatcherを使った監視の設定
    try:    #例外(実行中のエラー)が無いときの処理
        while true:
            changedResult = watch.WaitForChanged(All,1) #監視開始(監視時間はミリ秒。-1で無限。)
            if changedResult.ChangeType == Created:
                pred = oneclasssvm_pred(changedResult.Name.ToString())
    except KeyboardInterrupt:   #Ctrl+Cが押されたときの処理
        print("監視を終了します")
