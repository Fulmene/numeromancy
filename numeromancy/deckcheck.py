import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from progressbar import progressbar

from numeromancy.parse_decklist import parse_decklist
import numeromancy.card as card
import numeromancy.data as data


def task(deck):
    with open(deck, 'r') as d:
        dc = parse_decklist(d.read())
        for k in dc:
            if k == 'Unknown Card':
                continue
            try:
                card.find_name(k)
            except KeyError:
                print(f'Card not found: {deck} {k}')


if __name__ == '__main__':
    card.load_cards(data.load(no_download=False))

    with ThreadPoolExecutor(max_workers=256) as executor:
        futures = []
        deckdir = Path('../data/decklists')
        for f in deckdir.iterdir():
            for s in f.iterdir():
                if s.name != 'EOE':
                    for a in s.iterdir():
                        try:
                            for deck in a.iterdir():
                                futures.append(executor.submit(task, deck))
                        except NotADirectoryError:
                            loose = s.joinpath('Loose')
                            os.makedirs(loose, exist_ok=True)
                            deck = shutil.move(a, loose)
                            futures.append(executor.submit(task, deck))
        for _ in progressbar(as_completed(futures)):
            pass
