import math
from itertools import zip_longest
from collections import Counter

import torch
from torch.utils.data import DataLoader, Dataset
from progressbar import progressbar

import card, data, util
import cost_model
import synergy_model
from preprocessing import CARD_TEXTS, props_vector, read_text
from card_embedding import EmbeddedCardDataset
from deck_data import SynergyDataset


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


COST_EFF_MATRIX: dict[str, float] = {}
SYNERGY_MODEL = (0,0)
EMBEDDINGS = {}
def init_cost_effectiveness_matrix(legal_cards):
    global COST_EFF_MATRIX
    global EMBEDDINGS
    EMBEDDINGS = cost_model.load_card_embedding()
    legal_card_names = [c.name for c in legal_cards]
    _, clf = cost_model.load_model()
    cv = props_vector(legal_cards, props=['cmc'])
    dataset = [(EMBEDDINGS[name], min(int(cv[name].item()), 7)) for name in legal_card_names]
    dataset = util.transpose(dataset)
    data_loader = DataLoader(
        EmbeddedCardDataset(dataset[0], dataset[1]),
        batch_size=128)
    y = dataset[1]
    y_preds = []
    with torch.no_grad():
        for emb, _ in progressbar(data_loader):
            y_pred = clf(emb.to(device))
            #y_pred = torch.argmax(logits, dim=1)
            y_preds.extend(y_pred.tolist())
    COST_EFF_MATRIX = {name: sigmoid((yp[0]+1)/(yr+1) - 1) for name, yr, yp in zip(legal_card_names, y, y_preds)}


def init_synergy_model():
    global SYNERGY_MODEL
    SYNERGY_MODEL = synergy_model.load_model()


def compute_synergy_matrix(deck, legal_cards):
    global SYNERGY_MODEL
    global EMBEDDINGS
    matrix = {}
    clf = SYNERGY_MODEL[1]
    for c1 in progressbar(legal_cards):
        dataset = [(EMBEDDINGS[c1.name], EMBEDDINGS[c2.name], (c1.name, c2.name)) for c2 in deck]
        dataset = util.transpose(dataset)
        data_loader = DataLoader(SynergyDataset(dataset[0], dataset[1], dataset[2]), batch_size=128)
        sum_score = 0.0
        with torch.no_grad():
            for emb1, emb2, pair in data_loader:
                logits = clf(torch.cat((emb1, emb2), dim=1).to(device))
                sum_score += sum(logits)
        matrix[c1.name] = sum_score/len(deck)
    return matrix


def sse(a, b): # sum of square error
    return sum((z[0] - z[1])**2 for z in zip_longest(a, b, fillvalue=0))


def effective_cmc(card):
    layout = card.layout
    faces = card.card_faces
    if layout in ['split', 'modal_dfc', 'adventure']:
        return min(faces[0].cmc, faces[1].cmc)
    else:
        return faces[0].cmc


def compute_mana_curve_matrix(deck, legal_cards, mana_curve):
    mana_limit = len(mana_curve)
    deck_mana_curve = [[effective_cmc(c) for c in deck].count(i) for i in range(mana_limit)]
    initial_sse = sse(mana_curve, deck_mana_curve)
    new_curve_score = [
        # From the old curve's SSE,
        # the new curve SSE can be calculated by subtracting
        # the square of (mana_curve[i] - deck_mana_curve[i])
        # then add the square of (mana_curve[i] - (deck_mana_curve[i] + 1))
        # To simplify that further:
        #   let a = mana_curve[i] - deck_mana_curve[i]
        #   mana_curve[i] - (deck_mana_curve[i] + 1) = mana_curve[i] - deck_mana_curve[i] - 1
        #                                            = a - 1
        #   -a**2 +(a-1)**2  = -a**2 + a**2 - 2a + 1
        #                    = 1 - 2a
        # From proposal:
        #   mana curve score = 1/(1 + euclidean distance)
        # Reminder: Euclidean distance = sqrt(sum of square error)
        # 2025/07/29 - Planning to change euclidean distance to just sse
        #            - and add a denominator to stretch the x-axis
        1/(1 + (initial_sse + (1 - 2*(mana_curve[i] - deck_mana_curve[i])))/256)
        for i in range(mana_limit)
    ]
    legal_card_score = {c.name: new_curve_score[min(effective_cmc(c), mana_limit-1)] for c in legal_cards}
    return legal_card_score


def card_group(card):
    # 0 = creature
    # 1 = noncreature
    # 2 = land
    layout = card.layout
    faces = card.card_faces
    if layout in ['split', 'modal_dfc', 'adventure']:
        if "Creature" in faces[0].cardtypes or "Creature" in faces[1].cardtypes:
            return 0
        elif "Land" in faces[0].cardtypes and "Land" in faces[1].cardtypes:
            # Yes, "and", we only returns land if both faces are lands
            return 2
        else:
            return 1
    else:
        if "Creature" in faces[0].cardtypes:
            return 0
        elif "Land" in faces[0].cardtypes:
            return 2
        else:
            return 1


