import math
import os
import random
import csv
from itertools import islice
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

import torch
from torch.utils.data import Dataset
from progressbar import progressbar

import numeromancy.card as card
import numeromancy.data as data
import numeromancy.util as util
from numeromancy.preprocessing import CARD_TEXTS, props_vector
from numeromancy.parse_decklist import parse_decklist
from numeromancy.format import SETS
from numeromancy.deck_generator import is_nonland
from .card_embedding import CardEmbedding
from .cost_model import CARD_EMBEDDING, load_card_embedding

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

SYNERGYDIR = os.path.join(data.OUTPUTDIR, 'synergy')
TRAIN_SYNERGY = os.path.join(SYNERGYDIR, 'train_synergy.csv')
TEST_SYNERGY = os.path.join(SYNERGYDIR, 'test_synergy.csv')


class SynergyDataset(Dataset):
    def __init__(self, emb1, emb2, synergy):
        self.emb1 = emb1
        self.emb2 = emb2
        self.synergy = synergy

    def __len__(self):
        return len(self.synergy)

    def __getitem__(self, idx):
        return self.emb1[idx], self.emb2[idx], self.synergy[idx]


def calculate_npmi(decklists, epsilon=1e-2):
    occur = defaultdict(int)
    co_occur = defaultdict(int)
    for decklist in progressbar(decklists):
        count = len(decklist)
        keys = list(decklist.keys())
        for i in range(count):
            c1 = keys[i]
            if c1 == "Unknown Card":
                continue
            occur[c1] = occur[c1] + 1
            for j in range(i+1, count):
                c2 = keys[j]
                if c2 == "Unknown Card":
                    continue
                try:
                    _card1 = card.get_card(c1)
                except KeyError:
                    c1 = card.find_name(c1)
                try:
                    _card2 = card.get_card(c2)
                except KeyError:
                    c2 = card.find_name(c2)
                key = '|'.join(sorted((c1, c2)))
                co_occur[key] = co_occur[key] + 1

    data = []
    n = len(decklists)
    for k, v in co_occur.items():
        c1, c2 = k.split('|')
        p_c1 = occur[c1] / n
        p_c2 = occur[c2] / n
        p_co_occur = v / n + epsilon
        p_independent = p_c1 * p_c2 + epsilon
        npmi = math.log(p_co_occur / p_independent) / -math.log(p_co_occur)
        data.append((c1, c2, npmi))
    return data


def create_positive_data(decklists):
    # Decklists are Counter objects
    data = []
    for decklist in progressbar(decklists):
        for c1 in decklist:
            if c1 == "Unknown Card":
                continue
            for c2 in decklist:
                if c2 == "Unknown Card":
                    continue
                try:
                    _card1 = card.get_card(c1)
                except KeyError:
                    c1 = card.find_name(c1)
                try:
                    _card2 = card.get_card(c2)
                except KeyError:
                    c2 = card.find_name(c2)
                if c1 != c2:
                    data.append([c1, c2, 1])
    return data


def create_negative_data(decklists, num=1000):
    card_pool = list(set(card.find_name(c) for deck in decklists for c in deck if c != "Unknown Card"))
    # Assume synergy is rare. Generate random pairs from all the cards
    data = []
    for _ in progressbar(range(num)):
        c = random.sample(card_pool, 2)
        data.append([c[0], c[1], 0])
    return data


def write_deck_data(decklists, train_file=TRAIN_SYNERGY, test_file=TEST_SYNERGY, train_rate=0.7):
    # positive_data = create_positive_data(decklists)
    # random.shuffle(positive_data)
    # negative_data = create_negative_data(decklists, num=len(positive_data))
    # # neg data is already randomly generated so no need to shuffle
    # psplit = int(len(positive_data)*train_rate)
    # nsplit = int(len(negative_data)*train_rate)
    #
    # os.makedirs(SYNERGYDIR, exist_ok=True)
    #
    # with open(train_file, 'w') as f:
    #     pd = positive_data[:psplit]
    #     nd = negative_data[:nsplit]
    #     d = pd + nd
    #     writer = csv.writer(f)
    #     writer.writerows(d)
    #
    # with open(test_file, 'w') as f:
    #     pd = positive_data[psplit:]
    #     nd = negative_data[nsplit:]
    #     d = pd + nd
    #     writer = csv.writer(f)
    #     writer.writerows(d)
    pmi_data = calculate_npmi(decklists)
    positive = 0
    positive_printed = 0
    neutral = 0
    negative = 0
    negative_printed = 0
    max = 0.0
    min = 0.0
    for c1, c2, v in pmi_data:
        if v > 0.2:
            positive += 1
            if v > max:
                max = v
            if positive_printed < 10:
                print(f"Positive: {c1} | {c2}")
                positive_printed += 1
        elif v < -0.2:
            negative += 1
            if v < min:
                min = v
            if negative_printed < 10:
                print(f"Negative: {c1} | {c2}")
                negative_printed += 1
        else:
            neutral += 1
    total = positive + neutral + negative
    print(f"Positive: {positive} ({100*positive/total:.2f}%)")
    print(f"Neutral : {neutral} ({100*neutral/total:.2f}%)")
    print(f"Negative: {negative} ({100*negative/total:.2f}%)")
    print(f"Max: {max}")
    print(f"Min: {min}")


