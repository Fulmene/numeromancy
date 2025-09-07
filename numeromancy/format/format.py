from typing import Collection

from numeromancy.card import Card

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

def get_legal_cards(all_cards: Collection[Card], legal_sets: Collection[str], banlist: Collection[str]) -> set[Card]:
    """
    Create a format by filtering cards based on legal sets and banned cards.

    Args:
        all_cards: Collection of all available cards
        legal_sets: Collection of set codes that are legal in this format
        banned_cards: Collection of card names that are banned in this format

    Returns:
        Set of cards that are legal in this format
    """
    legal_cards = set()
    for card in all_cards:
        # Check if card is from at least one legal set and not banned
        if card.sets.intersection(legal_sets) and card.name not in banlist:
            legal_cards.add(card)

    return legal_cards
