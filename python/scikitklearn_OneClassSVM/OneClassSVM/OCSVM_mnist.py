from keras.datasets import mnist
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm

def mnist_Preprocessing():
	#mnist前処理
	(x_train, y_train), (x_test, y_test) = mnist.load_data()
	x_train_1 = converter(x_train, y_train, 1, 784)
	x_test_1 = converter(x_test, y_test, 1, 784)
	x_test_7 = converter(x_test, y_test, 7, 784)
	return x_train_1, x_test_1, x_test_7

def converter(xarray, yarray, num, outputnum):
	#numで指定されたラベルの値の該当するデータを抽出し，成形する
	xarray = xarray[np.where(yarray == num)[0]]
	xarray = xarray.astype('float32') / 255.0
	xarray = np.reshape(xarray, (len(xarray),outputnum))
	return xarray

def execute_OCSVM(x_train_1, x_test_1, x_test_7):
	#One Class SVM を実行
	clf = svm.OneClassSVM(nu=0.2, kernel="rbf", gamma=0.001)
	clf.fit(x_train_1)
	#配列の頭から「１」を100個，「７」を20個取り出し予想
	test = np.vstack((x_test_1[0:100], x_test_7[0:20]))
	pred = clf.predict(test)
	return pred

def evaluate(pred):
	#accracyの計算
	answer = np.array([1] * 100 + [-1] * 20)
	acc =  len(pred[pred == answer])/120.0
	print("accuracy : " + str(acc))

def show_Graph(pred):
	#予想された値をグラフ化し表示・保存
	x = np.arange(0, 120, 1)
	plt.plot(x, pred)
	plt.savefig('SVMmnist.png')
	plt.show()

if __name__ == "__main__":
	x_train_1, x_test_1, x_test_7 = mnist_Preprocessing()
	pred = execute_OCSVM(x_train_1, x_test_1, x_test_7)
	evaluate(pred)
	show_Graph(pred)

