# This file is part of Numeromancy.
# 
# Numeromancy: an automated Magic: The Gathering deck building system
# Copyright (C) 2022 Ada Joule
# 
# Numeromancy is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
# 
# Numeromancy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Numeromancy.  If not, see <http://www.gnu.org/licenses/>.

""" text_vector - Text model for card texts"""

import os

import numpy as np
from gensim.models.keyedvectors import KeyedVectors
import keras
from keras.layers import Embedding, Dense, Flatten, LSTM
from keras_self_attention import SeqSelfAttention
from keras.utils import to_categorical
from gensim.models import Word2Vec
from transformers import TFRobertaModel, RobertaConfig

from embedding import load_embedding
from preprocessing import TRAIN_TEXTS, TEST_TEXTS, read_text, read_prop
import card, data


MODEL = os.path.join(data.DATADIR, 'text_vector.keras')


# https://github.com/RaRe-Technologies/gensim/wiki/Using-Gensim-Embeddings-with-Keras-and-Tensorflow
def gensim_to_keras_embedding(keyed_vectors: KeyedVectors, train_embeddings=False) -> Embedding:
    """Get a Keras 'Embedding' layer with weights set from Word2Vec model's learned word embeddings.

    Parameters
    ----------
    train_embeddings : bool
        If False, the returned weights are frozen and stopped from being updated.
        If True, the weights can / will be further updated in Keras.

    Returns
    -------
    `keras.layers.Embedding`
        Embedding layer, to be used as input to deeper network layers.

    """
    # keyed_vectors = model.wv  # structure holding the result of training
    weights = keyed_vectors.vectors  # vectors themselves, a 2D numpy array    
    print(weights)
    # index_to_key = keyed_vectors.index_to_key  # which row in `weights` corresponds to which word?

    layer = Embedding(
        input_dim=weights.shape[0],
        output_dim=weights.shape[1],
        weights=[weights],
        trainable=train_embeddings,
    )
    return layer


def text_to_index(text: str, key_to_index: dict[str, int]) -> np.ndarray:
    split_text = text.split()
    return np.array([key_to_index[split_text[i]] if i < len(split_text) and split_text[i] in key_to_index else 0 for i in range(50)])


def lstm_layer():
    embedding = load_embedding()
    return lstm = LSTM(50, return_sequences=False)(gensim_to_keras_embedding(embedding))


def roberta_layer():
    model = TFRobertaModel.from_pretrained("FacebookAI/roberta-base")
    return model


def train_text_model() -> None:
    card.load_cards(data.load(no_download=True))
    cards = card.get_cards()

    embedding = load_embedding()
    input = keras.Input(shape=(50,))
    lstm_layer = LSTM(50, return_sequences=False)(
        gensim_to_keras_embedding(embedding, train_embeddings=False)(input))
    model = keras.Model(inputs=input, outputs=lstm_layer, name="text_vector")
    model.summary()

    classifier = Dense(8)(lstm_layer)
    classifier_model = keras.Model(inputs=input, outputs=classifier, name="text_classifier")
    classifier_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
    classifier_model.summary()

    key_to_index = { v: i for (i, v) in enumerate(embedding.index_to_key) }
    train_texts = read_text(TRAIN_TEXTS, make_dict=False)
    test_texts = read_text(TEST_TEXTS, make_dict=False)
    cmc = read_prop(cards, 'cmc')

    train_x, train_y = np.array([text_to_index(text, key_to_index) for (_, text) in train_texts]), to_categorical([min(cmc[name][0], 7) for (name, _) in train_texts], num_classes=8)

    print(train_x[:10])
    print(train_y[:10])

    classifier_model.fit(train_x, train_y)

    model.save(MODEL)
