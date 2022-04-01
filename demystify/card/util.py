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

""" Utility functions to search card text, get simple text stats """

import re

from .data import get_cards

def search_text(text, cards=None, reflags=re.I|re.U):
    """ Returns a list of (card name, line of text), containing
        every line in the text of a card that contains a match for the
        given text.

        A subset of cards can be specified if one doesn't want to search
        the entire set. """
    if not cards:
        cards = get_cards()
    r = re.compile(text, reflags)
    return [(c.name, line) for c in cards for line in c.rules_text.split('\n')
            if r.search(line)]

def preceding_words(text, cards=None, reflags=re.I|re.U):
    """ Returns a set of words which appear anywhere in a card's rules text
        before the given text.

        A subset of cards can be specified if one doesn't want to search
        the entire set. """
    if not cards:
        cards = get_cards()
    r = re.compile(r"([\w'-—]+)(?: | ?—){}".format(text), reflags)
    a = set()
    for c in cards:
        a.update(r.findall(c.rules_text))
    return a

def following_words(text, cards=None, reflags=re.I|re.U):
    """ Returns a set of words which appear anywhere in a card's rules text
        after the given text.

        A subset of cards can be specified if one doesn't want to search
        the entire set. """
    if not cards:
        cards = get_cards()
    r = re.compile(r"{}(?: |— ?)([\w'-—]+)".format(text), reflags)
    a = set()
    for c in cards:
        a.update(r.findall(c.rules_text))
    return a

def matching_text(text, cards=None, reflags=re.I|re.U, group=0):
    """ Returns a set of all matches for the given regex.
        By default use the whole match. Set group to use only the specific
        match group.

        A subset of cards can be specified if one doesn't want to search
        the entire set. """
    if not cards:
        cards = get_cards()
    r = re.compile(text, reflags)
    a = set()
    for c in cards:
        for m in r.finditer(c.rules_text):
            a.add(m.group(group))
    return a

def counter_types(cards=None):
    """ Returns a list of counter types named in the given cards. """
    cwords = preceding_words('counter', cards=cards)
    # Disallow punctuation, common words, and words about countering spells.
    cwords = {w for w in cwords if w and w[-1] not in '—-,.:\'"'}
    common = {'a', 'all', 'and', 'be', 'control', 'each', 'five', 'had',
              'have', 'is', 'may', 'more', 'of', 'or', 'spell', 'that',
              'those', 'was', 'with', 'would', 'x'}
    return sorted(cwords - common)

_punct = re.compile('[ \n—.]')

def missing_words(cards=None):
    """ Returns a set of new words not accounted for in words.py. """
    from words import all_words, macro_words
    existing_words = {w for y in set(all_words) | macro_words for w in y.split()}
    if not cards:
        cards = get_cards()
    seen_words = set()
    for c in cards:
        # If whitespace doesn't really matter, we could put punctuation
        # in the preprocessing, replace any "." with " . ", etc.
        # That way, we wouldn't need a regex to split with (but we'd still
        # maybe want some of this handling to catch 's and jump-start.
        for w in _punct.split(c.rules_text):
            w = w.lstrip("'").rstrip(',;:."')
            if w.startswith("non-"):
                w = w[4:]
            if (not w or any(x in w for x in ("NAME", "{", "[", "/"))
                    or not w[0].isalpha()):
                continue
            if w.endswith("'s") or w.endswith("s'"):
                seen_words.add(w[:-2])
            elif w.endswith("n't") or w.endswith("'ve") or w.endswith("'re"):
                seen_words.add(w[:-3])
            else:
                seen_words.add(w)
    # Or odd half-words from split tokens.
    common_words = {'SELF', 'PARENT', 'x', 'y', 'plainswalk', 'islandwalk',
                    'swampwalk', 'mountainwalk', 'forestwalk', 'desertwalk',
                    'plainscycling', 'islandcycling', 'swampcycling',
                    'mountaincycling', 'forestcycling', 'landcycling',
                    'slivercycling', 'wizardcycling',
                    'arabian', 'nights', 'urza', 'ca', 'city'}
    return seen_words - existing_words - common_words

def missing_types(cards=None):
    """ Returns a set of new subtypes not accounted for in words.py. """
    from words import subtypes, types
    existing_types = set(subtypes) | set(types)
    if not cards:
        cards = get_cards()
    seen_types = set(w for c in cards for w in c.types.split())
    not_types = {'—', '//'}
    return seen_types - existing_types - not_types
