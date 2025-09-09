# This file is part of Demystify.
# 
# Demystify: a Magic: The Gathering parser
# Copyright (C) 2022 Ada Joule
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

import logging
_logger = logging.getLogger(__name__)

import queue
import multiprocessing
import multiprocessing.queues
import sys
from typing import Optional
import progressbar

from .cmc import cmc

SUPERTYPES = {
    'Basic',
    'Legendary',
    'Ongoing',
    'Snow',
    'World',
}

TYPES = {
    'Artifact',
    'Battle',
    'Conspiracy',
    'Creature',
    'Dungeon',
    'Enchantment',
    'Instant',
    'Land',
    'Phenomenon',
    'Plane',
    'Planeswalker',
    'Scheme',
    'Sorcery',
    'Tribal',
    'Vanguard',
}


def parse_type_line(type_line: str) -> tuple[list[str], list[str], list[str]]:
    split_type = type_line.split(' // ')
    supertypes = []
    cardtypes = []
    subtypes = []
    for typeline in split_type:
        mdashed_types = typeline.split(' — ')
        left = mdashed_types[0].split()
        supertypes += [t for t in left if t in SUPERTYPES]
        cardtypes += [t for t in left if t in TYPES]
        subtypes += mdashed_types[1].split() if len(mdashed_types) > 1 else []
    return supertypes, cardtypes, subtypes


class CardFace:
    def __init__(self, scryfall_card_face, card):
        self.name = scryfall_card_face.get("name")
        self.mana_cost = scryfall_card_face.get("mana_cost") or ""

        self.cmc = cmc(self.mana_cost)
        self.colors = scryfall_card_face.get("colors")
        if self.colors is None:
            self.colors = card.colors

        self.type_line = scryfall_card_face.get("type_line")
        self.supertypes, self.cardtypes, self.subtypes = parse_type_line(self.type_line)
        self.oracle_text = scryfall_card_face.get("oracle_text") or ""

        self.power = scryfall_card_face.get("power")
        self.toughness = scryfall_card_face.get("toughness")
        self.loyalty = scryfall_card_face.get("loyalty")
        self.defense = scryfall_card_face.get("defense")

    def __repr__(self):
        return f"Card: \"{self.name}\""

    def __str__(self):
        info = f"{self.name}\t\t{self.mana_cost}\n{self.type_line}\n{self.oracle_text}"
        pt = f"\n{self.power}/{self.toughness}" if self.power is not None else ""
        loyalty = f"\n<{self.loyalty}>" if self.loyalty is not None else ""
        defense = f"\n<{self.defense}>" if self.defense is not None else ""
        return f"{info}{pt}{loyalty}{defense}"


class Card:
    """ Stores *gameplay* information of a Magic card. """

    name: str
    layout: str
    card_faces: list[CardFace]
    colors: list[str]
    sets: set[str]

    def __init__(self, scryfall_card):
        self.name = scryfall_card.get("name")
        self.layout = scryfall_card.get("layout")
        self.legalities = scryfall_card.get("legalities")
        self.colors = scryfall_card.get("colors")
        self.sets = set([scryfall_card.get("set")])

        if self.layout in ["split", "flip", "transform", "modal_dfc", "adventure", "battle"]:
            # Scryfall puts mana cost of adventure lands on the land side instead of adventure side
            #     as of the implementing of this part of the code. Remove if it ever gets fixed.
            faces = scryfall_card.get("card_faces")
            if self.layout == "adventure" and "Land" in faces[0]['type_line']:
                faces[1]['mana_cost'] = faces[0]['mana_cost']
                faces[0]['mana_cost'] = ''

            self.card_faces = [
                CardFace(faces[0], self),
                CardFace(faces[1], self),
            ]
        else:
            self.card_faces = [CardFace(scryfall_card, self)]

        #self.mana_cost = scryfall_card.get("mana_cost") or ""
        # Mana value of some funny cards can be fractional, but for "real" cards, it's integer only
        #self.cmc = int(scryfall_card.get("cmc"))
        #self.color_identity = scryfall_card.get("color_identity")
        #self.colors = scryfall_card.get("colors")

        #self.type_line = scryfall_card.get("type_line")
        #self.supertypes, self.cardtypes, self.subtypes = parse_type_line(self.type_line)
        #self.oracle_text = scryfall_card.get("oracle_text") or ""

        #self.power = scryfall_card.get("power")
        #self.toughness = scryfall_card.get("toughness")
        #self.loyalty = scryfall_card.get("loyalty")

    def __repr__(self):
        return f"Card: \"{self.name}\""

    def __str__(self):
        info = f"{self.name}\t\t({self.layout})"
        faces = ''.join('\n' + str(f) for f in self.card_faces)
        return f"{info}{faces}"


