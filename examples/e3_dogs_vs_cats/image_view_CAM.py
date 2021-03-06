from keras.applications import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input, decode_predictions
import numpy as np
from keras import backend as K

model = VGG16(weights='imagenet')
img_path = 'D:\\all-dataset\\dogs-vs-cats-small\\test\dogs\\dog.1500.jpg'
img = image.load_img(img_path, target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)
preds = model.predict(x)
print('predict:', decode_predictions(preds, top=3)[0])
index = np.argmax(preds[0])
print('index=', index)

dogs_output = model.output[:, index]
last_conv_layer = model.get_layer('block5_conv3')
grads = K.gradients(dogs_output, last_conv_layer.output)[0]
pooled_grads = K.mean(grads, axis=(0, 1, 2))
iterate = K.function([model.input], [pooled_grads, last_conv_layer.output[0]])
pooled_grads_value, conv_layer_output_value = iterate([x])

for i in range(512):
    conv_layer_output_value[:, :, i] *= pooled_grads_value[i]
heatmap = np.mean(conv_layer_output_value, axis=-1)
heatmap = np.maximum(heatmap, 0)
heatmap /= np.max(heatmap)

import matplotlib.pyplot as plt
import matplotlib.image as  mimage
# plt.matshow(heatmap)
# plt.show()
import cv2

oriimg = cv2.imread(img_path)
heatmap = cv2.resize(heatmap, (oriimg.shape[1], oriimg.shape[0]))
heatmap = np.uint8(255 * heatmap)
heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
superimposed_img = heatmap * 0.4 + oriimg
cv2.imwrite('dog_CAM.jpg', superimposed_img)
plt.imshow(mimage.imread('dog_CAM.jpg'))
plt.show()
