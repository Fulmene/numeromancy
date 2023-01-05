import os
from xgboost import XGBModel


def train_model(model: XGBModel, train_data: str | os.PathLike) -> XGBModel:
    model.fit(x_train, y_train)
    return model
