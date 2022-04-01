from antlr4.error.Errors import ParseCancellationException

import logging
_logger = logging.getLogger(__name__)

from parsing import parse
from card import Card, CardProgressBar

def is_parseable(rule: str, text: str) -> bool:
    try:
        parse(rule, text)
    except ParseCancellationException:
        return False
    return True


def is_parseable_card(card: Card) -> bool:
    if not hasattr(card, "parseable"):
        card.parseable = is_parseable('cardManaCost', card.mana_cost.lower()) and \
                         is_parseable('typeline', card.types) and \
                         is_parseable('rulesText', card.rules_text)
    return card.parseable


def parseable_ratio(cards: list[Card]) -> float:
    # Return 1 if the list is empty to avoid dividing by zero
    if len(cards) == 0:
        return 1

    parseable = 0
    unparseable = 0
    for c in CardProgressBar(cards):
        if is_parseable_card(c):
            parseable += 1
        else:
            unparseable += 1
            if unparseable < 10:
                _logger.info(f"Unparseable card: {c.name}")
                _logger.debug(c.rules_text)

    return parseable / len(cards)


def percentage_bar(num: float, bar_length: int = 20) -> str:
    return f"[{''.join('#' if x / bar_length < num else ' ' for x in range(bar_length))}]"
