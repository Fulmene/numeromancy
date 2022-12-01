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

""" preprocessing - Card data preprocessing """

import re
import csv
import random
from collections.abc import Iterable

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

# from gensim.models import Word2Vec
import networkx as nx
import nbne

from card import Card, CardProgressBar
import card, data


stemmer = PorterStemmer()
stops = stopwords.words('english')


def replace_word(word: str) -> str:
    if len(word) == 1 or word.isupper():  # Single letters are usually important in Magic
        return word
    elif word in stops:
        return 'W'
    else:
        return stemmer.stem(word)


def remove_bracket_spaces(text: str) -> str:
    return re.sub(r'\{\s+([A-Za-z0-9])\s+\}', r'{\1}', text)


def preprocess_text(cards: Iterable[Card], filename='card_texts.csv') -> None:
    with open(filename, 'w', encoding='UTF8') as f:
        writer = csv.writer(f);
        for c in cards:
            texts = []
            if c.rules_text:
                for line in c.rules_text.split('\n'):
                    text = []
                    for s in sent_tokenize(line):
                        words = map(replace_word, word_tokenize(s))
                        text.append(remove_bracket_spaces(' '.join(words)))
                    texts.append(' '.join(text))
            writer.writerow((c.name, ' '.join(texts)))


def write_augmented(filename, rows, ratio=0.3):
    with open(filename, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        augment_index = len(rows) * ratio
        for i, row in enumerate(rows):
            writer.writerow(row)
            if i < augment_index:
                split_text = row[1].split()
                writer.writerow((row[0], ' '.join(random.sample(split_text, len(split_text)))))


def split_train(card_texts_file='card_texts.csv', train_file='train.csv', test_file='test.csv') -> None:
    with open(card_texts_file, 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        cards = [row[0] for row in reader]
        random.shuffle(cards)
        div = int(len(cards) * 0.7)
        write_augmented(train_file, cards[:div])
        write_augmented(test_file, cards[div:])


def property_graph(cards: Iterable[Card], property: str) -> nx.Graph:
    graph = nx.Graph()
    for c in CardProgressBar(cards):
        key = c.name
        prop = getattr(c, property)
        graph.add_node(key, prop=prop)
        for n in graph.nodes:
            if key != n and prop == graph.nodes[n]['prop']:
                graph.add_edge(key, n)
    return graph


nbne_props = ['cmc', 'power', 'toughness']  # TODO other props Properties to be compressed with NBNE

def preprocess_props(cards: Iterable[Card]) -> None:
    for p in nbne_props:
        graph = property_graph(cards, p)
        nbne.train_model(graph, 10, output_file=f'nbne/{p}.model', embedding_dimension=10)
