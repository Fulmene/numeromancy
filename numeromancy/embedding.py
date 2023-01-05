import sys
import os
import csv
import re
from gensim.models import Word2Vec

from data import DATADIR
from preprocessing import CARD_TEXTS


EMBEDDING_MODEL = os.path.join(DATADIR, 'embedding.model')


def make_sents(text: str) -> list[list[str]]:
    sentences = re.split(r'\.|\n', text)
    return [s.strip().split(' ') for s in sentences if s]


def generate_embedding(texts_csv=CARD_TEXTS) -> Word2Vec:
    with open(texts_csv, 'r', encoding='UTF-8') as f:
        reader = csv.reader(f)
        sents = [item for row in reader for item in make_sents(row[1])]
        return Word2Vec(sentences=sents)


def load_embedding(filename=EMBEDDING_MODEL) -> Word2Vec:
    return Word2Vec.load(filename)


if __name__ == '__main__':
    print("Saving card text embedding model", file=sys.stderr)
    generate_embedding().save(EMBEDDING_MODEL)
