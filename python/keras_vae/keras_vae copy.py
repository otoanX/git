'''Example of VAE on MNIST dataset using MLP

The VAE has a modular design. The encoder, decoder and VAE
are 3 models that share weights. After training the VAE model,
the encoder can be used to generate latent vectors.
The decoder can be used to generate MNIST digits by sampling the
latent vector from a Gaussian distribution with mean = 0 and std = 1.

# Reference

[1] Kingma, Diederik P., and Max Welling.
"Auto-Encoding Variational Bayes."
https://arxiv.org/abs/1312.6114

下記サイトで解説している
Keras で変分オートエンコーダ（VAE）をMNISTでやってみる
http://cedro3.com/ai/vae/
Keras VAEの画像異常検出を理解する
http://cedro3.com/ai/keras-vae-anomaly/
python で yes/no で実行する/しないの処理のメモ
https://cortyuming.hateblo.jp/entry/2015/12/26/085736
Keras で変分オートエンコーダ（VAE）をセレブの顔画像でやってみる
http://cedro3.com/ai/keras-vae-celeba/
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from keras.layers import Dense, Input
from keras.layers import Conv2D, Flatten, Lambda
from keras.layers import Reshape, Conv2DTranspose
from keras.models import Model
from keras.datasets import mnist
from keras.losses import mse, binary_crossentropy
from keras.utils import plot_model, np_utils   ### 追加
from keras import backend as K
from keras.preprocessing.image import array_to_img, img_to_array, load_img  ###　追加
from sklearn.model_selection import train_test_split  ### 追加

import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

#import watchdog #更新したファイルを取得する

# reparameterization trick
# instead of sampling from Q(z|X), sample epsilon = N(0,I)
# z = z_mean + sqrt(var) * epsilon
def sampling(args):
    """Reparameterization trick by sampling from an isotropic unit Gaussian.

    # Arguments
        args (tensor): mean and log of variance of Q(z|X)

    # Returns
        z (tensor): sampled latent vector
    """

    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    # by default, random_normal has mean = 0 and std = 1.0
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon

def plot_results(models,
                 data,
                 batch_size=128,
                 model_name="vae_mnist"):
    """Plots labels and MNIST digits as a function of the 2D latent vector

    # Arguments
        models (tuple): encoder and decoder models
        data (tuple): test data and label
        batch_size (int): prediction batch size
        model_name (string): which model is using this function
    """

    encoder, decoder = models
    x_test, y_test = data
    os.makedirs(model_name, exist_ok=True)

    filename = os.path.join(model_name, "vae_mean.png")
    # display a 2D plot of the digit classes in the latent space
    z_mean, _, _ = encoder.predict(x_test,
                                   batch_size=batch_size)
    plt.figure(figsize=(12, 10))
    plt.scatter(z_mean[:, 0], z_mean[:, 1], c=y_test)
    plt.colorbar()
    plt.xlabel("z[0]")
    plt.ylabel("z[1]")
    plt.savefig(filename)
    plt.show()

    filename = os.path.join(model_name, "digits_over_latent.png")
    # display a 30x30 2D manifold of digits
    n = 30
    digit_size = 28
    figure = np.zeros((digit_size * n, digit_size * n))
    # linearly spaced coordinates corresponding to the 2D plot
    # of digit classes in the latent space
    grid_x = np.linspace(-4, 4, n)
    grid_y = np.linspace(-4, 4, n)[::-1]

    for i, yi in enumerate(grid_y):
        for j, xi in enumerate(grid_x):
            z_sample = np.array([[xi, yi]])
            x_decoded = decoder.predict(z_sample)
            digit = x_decoded[0].reshape(digit_size, digit_size)
            figure[i * digit_size: (i + 1) * digit_size,
                   j * digit_size: (j + 1) * digit_size] = digit

    plt.figure(figsize=(10, 10))
    start_range = digit_size // 2
    end_range = (n - 1) * digit_size + start_range + 1
    pixel_range = np.arange(start_range, end_range, digit_size)
    sample_range_x = np.round(grid_x, 1)
    sample_range_y = np.round(grid_y, 1)
    plt.xticks(pixel_range, sample_range_x)
    plt.yticks(pixel_range, sample_range_y)
    plt.xlabel("z[0]")
    plt.ylabel("z[1]")
    plt.imshow(figure, cmap='Greys_r')
    plt.savefig(filename)
    plt.show()

def list_pictures(directory, ext='jpg|jpeg|bmp|png|ppm'):
    return [os.path.join(root, f)
            for root, _, files in os.walk(directory) for f in files
            if re.match(r'([\w]+\.(?:' + ext + '))', f.lower())]

def yes_no_input():
    while True:
        choice = raw_input("Please respond with 'yes' or 'no' [y/N]: ").lower()
        if choice in ['y', 'ye', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False

print("Use MNIST dataset? If you don't use,save 64x64images in ./images/")
if yes_no_input():
    # MNIST dataset
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    image_size = x_train.shape[1]
    image_color = 1
    #original_dim = image_size * image_size
    #x_train = np.reshape(x_train, [-1, original_dim])
    #x_test = np.reshape(x_test, [-1, original_dim])
    x_train = np.reshape(x_train, [-1, image_size,image_size])
    x_test = np.reshape(x_test, [-1, image_size,image_size])
    x_train = x_train.astype('float32') / 255
    x_test = x_test.astype('float32') / 255
else:
    # 自作データセット読み込み
    x = []
    y = []
    image_size = 64 # kerasのload_imgで変換する画像サイズ
    image_color = 3
    #original_dim = 12288
    files = os.listdir("./images")
    files_dir = [f for f in files if os.path.isdir(os.path.join("./images", f))]
    for i,path in enumerate(files_dir,0):
        for picture in list_pictures(path):
            img = img_to_array(load_img(picture, target_size=(image_size,image_size)))  
            x.append(img)
            y.append(i)

    x = np.asarray(x)
    y = np.asarray(y)

    x = x.astype('float32')
    x = x/ 255.0    #正規化
    y = np_utils.to_categorical(y, len(files_dir))   #ラベルをベクトルに変換 

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=111)  #データを学習用80%評価用20%に分ける


# network parameters
input_shape = (image_size,image_size,image_color)
intermediate_dim = 16  #中間層の数
batch_size = 128
kernel_size = 3
filters = 32 #16→32に変更
latent_dim = 2  #潜在変数の次元数？latent：潜在
epochs = 50

# VAE model = encoder + decoder
# build encoder model
inputs = Input(shape=input_shape, name='encoder_input') #kerasのINPUTレイヤー
x = inputs
for i in range(3):   ### 2 → 3 に変更
    filters *= 2    
    x = Conv2D(filters=filters,
               kernel_size=kernel_size,
               activation='relu',
               strides=2,
               padding='same')(x)
 
# shape info needed to build decoder model
shape = K.int_shape(x)
 
# generate latent vector Q(z|X)
x = Flatten()(x)
x = Dense(intermediate_dim, activation='relu')(inputs) #Dense:kerasの全結合ニューラルネットワークレイヤー
z_mean = Dense(latent_dim, name='z_mean')(x)
z_log_var = Dense(latent_dim, name='z_log_var')(x)

# use "reparameterization trick" to push the sampling out as input
# ↑vaeはサンプリングという行為のせいで順伝搬が途切れるらしい。そこで「Reparameterization trick」を使って伝搬を繋げる。https://qiita.com/cympfh/items/50b19933fd3834e86862
# note that "output_shape" isn't necessary with the TensorFlow backend
z = Lambda(sampling, output_shape=(latent_dim,), name='z')([z_mean, z_log_var])

# instantiate encoder model
# 上で設計したモデルをインスタンス化(具現化)して使えるようにする
encoder = Model(inputs, [z_mean, z_log_var, z], name='encoder')
encoder.summary()   # モデルの要約を出力する
#plot_model(encoder, to_file='vae_mlp_encoder.png', show_shapes=True)

# build decoder model
latent_inputs = Input(shape=(latent_dim,), name='z_sampling')
#x = Dense(intermediate_dim, activation='relu')(latent_inputs)
#outputs = Dense(original_dim, activation='sigmoid')(x)
x = Dense(shape[1] * shape[2] * shape[3], activation='relu')(latent_inputs)
x = Reshape((shape[1], shape[2], shape[3]))(x)
for i in range(3):   ###　2 → 3 に変更
    x = Conv2DTranspose(filters=filters,
                        kernel_size=kernel_size,
                        activation='relu',
                        strides=2,
                        padding='same')(x)
    filters //= 2
outputs = Conv2DTranspose(filters=3,                 ### 1 → 3 に変更
                          kernel_size=kernel_size,
                          activation='sigmoid',
                          padding='same',
                          name='decoder_output')(x)

# instantiate decoder model
decoder = Model(latent_inputs, outputs, name='decoder')
decoder.summary()   # モデルの要約を出力する
#plot_model(decoder, to_file='vae_mlp_decoder.png', show_shapes=True)

# instantiate VAE model
outputs = decoder(encoder(inputs)[2])
vae = Model(inputs, outputs, name='vae_mlp')

if __name__ == '__main__':  # pythonファイルとして実行された場合(importされたときは実行しない)
    parser = argparse.ArgumentParser()  #パーサーを作る
    parser.add_argument("-w", "--weights", help="Load h5 model trained weights")
    parser.add_argument("-m",
                        "--mse",
                        help="Use mse loss instead of binary cross entropy (default)", action='store_true')
    args = parser.parse_args()  #コマンドライン引数を解析
    models = (encoder, decoder)
    data = (x_test, y_test)

    # VAE loss = mse_loss or xent_loss + kl_loss
    if args.mse:    #コマンドラインで平均二乗誤差が指定された場合
        reconstruction_loss = mse(inputs, outputs)  #損失関数に平均二乗誤差を使う
    else:
        reconstruction_loss = binary_crossentropy(inputs,
                                                  outputs)  #損失関数に二値交差エントロピーを使う

    reconstruction_loss *= original_dim
    kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
    kl_loss = K.sum(kl_loss, axis=-1)
    kl_loss *= -0.5
    vae_loss = K.mean(reconstruction_loss + kl_loss)
    vae.add_loss(vae_loss)
    vae.compile(optimizer='adam')
    vae.summary()
    plot_model(vae,
               to_file='vae_mlp.png',
               show_shapes=True)

    if args.weights:    #コマンドラインで重みファイルが指定された場合
        vae.load_weights(args.weights)  #モデルの重みをHDF5形式のファイルから読み込み
    else:
        # train the autoencoder
        vae.fit(x_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(x_test, None))
        vae.save_weights('vae_mlp_mnist.h5')

    plot_results(models,
                 data,
                 batch_size=batch_size,
                 model_name="vae_mlp")