# -*- coding: utf-8 -*-
"""lstm_sentiment_analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rgN-xwtsfA1XMKIjirBC08Dq0e4H9hD1
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import nltk
from nltk.corpus import stopwords
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, LSTM, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import tensorflow_datasets as tfds

# Download NLTK data
# nltk.download("stopwords")
# nltk.download("punkt")

# Load IMDb dataset using TensorFlow Datasets
imdb, info = tfds.load("imdb_reviews", with_info=True, as_supervised=True)
# Split the dataset into training and testing sets
train_data, test_data = imdb['train'], imdb['test']

# Extract reviews and labels from the dataset
train_sentences = []
test_sentences = []
train_labels = []
test_labels = []

for s, l in train_data:
    train_sentences.append(str(s.numpy()))
    train_labels.append(l.numpy())

for s, l in test_data:
    test_sentences.append(str(s.numpy()))
    test_labels.append(l.numpy())

# Convert labels to binary (1 for positive, 0 for negative)
train_labels = np.array(train_labels)
test_labels = np.array(test_labels)

# Data preprocessing
def preprocess_text(text):
    text = re.sub('[^a-zA-Z]', ' ', text)  # Remove non-alphabetic characters
    text = text.lower()  # Convert to lowercase
    text = text.strip()  # Remove leading/trailing white spaces
    return text

train_sentences = [preprocess_text(sentence) for sentence in train_sentences]
test_sentences = [preprocess_text(sentence) for sentence in test_sentences]

# Train-Test Split
x_train, x_test, y_train, y_test = train_test_split(train_sentences, train_labels, test_size=0.2, random_state=42)

# Tokenization and Padding
max_tokens = 567  # Maximum sequence length
tokenizer = Tokenizer(num_words=15000)
tokenizer.fit_on_texts(x_train)
x_train_tokens = tokenizer.texts_to_sequences(x_train)
x_test_tokens = tokenizer.texts_to_sequences(x_test)
x_train_pad = pad_sequences(x_train_tokens, maxlen=max_tokens)
x_test_pad = pad_sequences(x_test_tokens, maxlen=max_tokens)

model = Sequential()
embedding_size = 75
model.add(Embedding(input_dim=15000, output_dim=embedding_size, input_length=max_tokens, name='embedding_layer'))
model.add(LSTM(units=5, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=25, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=12, return_sequences=True))
model.add(Dropout(0.1))
model.add(LSTM(units=5))
model.add(Dropout(0.1))
model.add(Dense(1, activation='sigmoid'))

optimizer = Adam(learning_rate=1e-3)
model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

# Model training
history = model.fit(x_train_pad, y_train, validation_split=0.3, epochs=10, batch_size=750, shuffle=True, verbose=1)

# Model evaluation
result = model.evaluate(x_test_pad, y_test)
print("Test Loss:", result[0])
print("Test Accuracy:", result[1])

new_sentence = "This is a great movie!"
new_sentence = preprocess_text(new_sentence)
new_sentence_tokens = tokenizer.texts_to_sequences([new_sentence])
new_sentence_pad = pad_sequences(new_sentence_tokens, maxlen=max_tokens)
prediction = model.predict(new_sentence_pad)

if prediction > 0.5:
    sentiment = "positive"
else:
    sentiment = "negative"

print("Predicted Sentiment:", sentiment)

plt.figure()
plt.plot(history.history["accuracy"], label="Train")
plt.plot(history.history["val_accuracy"], label="Test")
plt.title("Accuracy")
plt.ylabel("Accuracy")
plt.xlabel("Epochs")
plt.legend()
plt.show()

plt.figure()
plt.plot(history.history["loss"], label="Train")
plt.plot(history.history["val_loss"], label="Test")
plt.title("Loss")
plt.ylabel("Loss")
plt.xlabel("Epochs")
plt.legend()
plt.show()