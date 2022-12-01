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

import csv

import card
import preprocessing


def card_properties_vector(cardname: str):
    card_data = card.get_card(cardname)


def card_vector(cardname: str, text: str):
    pass


def load_card_vector(filename='card_texts.csv'):
    """ Loads vector representation of cards from a file containing the cards' names and their rules text """
    with open(filename, 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        for row in reader:
            cardname = row[0]
            rulestext = row[1]
