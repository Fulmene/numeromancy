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

import os
import csv
import numpy as np
import xgboost as xgb

import card
from preprocessing import prop_read

def card_properties_vector(properties: list[str]):
    card_dict = dict()
    for prop in properties:
        prop_dict = prop_read(prop)
        for cardname, vector in prop_dict.items():
            card_dict[cardname] = np.append(card_dict[cardname], vector)
    return card_dict


def load_card_vector(filename='card_texts.csv'):
    """ Loads vector representation of cards from a file containing the cards' names and their rules text """
    with open(filename, 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        for row in reader:
            cardname = row[0]
            rulestext = row[1]
