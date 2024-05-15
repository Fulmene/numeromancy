import os
from xgboost import XGBModel, XGBClassifier

from embedding import load_embedding


def new_model() -> XGBModel:
    emb = load_embedding()
    model = XGBClassifier(n_estimators=100, max_depth=35, objective='binary:logistic')
    return model


def train_model(model: XGBModel, train_data: str | os.PathLike) -> XGBModel:

    model.fit(x_train, y_train)
    return model
