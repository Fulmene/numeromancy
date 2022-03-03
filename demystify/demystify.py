# This file is part of Demystify.
# 
# Demystify: a Magic: The Gathering parser
# Copyright (C) 2012 Benjamin S Wolf
# 
# Demystify is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
# 
# Demystify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Demystify.  If not, see <http://www.gnu.org/licenses/>.

"""demystify -- A Magic: The Gathering parser."""

import argparse
import logging
import re

logging.basicConfig(level=logging.DEBUG, filename="LOG", filemode="w")
plog = logging.getLogger("Parser")
plog.setLevel(logging.DEBUG)
_stdout = logging.StreamHandler()
_stdout.setLevel(logging.WARNING)
_stdout.setFormatter(logging.Formatter(fmt='%(levelname)s: %(message)s'))
plog.addHandler(_stdout)

import parse
import card
import data
# import test

def get_cards():
    return card.get_cards();

def preprocess(args):
    raw_cards = []
    for obj in data.load():
        # filter down to modern-legal only
        if obj["legalities"]["modern"] in ("legal", "banned") and "token" not in obj["layout"]:
            raw_cards.append(obj)
            _ = card.scryfall_card(**obj)
    numcards = len(raw_cards)
    if numcards == 0:
        plog.error("No cards found.")
        return 1
    cards = card.get_cards()
    split = {c.name for c in cards if c.multitype == "split"}
    xsplit = {c.multicard for c in cards if c.multitype == "split"}
    logging.debug("Split cards: " + "; ".join(sorted(split)))
    if split != xsplit:
        logging.error("Difference: " + "; ".join(split ^ xsplit))
    flip = {c.name for c in cards if c.multitype == "flip"}
    xflip = {c.multicard for c in cards if c.multitype == "flip"}
    logging.debug("Flip cards: " + "; ".join(sorted(flip)))
    if flip != xflip:
        logging.error("Difference: " + "; ".join(flip ^ xflip))
    trans = {c.name for c in cards if c.multitype == "transform"}
    xtrans = {c.multicard for c in cards if c.multitype == "transform"}
    logging.debug("Transform cards: " + "; ".join(sorted(trans)))
    if trans != xtrans:
        logging.error("Difference: " + "; ".join(trans ^ xtrans))
    # TODO Adventure
    # TODO MDFC
    s = int(len(split) / 2)
    f = int(len(flip) / 2)
    t = int(len(trans) / 2)
    logging.info("Discovered {} unique (physical) cards, from {} objects, including "
                 "{} split cards, {} flip cards, and {} transform cards."
                 .format(len(cards) - s - f - t, numcards, s, f, t))
    legalcards = get_cards()
    logging.info("Found {} banned cards.".format(len(cards) - len(legalcards)))
    card.preprocess_all(legalcards)
    if args.interactive:
        import code
        code.interact(local=globals())

def main():
    parser = argparse.ArgumentParser(
        description='A Magic: the Gathering parser.')
    subparsers = parser.add_subparsers()
    # test.add_subcommands(subparsers)
    loader = subparsers.add_parser('load')
    loader.add_argument('-i', '--interactive', action='store_true',
                        help='Enter interactive mode instead of exiting.')
    loader.set_defaults(func=preprocess)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
