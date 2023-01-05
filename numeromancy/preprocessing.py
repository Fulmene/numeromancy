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

import os
import re
import csv
import random
from collections.abc import Iterable
import numpy as np

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


CARD_TEXTS = os.path.join(data.DATADIR, 'card_texts.csv')
TRAIN_TEXTS = os.path.join(data.DATADIR, 'train_texts.csv')
TEST_TEXTS = os.path.join(data.DATADIR, 'test_texts.csv')


def replace_word(word: str) -> str:
    if len(word) == 1 or word.isupper():  # Single letters are usually important in Magic
        return word
    elif word in stops:
        return 'W'
    else:
        return stemmer.stem(word)


def remove_bracket_spaces(text: str) -> str:
    return re.sub(r'\{\s+([A-Za-z0-9])\s+\}', r'{\1}', text)


def preprocess_text(cards: Iterable[Card], filename=CARD_TEXTS) -> None:
    with open(filename, 'w', encoding='UTF8') as f:
        writer = csv.writer(f);
        for c in CardProgressBar(cards):
            texts = []
            if c.rules_text:
                for line in c.rules_text.split('\n'):
                    text = []
                    for s in sent_tokenize(line):
                        words = map(replace_word, word_tokenize(s))
                        text.append(remove_bracket_spaces(' '.join(words)))
                    texts.append(' '.join(text))
            writer.writerow((c.name, '\n'.join(texts)))


def write_augmented(filename: str, rows: list[list[str]], ratio: float = 0.3):
    augment_index = len(rows) * ratio
    new_rows = []
    for i, row in enumerate(rows):
        new_rows.append(row)
        if i < augment_index:
            split_text = row[1].split()
            split_text.extend((len(row[1].split('\n')) - 1) * ['\n'])
            new_text = '\n'.join(line.strip() for line in ' '.join(random.sample(split_text, len(split_text))).split('\n'))
            new_rows.append([row[0], new_text])
    random.shuffle(new_rows)
    with open(filename, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)


def split_train_texts(card_texts_file=CARD_TEXTS, train_file=TRAIN_TEXTS, test_file=TEST_TEXTS) -> None:
    with open(card_texts_file, 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        cards = [row for row in reader]
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
            # TODO support list property
            if key != n and prop == graph.nodes[n]['prop']:
                graph.add_edge(key, n)
    return graph


NBNE_DIMENSIONS = 10
nbne_props = ['subtypes']  # nbne_props are list_props that has more than NBNE_DIMENSIONS possible values
number_props = ['power', 'toughness']
list_props = ['types', 'supertypes', 'colors']

def preprocess_nbne_props(cards: Iterable[Card]) -> None:
    for p in nbne_props:
        graph = property_graph(cards, p)
        nbne.train_model(graph, NBNE_DIMENSIONS, output_file=f'nbne/{p}.model', embedding_dimension=NBNE_DIMENSIONS)


def nbne_read(filename):  # -> dict[str, np.array]:
    with open(filename, 'r') as f:
        header = f.readline().split()
        nodes, dims = int(header[0]), int(header[1])
        nbne_dict = dict()
        for _ in range(nodes):
            line = f.readline().split()
            cardname = ' '.join(line[:-dims])
            vector = np.asfarray(line[-dims:])
            nbne_dict[cardname] = vector
    return nbne_dict


def create_number_props(cards: Iterable[Card], prop):
    prop_dict = dict()
    for c in cards:
        prop_dict[c.name] = np.asarray(getattr(c, prop))
    return prop_dict


COLORS = ['w', 'u', 'b', 'r', 'g']

def create_color_dict(cards: Iterable[Card]):
    


def prop_read(prop: str):  # -> dict[str, np.array]:
    if prop in nbne_props:
        return nbne_read(f'nbne/{prop}.model')
    elif prop in number_props:
        return create_number_props(props)
    elif prop in list_props:
        pass


if __name__ == '__main__':
    card.load_cards(data.load())
    cards = card.get_cards()
    preprocess_text(cards)
    split_train_texts()
