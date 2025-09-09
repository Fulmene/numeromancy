# This file is part of Demystify.
#
# Demystify: a Magic: The Gathering parser
# Copyright (C) 2022 Ada Joule
#
# Demystify is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
#
# Demystify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Demystify.  If not, see <http://www.gnu.org/licenses/>.

""" card.data -- Card data for the package """

import logging
_logger = logging.getLogger(__name__)

from .card import Card, CardProgressBar
from .preprocessing import preprocess_all
from .names import add_name, clear_names


_all_cards: dict[str, Card] = {}
_cards_by_sets: dict[str, set[str]] = {}

def is_loadable(scryfall_card):
    return scryfall_card["legalities"]["vintage"] in ("legal", "restricted") and \
        scryfall_card["layout"] not in ("reversible_card")

def load_cards(scryfall_cards):
    """ Loads the cards' informations from scryfall into the module. """
    _all_cards.clear()
    _cards_by_sets.clear()

    _logger.info("Loading cards from scryfall data...")
    clear_names()
    for sc in CardProgressBar(scryfall_cards):
        if is_loadable(sc):
            name = sc["name"]
            card_set = sc["set"].upper()
            if name not in _all_cards:
                card = Card(sc)
                _all_cards[name] = card
                add_name(name)
            else:
                _all_cards[name].sets.add(card_set)

            if card_set not in _cards_by_sets:
                _cards_by_sets[card_set] = {name}
            else:
                _cards_by_sets[card_set].add(name)

    _logger.info("Preprocessing card texts...")
    for card in CardProgressBar(_all_cards.values()):
        preprocess_all(card)


def get_cards(format="vintage") -> set[Card]:
    """ Returns a set of all the Cards loaded by the function load_cards. """
    return set(c for c in _all_cards.values() if c.legalities[format] in ("legal", "restricted"))


def find_name(cardname: str) -> str:
    """ Find the closest card name. Useful for i.e. referring to only one half of a DFC.
        Error if multiple matched unless it is an exact match. """
    names = [name for name in _all_cards if cardname in name]
    if len(names) == 1:
        return names[0]
    elif len(names) > 1:
        names = [name for name in names if _all_cards[name].card_faces[0].name == cardname]
        if len(names) == 1:
            return names[0]
        else:
            raise KeyError(f"{cardname} matches multiple card names.")
    else:
        raise KeyError(f"{cardname} doesn't match any known card names.")


def get_card(cardname: str) -> Card:
    """ Returns a specific card by name. Raises KeyError if no such card exists. """
    return _all_cards[cardname]


def get_set(setcode: str) -> set[Card]:
    """ Returns a set of all the Cards in the given set. """
    setcode = setcode.upper()
    if setcode not in _cards_by_sets:
        return set()
    return {get_card(cardname) for cardname in _cards_by_sets[setcode]}
