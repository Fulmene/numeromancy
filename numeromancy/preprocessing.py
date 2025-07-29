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
import sys
logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)
_handler = logging.StreamHandler(sys.stderr)
_handler.setLevel(logging.WARNING)

import os
import re
import csv
import random
from collections.abc import Collection, Iterable
import numpy as np

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

import networkx as nx
import nbne

from card import Card, CardProgressBar
import card, data


stemmer = PorterStemmer()
stops = stopwords.words('english')


TEXTSDIR = os.path.join(data.OUTPUTDIR, 'texts')
CARD_TEXTS = os.path.join(TEXTSDIR, 'card_texts.csv')
TRAIN_TEXTS = os.path.join(TEXTSDIR, 'train_texts.csv')
TEST_TEXTS = os.path.join(TEXTSDIR, 'test_texts.csv')

PROPSDIR = os.path.join(data.OUTPUTDIR, 'props')


def replace_word(word: str) -> str:
    if len(word) == 1 or word.isupper():  # Single letters are usually important in Magic
        return word
    elif word in stops:
        return '_'
    else:
        return stemmer.stem(word)


def remove_bracket_spaces(text: str) -> str:
    return re.sub(r'\{\s+([A-Za-z0-9])\s+\}', r'{\1}', text)


def preprocess_text(cards: Iterable[Card], filename=CARD_TEXTS) -> None:
    _logger.info("Preprocessing card texts...")
    with open(filename, 'w', encoding='UTF8') as f:
        writer = csv.writer(f);
        for card in CardProgressBar(cards):
            all_texts = []
            for face in card.card_faces:
                texts = []
                if face.rules_text:
                    for line in face.rules_text.split('\n'):
                        text = []
                        for s in sent_tokenize(line):
                            words = word_tokenize(s)
                            text.append(remove_bracket_spaces(' '.join(words)))
                        texts.append(' '.join(text))
                all_texts.append('\n'.join(texts))
            if len(all_texts) < 2:
                all_texts.append("")
            writer.writerow((card.name, all_texts[0], all_texts[1]))


def write_augmented(filename: str, rows: list[list[str]], ratio: float = 0.3):
    augment_index = len(rows) * ratio
    new_rows = []
    for i, row in enumerate(rows):
        new_rows.append(row)
        if i < augment_index:
            split_text1 = row[1].split()
            split_text1.extend((len(row[1].split('\n')) - 1) * ['\n'])
            new_text1 = '\n'.join(line.strip() for line in ' '.join(random.sample(split_text1, len(split_text1))).split('\n'))
            split_text2 = row[2].split()
            split_text2.extend((len(row[2].split('\n')) - 1) * ['\n'])
            new_text2 = '\n'.join(line.strip() for line in ' '.join(random.sample(split_text2, len(split_text2))).split('\n'))
            new_rows.append([row[0], new_text1, new_text2])
    random.shuffle(new_rows)
    with open(filename, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)


