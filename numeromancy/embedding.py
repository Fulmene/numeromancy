import io

import tensorflow as tf

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

from sklearn.manifold import TSNE

from gensim.models import Word2Vec

import data
import card

card.load_cards(data.load())
cards = card.get_cards()

lemmatizer = WordNetLemmatizer()
stops = stopwords.words('english')

sentences = []
for c in cards:
    if c.rules_text:
        for line in c.rules_text.split('\n'):
            sents = sent_tokenize(line)
            for s in sents:
                words = [lemmatizer.lemmatize(w) if w not in stops else 'W' for w in word_tokenize(s)]
                sentences.append(words)

model = Word2Vec(sentences=sentences)
model.save('mtg.model')
