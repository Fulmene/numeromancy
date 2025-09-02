from collections import Counter
import re

def parse_decklist(decklist):
    """
    Parses a Magic: The Gathering deck list into a Counter object.

    Args:
        decklist (str): A string containing the deck list (one card per line).

    Returns:
        Counter: A Counter object mapping card names to their counts.
    """
    card_counter = Counter()

    for line in decklist.split('\n'):
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        # Match lines like "2 Snapcaster Mage" or "1x Mountain"
        match = re.match(r'(\d+)(?:\s*x\s*)?(.+)', line)
        if match:
            quantity = int(match.group(1))
            card_name = match.group(2).strip()
            card_counter[card_name] += quantity

    return card_counter


if __name__ == '__main__':
    # Example Usage
    decklist = """
    4 Lightning Bolt
    2 Snapcaster Mage
    1 Mountain
    3 x Delver of Secrets
    2x Tarmogoyf
    """

    deck = parse_decklist(decklist)
    print(deck)
