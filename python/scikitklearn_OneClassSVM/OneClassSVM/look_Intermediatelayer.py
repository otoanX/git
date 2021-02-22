from keras.datasets import mnist
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm

from keras.models import model_from_json
from keras.models import Model

def mnist_Preprocessing():
	#mnist前処理
	(x_train, y_train), (x_test, y_test) = mnist.load_data()
	x_train_1 = converter(x_train, y_train, 1, 28)
	x_test_1 = converter(x_test, y_test, 1, 28)
	x_test_7 = converter(x_test, y_test, 7, 28)

    # モデルを読み込む
	model = model_from_json(open('AE1_mlp_model.json').read())
	# 学習結果を読み込む
	model.load_weights('AE1_mlp_weights.h5')

	layer_name = 'conv2d_3'
	hidden_later_model = Model(inputs=model.input, outputs=model.get_layer(layer_name).output)

	x_train_1 = hidden_later_model.predict(x_train_1)
	x_test_1 = hidden_later_model.predict(x_test_1)
	x_test_7 = hidden_later_model.predict(x_test_7)

	return x_train_1, x_test_1, x_test_7

def converter(xarray, yarray, num, outputnum):
	#numで指定されたラベルの値の該当するデータを抽出し，成形する
	xarray = xarray[np.where(yarray == num)[0]]
	xarray = xarray.astype('float32') / 255.0
	xarray = np.reshape(xarray, (len(xarray), outputnum, outputnum, 1))
	return xarray

def show_IntermediatelayerImage(array, image_num, width, height, filter_num, filename):
	#中間層出力画像表示・保存(表示したい中間層配列，表示したい枚数，中間層画像の横幅，中間層画像の縦幅，中間層のフィルタ数，保存ファイルネーム（拡張子無し）)
	for i in range(image_num):
		plt.figure(figsize=(3, 3))
		for j in range(filter_num):
			ax = plt.subplot(4, 4, j+1)
			plt.imshow(array[i,:,:,j].reshape(width, height))
			plt.gray()
			ax.get_xaxis().set_visible(False)
			ax.get_yaxis().set_visible(False)
			plt.savefig(filename+ str(i) + ".png")
	plt.show()
	plt.close()

if __name__ == "__main__":
	x_train_1, x_test_1, x_test_7 =  mnist_Preprocessing()
	show_IntermediatelayerImage(x_test_1, 3, 7, 7, 16, "look")


