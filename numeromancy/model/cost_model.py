import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
# import xgboost as xgb
from progressbar import progressbar

from numeromancy.preprocessing import CARD_TEXTS, TRAIN_TEXTS, TEST_TEXTS, props_vector, read_text
from .card_embedding import CardEmbedding, CardDataset
import numeromancy.card as card
import numeromancy.data as data
import numeromancy.util as util


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODELDIR = os.path.join(data.OUTPUTDIR, 'model')
CARD_EMBEDDING = os.path.join(MODELDIR, 'card_embedding')
COST_CLASSIFIER = os.path.join(MODELDIR, 'classifier')
EMBEDDING_DICT = os.path.join(MODELDIR, 'card_embedding.pt')


def load_model(emb_path=CARD_EMBEDDING, clf_path=COST_CLASSIFIER):
    emb = CardEmbedding().to(device)
    emb.load_state_dict(torch.load(emb_path, weights_only=True))
    emb.eval()

    clf = nn.Sequential(
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 1)).to(device)
    clf.load_state_dict(torch.load(clf_path, weights_only=True))
    clf.eval()
    return emb, clf


def save_card_embedding():
    emb, _ = load_model()
    card.load_cards(data.load())
    cards = card.get_cards()
    face_names = list(f.name for c in cards for f in c.card_faces)
    pv = props_vector(cards)
    texts = dict(read_text(CARD_TEXTS))
    dataset = [(torch.from_numpy(pv[f]).float().to("cpu"),
            texts[f],
            f)
            for f in face_names]
    dataset = util.transpose(dataset)
    dataloader = DataLoader(
        CardDataset(dataset[0], dataset[1], dataset[2]),
        batch_size=128)

    with torch.no_grad():
        embeddings = {}
        for props, text, name in progressbar(dataloader):
            embed = emb(props, text).to("cpu")
            for n, e in zip(name, embed):
                embeddings[n] = e
        torch.save(embeddings, EMBEDDING_DICT)


def load_card_embedding():
    embeddings = torch.load(EMBEDDING_DICT)
    return embeddings


if __name__ == '__main__':
    epochs = 300
    batch_size = 128
    num_classes = 8

    card.load_cards(data.load(no_download=True))
    cards = card.get_cards()

    emb = CardEmbedding().to(device)
    for param in emb.transformer.parameters():
        param.requires_grad = True

    # TODO maybe filter lands out of the data
    pv = props_vector(cards, backface=False)
    cv = props_vector(cards, props=['cmc'], backface=False)

    train_texts = [(name, text) for name, text in read_text(TRAIN_TEXTS) if name in pv]
    test_texts = [(name, text) for name, text in read_text(TEST_TEXTS) if name in pv]
    # train_items = [(k, v) for k, v in train_texts if k in pv]
    # test_items = [(k, v) for k, v in test_texts if k in pv]

    train_dataset = [(torch.from_numpy(pv[name]).float(), text, min(int(cv[name].item()), num_classes-1)) for name, text in train_texts]
    train_dataset = util.transpose(train_dataset)
    test_dataset = [(torch.from_numpy(pv[name]).float(), text, min(int(cv[name].item()), num_classes-1)) for name, text in test_texts]
    test_dataset = util.transpose(test_dataset)
    y_train = train_dataset[2]
    y_test = test_dataset[2]
    train_loader = DataLoader(
        CardDataset(train_dataset[0],
                    train_dataset[1],
                    y_train),
        batch_size=batch_size,
        shuffle=True)
    test_loader = DataLoader(
        CardDataset(test_dataset[0],
                    test_dataset[1],
                    y_test),
        batch_size=batch_size)

    simple_clf = nn.Sequential(
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 1)).to(device)

    optimizer = torch.optim.Adam(
        list(emb.parameters()) + list(simple_clf.parameters()),
        lr=2e-5)
    loss_fn = nn.MSELoss()

    emb.train()
    simple_clf.train()

    for epoch in range(epochs):
        total_loss = 0
        for props, text, label in progressbar(train_loader):
            label = label.to(device).float().unsqueeze(1)
            embedding = emb(props, text)
            logits = simple_clf(embedding)
            loss = loss_fn(logits, label)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1} | Loss: {total_loss: .4f}")

    simple_clf.eval()
    emb.eval()

    with torch.no_grad():
        sse = 0.0
        size = 0
        for props, text, label in progressbar(test_loader):
            embedding = emb(props, text)
            y_pred = simple_clf(embedding)
            #y_pred = torch.argmax(logits, dim=1)
            sse += sum(cmc - y for cmc, y in zip(label, y_pred))
            size += y_pred.shape[0]
        print("MSE: ", sse/size)
        #print("Accuracy: ", hit/size)
        #print("Close: ", (hit + close/2)/size)

    os.makedirs(MODELDIR, exist_ok=True)
    torch.save(emb.state_dict(), CARD_EMBEDDING)
    torch.save(simple_clf.state_dict(), COST_CLASSIFIER)

    """
    with torch.no_grad():
        x_train = []
        x_test = []
        for batch_props, batch_text, _ in progressbar(train_loader):
            batch_emb = emb(batch_props, batch_text)
            x_train.append(batch_emb.cpu().numpy())
        for batch_props, batch_text, _ in progressbar(test_loader):
            batch_emb = emb(batch_props, batch_text)
            x_test.append(batch_emb.cpu().numpy())
        x_train = np.concatenate(x_train, 0)
        x_test = np.concatenate(x_test, 0)

    # x_train = np.concatenate([emb(torch.unsqueeze(torch.from_numpy(pv[name]), dim=0), text).cpu().numpy() for name, text in progressbar(train_items)], 0)
    # x_test = np.concatenate([emb(torch.unsqueeze(torch.from_numpy(pv[name]), 0), text).cpu().numpy() for name, text in progressbar(test_items)], 0)
    # y_test = [cv[name].item() for name, _ in test_items]

    model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_classes=num_classes,
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        tree_method='gpu_hist' if torch.cuda.is_available() else 'hist',
        eval_metric='mlogloss',
        use_label_encoder=False,
    )

    model.fit(
        x_train, y_train,
        verbose=True,
    )

    pred = model.predict(x_test)
    correct = 0
    close = 0
    for p, y in zip(pred, y_test):
        if p == y:
            correct += 1
        elif abs(p - y) == 1:
            close += 1
    print("Accuracy: ", correct/len(y_test))
    print("Close enough: ", (correct + close/2)/len(y_test))
    """