def card_encode(cardname, embeddings, cv):
    # This code assumes that the cards are already loaded.
    try:
        c = card.get_card(cardname)
    except KeyError:
        c = card.get_card(card.find_name(cardname))
    emb1 = embeddings[c.card_faces[0].name]
    cmc1 = torch.from_numpy(cv[c.card_faces[0].name]).float()
    emb2 = torch.tensor(64 * [0.0])
    cmc2 = torch.tensor([0.0])
    if c.layout in ["split", "modal_dfc", "adventure"]:
        emb2 = embeddings[c.card_faces[1].name]
        cmc2 = torch.from_numpy(cv[c.card_faces[1].name]).float()
        layout_tensor = torch.tensor([1.0, 0.0])
    elif c.layout in ["transfrom", "flip", "battle"]:
        emb2 = embeddings[c.card_faces[1].name]
        cmc2 = torch.from_numpy(cv[c.card_faces[1].name]).float()
        layout_tensor = torch.tensor([0.0, 1.0])
    else:
        layout_tensor = torch.tensor([0.0, 0.0])
    return emb1, cmc1, emb2, cmc2, layout_tensor


def read_deck_data(filename):
    # This code assumes that the cards are already loaded.
    embeddings = load_card_embedding()
    # cv = props_vector(card.get_cards(), props=['cmc'], backface=False)
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        # rows = [row for row in reader]
        deck_data = [(
            embeddings[card.get_card(c1).card_faces[0].name],
            embeddings[card.get_card(c2).card_faces[0].name],
        # card_encode(c1, embeddings, cv) + card_encode(c2, embeddings, cv),
            torch.tensor(int(syn)).float())
            for c1, c2, syn in progressbar(reader)]
    # print("Point 1")
    deck_data = util.transpose(deck_data)
    # print("Point 2")
    return SynergyDataset(deck_data[0], deck_data[1], deck_data[2])


def deck_task(filepath):
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            deck = parse_decklist(f.read(), limit=60)
            lands = []
            for name in deck:
                try:
                    c = card.get_card(name)
                except KeyError:
                    c = card.get_card(card.find_name(name))
                if not is_nonland(c):
                    lands.append(name)
            deck.pop(lands, None)
            return deck


def create_deck_data(set_code, train_file=TRAIN_SYNERGY, test_file=TEST_SYNERGY, train_rate=0.7):
    card.load_cards(data.load(no_download=True))
    decklists = []
    decklist_dir = '../data/decklists/standard'

    with ThreadPoolExecutor(max_workers=64) as executor:
        # setdirs = [ os.path.join(decklist_dir, s) for s in os.listdir(decklist_dir) if SETS[s].date <= SETS[set_code].date ]
        futures = []
        for setdir in os.listdir(decklist_dir):
            if SETS[setdir].date <= SETS[set_code].date:
                setdir = os.path.join(decklist_dir, setdir)
                for deckdir in os.listdir(setdir):
                    deckdir = os.path.join(setdir, deckdir)
                    # for deck in islice(os.listdir(deckdir), 5):
                    for deck in os.listdir(deckdir):
                        filepath = os.path.join(deckdir, deck)
                        futures.append(executor.submit(deck_task, filepath))
        for f in progressbar(as_completed(futures)):
            decklists.append(f.result())
    write_deck_data(decklists, train_file, test_file, train_rate)


if __name__ == '__main__':
    card.load_cards(data.load(no_download=True))
    decklists = []
    decklist_dir = '../data/decklists/standard'
    for setdir in os.listdir(decklist_dir):
        if setdir not in ['DFT', 'TDM', 'FIN', 'EOE']:
            setdir = os.path.join(decklist_dir, setdir)
            for deckdir in os.listdir(setdir):
                deckdir = os.path.join(setdir, deckdir)
                # for deck in islice(os.listdir(deckdir), 10):
                for deck in os.listdir(deckdir):
                    filepath = os.path.join(deckdir, deck)
                    if os.path.isfile(filepath):
                        with open(filepath, 'r') as f:
                            deck = parse_decklist(f.read())
                            decklists.append(deck)
    write_deck_data(decklists)
