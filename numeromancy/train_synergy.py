import os

from numeromancy.model import synergy_model, SYNERGYDIR, create_deck_data, read_deck_data
import numeromancy.card as card
import numeromancy.data as data


# Train synergy using decklist data up until the specified set
def train_synergy(set_code, create_data=True):
    file_dir = os.path.join(SYNERGYDIR, set_code)
    os.makedirs(file_dir, exist_ok=True)
    train_file = os.path.join(file_dir, 'train.csv')
    test_file = os.path.join(file_dir, 'test.csv')
    model_file = os.path.join(file_dir, 'classifier.pt')
    if create_data:
        create_deck_data(set_code, train_file, test_file)

    model = synergy_model.train_model(synergy_model.new_model(), train_file=train_file, model_file=model_file)
    model.eval()
    synergy_model.test_model(model, test_file=test_file)


def load_trained_synergy(set_code):
    file_dir = os.path.join(SYNERGYDIR, set_code)
    model_file = os.path.join(file_dir, 'classifier.pt')
    return synergy_model.load_model(model_file)