class CardProgressBar(list):
    """ A list-like object that writes a progress bar to stdout
        when iterated over. """
    def __iter__(self):
        """ A generator that writes a progress bar to stdout as its elements
            are accessed. """
        widgets = [progressbar.widgets.Variable('cardname', format='{formatted_value}', width=16, precision=16), ' ',
                   progressbar.widgets.Bar(left='[', right=']'), ' ',
                   progressbar.widgets.SimpleProgress(), ' ',
                   progressbar.widgets.ETA()]
        pbar = progressbar.bar.ProgressBar(widgets=widgets, max_value=len(self))
        pbar.start()
        for i, card in enumerate(super(CardProgressBar, self).__iter__()):
            cardname = card.name if hasattr(card, "name") else card.get("name")
            pbar.update(i, cardname=cardname[:16])
            yield card
        pbar.finish()


## Multiprocessing support for card-related tasks

class CardProgressQueue(multiprocessing.queues.JoinableQueue):
    def __init__(self, cards):
        super(CardProgressQueue, self).__init__(
                len(cards), ctx=multiprocessing.get_context())
        widgets = [progressbar.widgets.Variable('cardname', format='{formatted_value}', width=16, precision=16), ' ',
                   progressbar.widgets.Bar(left='[', right=']'), ' ',
                   progressbar.widgets.SimpleProgress(), ' ',
                   progressbar.widgets.ETA()]
        self._pbar = progressbar.bar.ProgressBar(widgets=widgets, max_value=len(cards))
        self._pbar.start()
        for c in cards:
            self.put(c)

    def task_done(self, cname=' '):
        with self._cond:
            if not self._unfinished_tasks.acquire(False):
                raise ValueError('task_done() called too many times')
            if self._unfinished_tasks._semlock._is_zero():
                self._pbar.finish()
                self._cond.notify_all()
            else:
                self._pbar.update(self._sem._semlock._get_value(), cardname=cname[:16])


def _card_worker(work_queue, res_queue, func):
    _logger.debug("Card worker starting up - Python {}".format(sys.version))
    try:
        while True:
            c = work_queue.get(timeout=0.2)
            try:
                res = func(c)
                res_queue.put(res)
            except queue.Full:
                _logger.error("Result queue full, can't add result for {}."
                             .format(c.name))
                res_queue.put(None)
            except Exception as e:
                _logger.exception('Exception encountered processing {} for '
                                 '{}: {}'.format(func.__name__, c.name, e))
                res_queue.put(None)
            finally:
                work_queue.task_done(cname=c.name)
    except queue.Empty:
        return
    except Exception as e:
        _logger.fatal('Fatal exception processing {}: {}'
                     .format(func.__name__, e))


def map_multi(func, cards, processes=None):
    """ Applies a given function to each card in cards, utilizing
        multiple processes, and displaying progress with a CardProgressBar.
        Results are not guaranteed to be in any order relating to the
        initial order of cards, and all None results and exceptions thrown
        are stripped out. If correlated results are desired, the function
        should return the name of the card alongside the result.

        func: A function that takes in a single Card object as an argument.
            Any modifications this function makes to Card data will be lost
            when it exits, hence it should return said data and the callee
            should modify the Card as specified. The only caveat to this is
            that the data it returns must be pickleable.
        cards: An iterable of Card objects that supports __len__.
        processes: The number of processes. If None, defaults to the 
            number of CPUs. """
    if not processes:
        processes = multiprocessing.cpu_count()
    q = CardProgressQueue(cards)
    rq = multiprocessing.Queue()
    pr = [multiprocessing.Process(target=_card_worker, args=(q, rq, func))
          for _ in range(processes)]
    for p in pr:
        p.start()
    q.join()
    result = []
    for _ in cards:
        res = rq.get()
        if res is not None:
            result.append(res)
    for p in pr:
        p.join()
    return result
