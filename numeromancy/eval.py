import random
from collections import Counter

from numeromancy.deck_generator import PRIMARY_COLORS, generate_deck, create_deck, is_nonland, is_in_color, card_group, effective_cmc
from numeromancy.parse_decklist import parse_decklist
import numeromancy.card as card
import numeromancy.data as data


def evaluate(decklist: Counter[str], format, date_or_code, n=10):
    """
    Evaluate the deck generation model by removing random cards and checking if they are suggested back.

    Parameters:
    deck_counter (Counter[str]): A counter object containing MTG card names and their counts in the deck
    n (int): Number of evaluation iterations

    Returns:
    float: Average accuracy of the model in recovering removed cards
    """
    # Get Card objects from counter
    deck_cards = []
    for name, count in decklist.items():
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
        name: count for name, count in decklist.items()
        if is_nonland(card.get_card(name))
    })

    # Calculate colors
    colors = [c for c in PRIMARY_COLORS if any(is_in_color(card, c) for card in nonland_cards)]

    # 4. For n number of times
    accuracies = []
    for _ in range(n):
        # 4.1. Create a new counter object that removed three random card names from the deck
        if len(nonland_deck_counter) < 3:
            continue  # Skip if not enough cards to remove

        new_counter = nonland_deck_counter.copy()
        removed_names = random.sample(list(nonland_deck_counter.keys()), 3)
        print(f"Removed: {removed_names}")
        for name in removed_names:
            del new_counter[name]
        removed_counter = Counter({ name: count for name, count in nonland_deck_counter.items() if name in removed_names })

        # Convert new counter to list of Card objects for starting_cards
        starting_cards = list(card.get_card(c) for c in new_counter.elements())

        # 4.2. Call generate_deck using this new counter
        generated_deck = create_deck(starting_cards, format, date_or_code, colors, mana_curve, card_types)

        # 4.3. Compare the newly added cards with the cards cut in 4.1
        added_cards = generated_deck[len(starting_cards):]
        added_counter = Counter(added_cards)

        # 4.4. Accuracy = The number of cards that match the removed cards / The number of cut cards
        matches = sum(count for count in (removed_counter & added_counter).values())
        accuracy = matches / len(added_cards)
        accuracies.append(accuracy)

    # 5. Return average accuracy
    return sum(accuracies) / len(accuracies) if accuracies else 0.0


def evaluate_deck(decklist_file: str, format, date_or_code):
    """
    Evaluate a deck by parsing its decklist file and calling evaluate on the resulting counter.

    Args:
        decklist_file (str): Path to the decklist file

    Returns:
        float: Average accuracy of the model in recovering removed cards
    """
    # Read the decklist file
    with open(decklist_file, 'r') as f:
        decklist_content = f.read()

    # Parse the decklist with a limit of 60
    deck_counter = parse_decklist(decklist_content, limit=60)

    # Load cards and get legal cards
    card.load_cards(data.load(no_download=True))

    # Call evaluate on the resulting counter
    return evaluate(deck_counter, format, date_or_code)


if __name__ == '__main__':
    # Load cards if not loaded
    # card.load_cards(data.load(no_download=True))
    acc = evaluate_deck(
        '../data/decklists/standard/WAR/Boros Feather/TOP8_MCQ Barcelona @ Mana Base (Malaysia) #1 Boros Feather - Justin Chin.dek',
        'standard',
        'WAR',
    )
    print(acc)
