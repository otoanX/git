#データをOneClassSVMで学習する。
#フォルダを監視して、新規画像をOneClassSVMで予測して結果を返す

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image   #画像表示
import os

#「Qiita」One Class SVMを使ってMNISTの数字画像の異常検知がしたい@satoshi_y
# https://qiita.com/satoshi_y/items/5573cacb64168a7a73ed
# https://github.com/mituki-suzu/OneClassSVM.git
#scikit-learnの日本語ドキュメント
# https://qh73xebitbucketorg.readthedocs.io/ja/latest/1.Programmings/python/LIB/scikit-learn/main/
from sklearn import svm

#System.IO.FileSystemWatcherによるフォルダ監視
#「日曜プログラマーの休日」フォルダ、ファイルの変更を監視する
#http://www.ops.dti.ne.jp/ironpython.beginner/FileSystemWatcher.html
#import System
from System.IO import FileSystemWatcher
from System.IO.NotifyFilters import FileName, DirectoryName, LastWrite
from System.IO.WatcherChangeTypes import All
from System.IO.WatcherChangeTypes import Created, Changed, Renamed, Deleted

def imageopen():
    for file in os.listdir():
        base, ext = os.path.splitext(file)
        if ext == '.jpg':
            #print('file:{},ext:{}'.format(file,ext))
            print(file)
            image += np.array(Image.open(file))
    image = converter(image,1,1,784)
    return image

def converter(xarray, yarray, num, outputnum):
	#numで指定されたラベルの値の該当するデータを抽出し，成形する
	xarray = xarray[np.where(yarray == num)[0]]
	xarray = xarray.astype('float32') / 255.0
	xarray = np.reshape(xarray, (len(xarray),outputnum))
	return xarray

class Oneclasssvm:
    def fix(self,train_data):
        self.train_data = train_data
        clf = svm.OneClassSVM(nu=0.2, kernel="rbf", gamma=0.001)    #分類器宣言#clfは分類器の略
        clf.fit(self.train_data) #学習実施
    def pred(self,test_data):
        self.test_data = test_data
        pred = clf.predict(self.test_data)   #予測実施
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

if __name__ == "__main__" :
    train_data = imageopen()

    oneclasssvm = Oneclasssvm()
    oneclasssvm.fix(train_data)

    fileadd_check() #System.IO.FileSystemWatcherを使った監視の設定
    try:    #例外(実行中のエラー)が無いときの処理
        while true:
            changedResult = watch.WaitForChanged(All,1) #監視開始(監視時間はミリ秒。-1で無限。)
            if changedResult.ChangeType == Created:
                pred = oneclasssvm.pred(changedResult.Name.ToString())
    except KeyboardInterrupt:   #Ctrl+Cが押されたときの処理
        print("監視を終了します")
