import os

imdb_dir = 'D:\\all-dataset\\aclImdb'
train_dir = os.path.join(imdb_dir, 'train')
labels = []
texts = []

for label_type in ['neg', 'pos']:
    dir_name = os.path.join(train_dir, label_type)
    for fname in os.listdir(dir_name):
        if fname[-4:] == '.txt':
            f = open(os.path.join(dir_name, fname), encoding='utf-8')
            texts.append(f.read())
            f.close()
            if label_type == 'neg':
                labels.append(0)
            else:
                labels.append(1)

print('texts', len(texts))

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np

maxlen = 500
training_samples = 15000
validation_sample = 10000
max_words = 15000
# 分词器
tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(texts)
# 转为序列
sequences = tokenizer.texts_to_sequences(texts)
print('sequences:', len(sequences))
word_index = tokenizer.word_index
data = pad_sequences(sequences, maxlen=maxlen)
print(data[0])
labels = np.asarray(labels)
print('data shape =', data.shape)
print('lables shape =', labels.shape)
indices = np.arange(data.shape[0])
np.random.shuffle(indices)
data = data[indices]
labels = labels[indices]

x_train = data[:training_samples]
y_train = labels[:training_samples]
x_val = data[training_samples:training_samples + validation_sample]
y_val = labels[training_samples:training_samples + validation_sample]

glove_fpath = 'D:\\all-dataset\\glove.6B\\glove.6B.100d.txt'
embeddings_index = {}
f = open(glove_fpath, encoding='utf-8')
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()

# CloVe词嵌入矩阵
embedding_dim = 100
embedding_matrix = np.zeros((max_words, embedding_dim))
for word, i in word_index.items():
    if i < max_words:
        embedding_vec = embeddings_index.get(word)
        if embedding_vec is not None:
            embedding_matrix[i] = embedding_vec

# model
from keras.models import Sequential
from keras import optimizers
from keras.layers import Embedding, Flatten, Dense, LSTM, Bidirectional

model = Sequential()
model.add(Embedding(max_words, embedding_dim, input_length=maxlen))
# 添加双向RNN,精度提高，出现过拟合，加dropout
model.add(Bidirectional(LSTM(embedding_dim, dropout=0.3, recurrent_dropout=0.5)))
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# 冻结预训练层
model.layers[0].set_weights([embedding_matrix])
model.layers[0].trainable = False
# ,decay=0.9, epsilon=1e-6
model.compile(optimizer=optimizers.RMSprop(lr=0.002), loss='binary_crossentropy',
              metrics=[
                  'acc'])
# model.compile(optimizer=optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-8),
#               loss='binary_crossentropy', metrics=['acc'])
model.summary()
# 使用GPU
import tensorflow as tf
import keras.backend.tensorflow_backend as KTF
KTF.set_session(tf.Session(config=tf.ConfigProto(device_count={'gpu': 0})))

history = model.fit(x_train, y_train, epochs=30, batch_size=32, validation_data=(x_val, y_val))
model.save_weights('imdb_embedding_weights.h5')
