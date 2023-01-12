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

import logging
_logger = logging.getLogger(__name__)

import os
import re
import csv
import random
from collections.abc import Collection, Iterable
import sys
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


TEXTSDIR = os.path.join(data.DATADIR, 'text')
CARD_TEXTS = os.path.join(TEXTSDIR, 'card_texts.csv')
TRAIN_TEXTS = os.path.join(TEXTSDIR, 'train_texts.csv')
TEST_TEXTS = os.path.join(TEXTSDIR, 'test_texts.csv')

PROPSDIR = os.path.join(data.DATADIR, 'props')


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
    _logger.info("Preprocessing card texts...")
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
    _logger.info("Splitting card texts into train and test datasets")
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
            if key != n and not set(prop).isdisjoint(graph.nodes[n]['prop']):
                graph.add_edge(key, n)
    return graph


numerical_props = ['power', 'toughness', 'loyalty']
list_props = ['supertypes', 'types', 'subtypes', 'colors']
NBNE_DIMENSIONS = 10


def preprocess_numerical_prop(cards: Collection[Card], prop: str, props_dir: str | os.PathLike) -> None:
    _logger.info(f'Preprocessing the numerical property {prop}...')
    with open(os.path.join(props_dir, f'{prop}.vec'), 'w') as f:
        print(len(cards), 1, file=f)
        for c in CardProgressBar(cards):
            print(c.name, getattr(c, prop), file=f)


def preprocess_nbne_prop(cards: Iterable[Card], prop: str, props_dir: str | os.PathLike = PROPSDIR) -> None:
    _logger.info(f'Creating the property graph for property {prop}...')
    graph = property_graph(cards, prop)
    _logger.info('Training the NBNE model...')
    nbne.train_model(graph, NBNE_DIMENSIONS, output_file=os.path.join(props_dir, f'{prop}.model'), embedding_dimension=NBNE_DIMENSIONS)
    _logger.info('Complete!')


def preprocess_list_prop(cards: Collection[Card], prop: str, props_dir: str | os.PathLike) -> None:
    _logger.info(f'Preprocessing the list property {prop}...')
    values = set()
    _logger.info(f'Finding all possible values from the given list of cards...')
    for c in CardProgressBar(cards):
        values.update(getattr(c, prop))

    dimensions = len(values)
    if dimensions > NBNE_DIMENSIONS:
        _logger.info(f'Property {prop} has more than {NBNE_DIMENSIONS} possible values.')
        preprocess_nbne_prop(cards, prop, props_dir)
    else:
        _logger.info(f'Property {prop} has {dimensions} possible values.')
        values = list(values)
        with open(os.path.join(props_dir, f'{prop}.vec'), 'w') as f:
            print(len(cards), dimensions, file=f)
            _logger.info(f'Creating sparse vectors for property {prop}...')
            for c in CardProgressBar(cards):
                property = getattr(c, prop)
                vector = [1 if v in property else 0 for v in values]
                print(c.name, *vector, file=f)


def preprocess_props(cards: Collection[Card], props_dir: str | os.PathLike =PROPSDIR) -> None:
    for prop in numerical_props:
        preprocess_numerical_prop(cards, prop, props_dir)
    for prop in list_props:
        preprocess_list_prop(cards, prop, props_dir)


def prop_read(prop: str, props_dir: str | os.PathLike = PROPSDIR) -> dict[str, np.ndarray]:
    with open(os.path.join(props_dir, prop), 'r') as f:
        header = f.readline().split()
        nodes, dims = int(header[0]), int(header[1])
        nbne_dict = dict()
        for _ in range(nodes):
            line = f.readline().split()
            cardname = ' '.join(line[:-dims])
            vector = np.asfarray(line[-dims:])
            nbne_dict[cardname] = vector
    return nbne_dict


if __name__ == '__main__':
    card.load_cards(data.load())
    cards = card.get_cards()
    os.makedirs(TEXTSDIR)
    preprocess_text(cards)
    split_train_texts()
    os.makedirs(PROPSDIR)
    preprocess_props(cards)
