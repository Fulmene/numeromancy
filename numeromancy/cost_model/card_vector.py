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

""" card_vector - Constructing the vector representation of a card """

from collections.abc import Iterable
import os
import csv
import numpy as np

from card import Card, CardProgressBar, get_cards
from preprocessing import read_prop
from embedding import load_embedding


PROPS = [ "layout", "colors", "supertypes", "cardtypes", "subtypes", "power", "toughness", "loyalty", "defense" ]
def card_properties_vectors(cards: Iterable[Card], props: list[str] = PROPS) -> dict[str, np.ndarray]:
    prop_dicts = { p: read_prop(cards, p) for p in props }
    return { c.name: np.concatenate([prop_dicts[p][c.name] for p in props]) for c in cards }


def load_card_vector(filename='card_texts.csv'):
    """ Loads vector representation of cards from a file containing the cards' names and their rules text """
    cards = get_cards()
    with open(filename, 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        for row in reader:
            cardname = row[0]
            rulestext = row[1]
