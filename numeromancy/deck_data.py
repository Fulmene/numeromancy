import os
import random
import csv

import torch
from torch.utils.data import Dataset
from preprocessing import CARD_TEXTS, props_vector, read_text
from progressbar import progressbar

import card, data, util
from parse_decklist import parse_decklist
from card_embedding import CardEmbedding
from cost_model import CARD_EMBEDDING, load_card_embedding

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
    positive_data = create_positive_data(decklists)
    random.shuffle(positive_data)
    negative_data = create_negative_data(decklists, num=len(positive_data))
    # neg data is already randomly generated so no need to shuffle
    psplit = int(len(positive_data)*train_rate)
    nsplit = int(len(negative_data)*train_rate)

    os.makedirs(SYNERGYDIR, exist_ok=True)

    with open(train_file, 'w') as f:
        pd = positive_data[:psplit]
        nd = negative_data[:nsplit]
        d = pd + nd
        writer = csv.writer(f)
        writer.writerows(d)

    with open(test_file, 'w') as f:
        pd = positive_data[psplit:]
        nd = negative_data[nsplit:]
        d = pd + nd
        writer = csv.writer(f)
        writer.writerows(d)


def read_deck_data(filename):
    embeddings = load_card_embedding()
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        deck_data = [(
            embeddings[c1],
            embeddings[c2],
            torch.tensor(int(syn)).float())
            for c1, c2, syn in reader]
        deck_data = util.transpose(deck_data)
        return SynergyDataset(deck_data[0], deck_data[1], deck_data[2])


if __name__ == '__main__':
    card.load_cards(data.load(no_download=True))
    decklists = []
    decklist_dir = '../data/decklists'
    for filename in os.listdir(decklist_dir):
        filepath = os.path.join(decklist_dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                deck = parse_decklist(f.read())
                decklists.append(deck)
    write_deck_data(decklists)
