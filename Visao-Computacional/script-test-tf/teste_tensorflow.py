from tensorflow import keras
from keras import datasets
from keras import models
from keras import layers
from keras.utils import to_categorical
#
# Load MNIST data
#
(train_images, train_labels), (test_images, test_labels) = datasets.mnist.load_data()
#
# Create network comprising of two dense (fully connected) layers
#
network = models.Sequential()
network.add(layers.Dense(512, activation='relu', input_shape=(28 * 28,), name="layer1"))
network.add(layers.Dense(10, activation='softmax', name="layer2"))
#
# Prepare the training images and training labels
#
train_images = train_images.reshape((60000, 28 * 28))
train_images = train_images.astype('float32') / 255
train_labels = to_categorical(train_labels)
#
# Prepare the test images and test labels
#
test_images = test_images.reshape((10000, 28 * 28))
test_images = test_images.astype('float32') / 255
test_labels = to_categorical(test_labels)
#
# Prepare the network
#
network.compile(optimizer='rmsprop',
                loss='categorical_crossentropy',
                metrics=['accuracy'])
#
# Fit the neural network
#
network.fit(train_images, train_labels, epochs=5, batch_size=128)
#
# Evaluate the network performance
#
test_loss, test_acc = network.evaluate(test_images, test_labels)
#
# Print the accuracy
#
print('test_acc:', test_acc)