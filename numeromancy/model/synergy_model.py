import os

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from progressbar import progressbar

from numeromancy.preprocessing import CARD_TEXTS, props_vector, read_text
from .card_embedding import CardEmbedding
from .cost_model import CARD_EMBEDDING, MODELDIR
from .deck_data import read_deck_data, TRAIN_SYNERGY, TEST_SYNERGY
import numeromancy.card as card
import numeromancy.data as data

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SYNERGY_CLASSIFIER = os.path.join(MODELDIR, 'synergy_classifier')


def new_model():
    return nn.Sequential(
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 1)).to(device)


def load_model(model_file=SYNERGY_CLASSIFIER):
    model = new_model()
    model.load_state_dict(torch.load(model_file, weights_only=True))
    model.eval()
    return model


def train_model(model, train_file=TRAIN_SYNERGY, model_file=SYNERGY_CLASSIFIER, epochs=500, batch_size=16384):
    card.load_cards(data.load(no_download=True))
    cards = card.get_cards()

    train_loader = DataLoader(read_deck_data(train_file), batch_size=batch_size, shuffle=True)

    optimizer = torch.optim.Adam(
        list(model.parameters()),
        lr=2e-5)
    loss_fn = nn.BCEWithLogitsLoss()
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for emb1, emb2, synergy in progressbar(train_loader):
            synergy = synergy.to(device).float().unsqueeze(1)
            logits = model(torch.cat((emb1, emb2), dim=1).to(device))
            loss = loss_fn(logits, synergy)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1} | Loss: {total_loss: .4f}")
    torch.save(model.state_dict(), model_file)

    return model


def test_model(model, test_file=TEST_SYNERGY, batch_size=16384):
    card.load_cards(data.load(no_download=True))
    cards = card.get_cards()

    test_loader = DataLoader(read_deck_data(test_file), batch_size=batch_size, shuffle=True)
    with torch.no_grad():
        hit = 0
        all = 0
        for emb1, emb2, synergy in progressbar(test_loader):
            logits = model(torch.cat((emb1, emb2), dim=1).to(device))
            prob = torch.sigmoid(logits)
            hit += sum(1 if abs(s - l) < 0.5 else 0 for l, s in zip(prob, synergy))
            all += len(logits)
            # print(logits, synergy)
        print(f"Accuracy: {hit/all}")


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