def split_train_texts(card_texts_file=CARD_TEXTS, train_file=TRAIN_TEXTS, test_file=TEST_TEXTS, ratio=0.7) -> None:
    _logger.info("Splitting card texts into train and test datasets")
    with open(card_texts_file, 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        cards = [row for row in reader]
        random.shuffle(cards)
        div = int(len(cards) * ratio)
        write_augmented(train_file, cards[:div])
        write_augmented(test_file, cards[div:])


def read_text(filename, make_dict=True):
    with open(filename, 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        texts = [ (r[0], r[1]) for r in reader ]
    return dict(texts) if make_dict else texts


layouts = ['choose', 'transform']
numerical_props = ['power', 'toughness', 'loyalty', 'defense', 'cmc']
list_props = ['supertypes', 'cardtypes', 'subtypes', 'colors']
feature_props = [x for x in numerical_props + list_props if x != 'cmc']
NBNE_DIMENSIONS = 10


def face_count(cards: Collection[Card]) -> int:
    return sum(len(c.card_faces) for c in cards)


def to_number(s) -> int:
    if s is None:
        return 0
    elif isinstance(s, str):
        return eval(s.replace('X', '0').replace('*', '0'))
    else:
        return s


def preprocess_numerical_prop(cards: Collection[Card], prop: str, props_dir: str | os.PathLike) -> None:
    _logger.info(f'Preprocessing the numerical property {prop}...')
    with open(os.path.join(props_dir, f'{prop}.model'), 'w') as f:
        print(face_count(cards), 1, file=f)
        for card in CardProgressBar(cards):
            for face in card.card_faces:
                print(face.name, to_number(getattr(face, prop)), file=f)


def preprocess_list_prop(cards: Collection[Card], prop: str, props_dir: str | os.PathLike) -> None:
    _logger.info(f'Preprocessing the list property {prop}...')
    values = set()
    _logger.info(f'Finding all possible values from the given list of cards...')
    for card in cards:
        for face in card.card_faces:
            values.update(getattr(face, prop))

    values = list(values)
    dimensions = len(values)
    _logger.info(f'Property {prop} has {dimensions} possible values.')
    _logger.info(values)

    if dimensions > NBNE_DIMENSIONS:
        _logger.info(f'Creating the property graph for property {prop}...')
        graph = nx.Graph()
        for card in CardProgressBar(cards):
            for face in card.card_faces:
                key = face.name
                property = getattr(face, prop)
                graph.add_node(key)
                for c2 in cards:
                    for f2 in c2.card_faces:
                        key2 = f2.name
                        property2 = getattr(f2, prop)
                        if key != key2 and not set(property).isdisjoint(property2):
                            graph.add_edge(key, key2)
        nbne.train_model(graph, NBNE_DIMENSIONS, output_file=os.path.join(props_dir, f'{prop}.model'), embedding_dimension=NBNE_DIMENSIONS)
    else:
        _logger.info(f'Creating sparse vectors for property {prop}...')
        with open(os.path.join(props_dir, f'{prop}.model'), 'w') as f:
            print(face_count(cards), dimensions, file=f)
            for card in CardProgressBar(cards):
                for face in card.card_faces:
                    property = getattr(face, prop)
                    vector = [1 if v in property else 0 for v in values]
                    print(face.name, *vector, file=f)


def preprocess_props(cards: Collection[Card], props_dir: str | os.PathLike = PROPSDIR) -> None:
    for prop in numerical_props:
        preprocess_numerical_prop(cards, prop, props_dir)
    for prop in list_props:
        preprocess_list_prop(cards, prop, props_dir)


def read_prop(cards: Iterable[Card], prop: str, props_dir: str | os.PathLike = PROPSDIR) -> dict[str, np.ndarray]:
    with open(os.path.join(props_dir, f'{prop}.model'), 'r') as f:
        header = f.readline().split()
        lines, dims = int(header[0]), int(header[1])
        vectors = dict()
        for _ in range(lines):
            line = f.readline().split()
            cardname = ' '.join(line[:-dims])
            vector = np.asfarray(line[-dims:])
            vectors[cardname] = vector
    vectors.update((c.name, np.zeros((dims,))) for c in cards if c.name not in vectors)
    return vectors


def props_vector(cards, props = feature_props):
    prop_dicts = { p: read_prop(cards, p) for p in props }
    return { c.name: np.concatenate([prop_dicts[p][c.name] for p in props]) for c in cards }


def preprocess_layout(cards: Collection[Card], props_dir: str | os.PathLike = PROPSDIR) -> None:
    with open(os.path.join(props_dir, 'layout.model'), 'w') as f:
        print(len(cards), len(layouts), file=f)
        for card in CardProgressBar(cards):
            if card.layout in ['split', 'modal_dfc', 'adventure']:
                vector = [1 if l == 'choose' else 0 for l in layouts]
            elif card.layout in ['transform', 'flip', 'battle']:
                vector = [1 if l == 'transform' else 0 for l in layouts]
            else:
                vector = [1 if l == 'single' else 0 for l in layouts]
            print(card.name, *vector, file=f)


def preprocess_all(cards: Collection[Card]) -> None:
    preprocess_layout(cards)
    preprocess_text(cards)
    split_train_texts()
    preprocess_props(cards)


if __name__ == '__main__':
    card.load_cards(data.load(no_download=True))
    cards = card.get_cards()
    os.makedirs(TEXTSDIR, exist_ok=True)
    os.makedirs(PROPSDIR, exist_ok=True)
    preprocess_all(cards)
