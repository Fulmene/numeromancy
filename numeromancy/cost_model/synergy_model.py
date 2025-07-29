# synergy_model

from xgboost import XGBModel, XGBClassifier

def new_model():
    model = XGBClassifier(n_estimators=100, max_depth=35, objective='binary:logistic')
    return model


def save_model(model):
    return


def load_model():
    return


def train(model):
    return


def predict(model, card_vectors, card1, card2):
    input = card_vectors[card1] + card_vectors[card2]
    pred = model.predict(input)
    return pred
