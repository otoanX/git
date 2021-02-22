from keras.datasets import mnist
import numpy as np
import keras

from keras.backend import tensorflow_backend as backend
from keras.callbacks import TensorBoard
from keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from keras.optimizers import adam
from keras.utils import plot_model


def AE1model():
	input_img = Input(shape=(28, 28, 1))
	x = Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding="same")(input_img)
	x = MaxPooling2D(pool_size=(2, 2), padding='same')(x)
	x = Conv2D(filters=16, kernel_size=(3, 3), activation='relu', padding="same")(x)
	encoded = MaxPooling2D(pool_size=(2, 2), padding='same')(x)

	x = Conv2D(filters=16, kernel_size=(3, 3), activation='relu', padding="same")(encoded)
	x = UpSampling2D(size=(2, 2))(x)
	x = Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding="same")(x)
	x = UpSampling2D(size=(2, 2))(x)
	decoded = Conv2D(filters=1, kernel_size=(3, 3), activation='sigmoid', padding="same")(x)

	return Model(input_img, decoded)

def converter(xarray, yarray, num, outputnum):
	#numで指定されたラベルの値の該当するデータを抽出し，成形する
	xarray = xarray[np.where(yarray == num)[0]]
	xarray = xarray.astype('float32') / 255.0
	xarray = np.reshape(xarray, (len(xarray), outputnum, outputnum, 1))

	return xarray

if __name__ == "__main__":
	#mnist前処理
	(x_train, y_train), (x_test, y_test) = mnist.load_data()
	x_train_1 = converter(x_train, y_train, 1, 28)
	x_test_1 = converter(x_test, y_test, 1, 28)

    #モデルの構築
	model = AE1model()

	#作成したモデルを画像として可視化
	plot_model(model, to_file='modelmnist.png', show_shapes=True)

	model.compile(optimizer='adam', loss='binary_crossentropy')

	tb = TensorBoard(log_dir="./logs")
	history = model.fit(x_train_1, x_train_1,
			            epochs=200,
			            batch_size=256,
			            shuffle=True,
			            validation_data=(x_test_1, x_test_1),
			            callbacks=[tb])

	#学習結果を保存
	json_string = model.to_json()
	open('AE1_mlp_model.json', 'w').write(json_string)
	model.save_weights('AE1_mlp_weights.h5')