def compute_strategy_matrix(deck, legal_cards, card_types):
    types_n = len(card_types) - 1
    deck_card_types = [[card_group(c) for c in deck].count(i) for i in range(types_n)]
    initial_sse = sse(card_types, deck_card_types)
    new_curve_score = [
        # same as mana curve
        1/(1 + (initial_sse + (1 - 2*(card_types[i] - deck_card_types[i])))/256)
        for i in range(types_n)
    ]
    legal_card_score = {c.name: new_curve_score[card_group(c)] for c in legal_cards}
    return legal_card_score


UNLIMITED = ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"]
def get_max_scoring_card(deck, legal_cards, mana_curve, card_types, weights):
    global COST_EFF_MATRIX
    legal_cards = {c for c in legal_cards if c.name in UNLIMITED or deck.count(c) < 4}
    synergy_matrix = compute_synergy_matrix(deck, legal_cards)
    mana_curve_matrix = compute_mana_curve_matrix(deck, legal_cards, mana_curve)
    strategy_matrix = compute_strategy_matrix(deck, legal_cards, card_types)
    scores = {c.name: (
        weights[0] * COST_EFF_MATRIX[c.name],
        weights[1] * synergy_matrix[c.name].item(),
        weights[2] * mana_curve_matrix[c.name],
        weights[3] * strategy_matrix[c.name]
        ) for c in legal_cards
    }.items()
    print(f"Card {len(deck) + 1} Top 5:")
    print(*[p for p in sorted(scores, key=lambda x: sum(x[1]), reverse=True)][:5], sep='\n')
    max_score_card = max(scores, key=lambda x: sum(x[1]))[0]
    return max_score_card


def generate_deck(starting_cards, legal_cards, mana_curve, card_types, weights=(1.0, 1.0, 1.0, 1.0)):
    """ Generate a deck of cards given the parameters

    Parameters:
    starting_cards (list[Card]): A list of the Card objects of the cards the deck starts with
    legal_cards (set[Card]): The set of cards legal to use in the deck
    mana_curve (list[int]): The desired mana curve of the deck, starting from 0-cost
        The size of this list determines the maximum mana cost considered effective in a deck
        Best if the last number in the list is 0
    card_types (tuple[int, int, int]): The desired number of each card type, in order: creature, noncreature, land
        The sum of this tuple is the desired deck size. In typical constructed formats, this number should be 60.

    Returns:
    list[Card]: A list of the Card objects of the card in the final deck
    """
    deck_size = card_types[0] + card_types[1]
    deck = starting_cards
    # cost effectiveness score should be computed outside of the loop
    # since it stays the same throughout the entire process
    init_cost_effectiveness_matrix(legal_cards)
    init_synergy_model()
    while (len(deck) < deck_size):
        c = get_max_scoring_card(deck, legal_cards, mana_curve, card_types, weights)
        deck.append(card.get_card(c))
    return deck


def is_nonland(c: card.Card) -> bool:
    front = "Land" not in c.card_faces[0].cardtypes
    back = False
    if not front and c.layout in ['split', 'modal_dfc', 'adventure']:
        back = "Land" not in c.card_faces[1].cardtypes
    return front or back


def is_in_color(c: card.Card, colors: list[str]) -> bool:
    # TODO handle hybrid mana
    front = set(c.card_faces[0].colors).issubset(colors)
    back = False
    if not front and c.layout in ['split', 'modal_dfc', 'adventure']:
        back = set(c.card_faces[1].colors).issubset(colors)
    return front or back


if __name__ == '__main__':
    card.load_cards(data.load(no_download=True))

    monored = (
        4 * [card.get_card("Emberheart Challenger")],
        ["R"],
        [0, 16, 16, 8, 4, 0],
        [30, 10, 20],
        (0.0, 1.0, 1.0, 1.0),
    )

    vivi = (
        4 * [card.get_card("Vivi Ornitier")],
        ["U", "R"],
        [0, 20, 12, 5, 1, 0],
        [5, 33, 22],
        (1.0, 1.0, 1.0, 1.0),
    )
    
    starting_cards, colors, mana_curve, card_types, weights = monored
    legal_cards = {c for c in card.get_cards() if c.legalities["standard"] == "legal" and is_nonland(c) and is_in_color(c, colors)}

    print("Decklist:")
    for c, n in Counter(c.name for c in generate_deck(starting_cards, legal_cards, mana_curve, card_types, weights)).items():
        print(n, c)
    print(f"{card_types[2]} Lands")
