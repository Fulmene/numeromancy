import os

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from progressbar import progressbar

from preprocessing import CARD_TEXTS, props_vector, read_text
from card_embedding import CardEmbedding
from cost_model import CARD_EMBEDDING, MODELDIR
from deck_data import read_deck_data, TRAIN_SYNERGY, TEST_SYNERGY
import card, data

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SYNERGY_CLASSIFIER = os.path.join(MODELDIR, 'synergy_classifier')


def load_model(emb_path=CARD_EMBEDDING, clf_path=SYNERGY_CLASSIFIER):
    emb = CardEmbedding().to(device)
    emb.load_state_dict(torch.load(emb_path, weights_only=True))
    emb.eval()

    clf = nn.Sequential(
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 1),
        nn.Sigmoid()).to(device)
    clf.load_state_dict(torch.load(clf_path, weights_only=True))
    clf.eval()
    return emb, clf


if __name__ == '__main__':
    epochs = 500
    batch_size = 16384

    card.load_cards(data.load(no_download=True))
    cards = card.get_cards()

    train_loader = DataLoader(read_deck_data(TRAIN_SYNERGY), batch_size=batch_size, shuffle=True)

    clf = nn.Sequential(
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 1)).to(device)
    optimizer = torch.optim.Adam(
        list(clf.parameters()),
        lr=2e-5)
    loss_fn = nn.BCEWithLogitsLoss()
    clf.train()

    for epoch in range(epochs):
        total_loss = 0
        for emb1, emb2, synergy in progressbar(train_loader):
            synergy = synergy.to(device).float().unsqueeze(1)
            logits = clf(torch.cat((emb1, emb2), dim=1).to(device))
            loss = loss_fn(logits, synergy)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1} | Loss: {total_loss: .4f}")

    clf.eval()
    del train_loader

    test_loader = DataLoader(read_deck_data(TEST_SYNERGY), batch_size=batch_size)
    with torch.no_grad():
        hit = 0
        all = 0
        for emb1, emb2, synergy in progressbar(test_loader):
            logits = clf(torch.cat((emb1, emb2), dim=1).to(device))
            prob = torch.sigmoid(logits)
            hit += sum(1 if abs(s - l) < 0.5 else 0 for l, s in zip(prob, synergy))
            all += len(logits)
            # print(logits, synergy)
        print(f"Accuracy: {hit/all}")


    os.makedirs(MODELDIR, exist_ok=True)
    torch.save(clf.state_dict(), SYNERGY_CLASSIFIER)
