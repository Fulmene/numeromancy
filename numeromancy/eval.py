import random
from collections import Counter

from deck_generator import generate_deck, is_nonland, card_group, effective_cmc
import card
import data


def evaluate(deck_counter, legal_cards, n=10):
    """
    Evaluate the deck generation model by removing random cards and checking if they are suggested back.

    Parameters:
    deck_counter (Counter): A counter object containing MTG card names and their counts in the deck
    n (int): Number of evaluation iterations

    Returns:
    float: Average accuracy of the model in recovering removed cards
    """
    # Get Card objects from counter
    deck_cards = []
    for name, count in deck_counter.items():
        c = card.get_card(name)
        deck_cards.extend([c] * count)

    # 1. Calculate the deck's mana curve, excluding lands
    nonland_cards = [c for c in deck_cards if is_nonland(c)]
    mana_curve = [0] * 8  # Assume max CMC of 7, adjust if needed
    for c in nonland_cards:
        cmc = effective_cmc(c)
        if cmc < len(mana_curve):
            mana_curve[cmc] += 1

    # 2. Calculate the deck's card types (creature, noncreature, land)
    creature_count = sum(1 for c in deck_cards if card_group(c) == 0)
    noncreature_count = sum(1 for c in deck_cards if card_group(c) == 1)
    land_count = sum(1 for c in deck_cards if card_group(c) == 2)
    card_types = (creature_count, noncreature_count, land_count)

    # 3. Remove all lands from the deck
    nonland_deck_counter = Counter({
        name: count for name, count in deck_counter.items()
        if is_nonland(card.get_card(name))
    })

    # 4. For n number of times
    accuracies = []
    for _ in range(n):
        # 4.1. Create a new counter object that removed three random card names from the deck
        if len(nonland_deck_counter) < 3:
            continue  # Skip if not enough cards to remove

        new_counter = nonland_deck_counter.copy()
        removed_names = random.sample(list(nonland_deck_counter.keys()), 3)
        for name in removed_names:
            del new_counter[name]

        # Convert new counter to list of Card objects for starting_cards
        starting_cards = list(new_counter.elements())

        # 4.2. Call generate_deck using this new counter
        generated_deck = generate_deck(starting_cards, legal_cards, mana_curve, card_types)

        # 4.3. Compare the newly added cards with the cards cut in 4.1
        added_cards = generated_deck[len(starting_cards):]
        added_names = [c.name for c in added_cards]

        # 4.4. Accuracy = The number of cards that match the removed cards / The number of cut cards
        # TODO This is still inaccurate. fixing later
        matches = sum(1 for name in removed_names if name in added_names)
        accuracy = matches / 3
        accuracies.append(accuracy)

    # 5. Return average accuracy
    return sum(accuracies) / len(accuracies) if accuracies else 0.0


if __name__ == '__main__':
    # Load cards if not loaded
    card.load_cards(data.load(no_download=True))
