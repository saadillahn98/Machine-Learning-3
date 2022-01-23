# -*- coding: utf-8 -*-
"""Submission Terakhir

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OrKLm-8dCP75m9ydl0BYeAEkL5TrV1DR

**IMAGE CLASSIFICATION PROJECT**<br>
Dibuat oleh : Saadillah Noer<br>
Email : saadillahnoer@gmail.com

**Import Libraries**<br>
"""

import tensorflow as tf
tf.test.gpu_device_name()

from tensorflow.python.client import device_lib
device_lib.list_local_devices()

import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

from google.colab import drive
drive.mount('/content/drive')

import os
os.environ['KAGGLE_CONFIG_DIR'] = "/content/drive/MyDrive/Dataset_img"

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/

!ls

"""**Splitting Data**<br>"""

base_dir = "/content/drive/MyDrive/Split"
data_dir = "/content/drive/MyDrive/Dataset_img"

pip install split-folders

import splitfolders
splitfolders.ratio(data_dir, output=base_dir, seed=1337, ratio=(.60, .40))

!ls Split

"""**Processing Data**<br>"""

import os

train_path = os.path.join(base_dir, 'train')
val_path = os.path.join(base_dir, 'val')

#Augmentasi Dataset
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils import shuffle

batch_size = 16
Augmentasi_gen = ImageDataGenerator(rescale=1. / 255,
                                    rotation_range=20,
                                    width_shift_range=0.2,
                                    height_shift_range=0.2,
                                    zoom_range=0.2,
                                    horizontal_flip=True,
                                    fill_mode = 'nearest')

Augmentasi_genz = ImageDataGenerator(rescale=1. / 255,
                                    rotation_range=20,
                                    width_shift_range=0.2,
                                    height_shift_range=0.2,
                                    zoom_range=0.2,
                                    horizontal_flip=True,
                                    fill_mode = 'nearest')

train_gen = Augmentasi_gen.flow_from_directory(
    train_path,
    class_mode = 'categorical',
    shuffle = True,
    target_size=(224, 224),
    batch_size=batch_size,
    color_mode = 'rgb'
)
val_gen = Augmentasi_gen.flow_from_directory(
    val_path,
    class_mode = 'categorical',
    shuffle = True,
    target_size=(224, 224),
    batch_size=batch_size,
    color_mode='rgb'
)

"""**Arsitektur Model 3 Conv & 2 Hidden Layer**<br>"""

import tensorflow as tf
model = tf.keras.models.Sequential([
                                    # bentuk input adalah ukuran gambar yang diinginkan 150x150 dengan warna 3 byte color
                                    tf.keras.layers.Conv2D(64, (3,3), activation='relu', input_shape=(224, 224, 3)),
                                    tf.keras.layers.MaxPooling2D(2,2),
                                    tf.keras.layers.Conv2D(32, (3,3), strides=(1,1), activation='relu'),
                                    tf.keras.layers.MaxPool2D(2,2),
                                    tf.keras.layers.Dropout(0.4),
                                    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
                                    tf.keras.layers.MaxPool2D(2,2),
                                    # Flatten the results to feed into a DNN
                                    tf.keras.layers.Flatten(),
                                    # 512 neuron hidden layer
                                    tf.keras.layers.Dense(512, activation='relu'),
                                    tf.keras.layers.Dense(256, activation='relu'),
                                    # Only 1 output neuron. It will contain a value from 0-1 where 0 for 1 class ('cats') and 1 for the other ('dogs')
                                    tf.keras.layers.Dense(3, activation='softmax')
])

"""**Optimizer dan Loss**<br>"""

model.compile(optimizer=tf.optimizers.Adam(),
              loss='categorical_crossentropy',
              metrics = ['accuracy'])

"""**Memanggil fungsi fit**<br>"""

history = model.fit(train_gen,
                    validation_data=val_gen,
                    epochs=10,
                    verbose=2)

"""**Plot Akurasi Model**"""

#Plot akurasi dari model
import matplotlib.pyplot as plt
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Akurasi Model')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""**Plot Akurasi Loss**"""

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""**Menyimpan model kedalam TF.Lite**"""

converter_model = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter_model.convert()
# Save the model.
with open('model.tflite', 'wb') as f:
  f.write(tflite_model)

model.save('model xor.h5')

"""**Pisahkan Dataset dan Train set**"""

EPOCH = 10
history = model.fit(x=train_gen,
        steps_per_epoch=len(train_gen),
        epochs=EPOCH,
        validation_data=val_gen,
        validation_steps=len(val_gen),
        shuffle=True,
        verbose = 2)

"""**Model Callback**<br>"""

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.91 and logs.get('val_accuracy')>0.94):
      print("\nAccuracy above 91%, finish training!")
      self.model.stop_training = True

callbacks = myCallback()