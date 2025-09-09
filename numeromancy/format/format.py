from typing import Collection
from datetime import datetime

from numeromancy.card import Card, get_set
from .sets import date_and_code, get_pioneer_sets, get_modern_sets
from .standard import find_standard_sets, get_standard_banlist
from .banlist import get_banlist

""" A Magic: the Gathering format is a set of cards legal in the format. """

# Set of cards that can be run any number of copies in a deck
UNLIMITED = set([
    "Plains",
    "Island",
    "Swamp",
    "Mountain",
    "Forest",
    "Wastes",
    "Snow-Covered Plains",
    "Snow-Covered Island",
    "Snow-Covered Swamp",
    "Snow-Covered Mountain",
    "Snow-Covered Forest",
    "Snow-Covered Wastes",
])


def _get_legal_cards(legal_sets: Collection[str], banlist: Collection[str]) -> set[Card]:
    """
    Create a format by filtering cards based on legal sets and banned cards.

    Args:
        all_cards: Collection of all available cards
        legal_sets: Collection of set codes that are legal in this format
        banned_cards: Collection of card names that are banned in this format

    Returns:
        Set of cards that are legal in this format
    """
    return {c for s in legal_sets for c in get_set(s) if c.name not in banlist}


def get_legal_cards(format: str, date_or_code: str|datetime) -> set[Card]:
    date, code = date_and_code(date_or_code)
    format = format.lower()
    if format == 'standard':
        sets = find_standard_sets(date_or_code)
        banlist = get_standard_banlist(date)
    elif format == 'pioneer':
        sets = get_pioneer_sets(date_or_code)
        banlist = get_banlist("pioneer", date)
    elif format == 'modern':
        sets = get_modern_sets(date_or_code)
        banlist = get_banlist("modern", date)
    return _get_legal_cards(sets, banlist)
