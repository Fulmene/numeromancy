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

"""card.preprocessing -- Card text preprocessing"""

import re

from .card import Card, CardFace
from .names import preprocess_names, construct_shortname


# Basically, LPAREN then anything until RPAREN, but there may
# be nested parentheses inside braces for hybrid mana symbols
# (this occurs in reminder text about hybrid mana symbols).
# Also watch out for the parentheses inside hybrid mana symbols themselves.
_reminder_text = re.compile(r".?\([^{()]*(\{[^}]*\}[^{()]*)*\).?")

def _reminder_chop(m):
    s = m.group(0)
    if s[0] == '{':
        return s
    elif s[0] == ' ' and s[-1] != ')':
        return s[-1]
    return ''

def preprocess_reminder(text) -> str:
    """ Chop out reminder text during the preprocessing step.
    
        While this isn't strictly necessary because we can ignore reminder
        text via an ignore token, it is useful to do during preprocessing
        so that searching cards for text won't match reminder text. """
    return _reminder_text.sub(_reminder_chop, text).strip()


def preprocess_capitals(text) -> str:
    """ Lowercase every word (but not SELF, PARENT, NAME_, or
        bare mana symbols). """
    if len(text) == 1:
        return text
    return ' '.join(
        [w if 'SELF' in w or 'PARENT' in w or 'NAME_' in w
            else w.lower()
            for w in text.split(' ')])


# Min length is 2 to avoid the sole exception of "none".
_non = re.compile(r"\bnon(\w{2,})", flags=re.I|re.U)
_pw = re.compile(r"^−", flags=re.M)

def preprocess_misc(text: str) -> str:
    """ Miscellaneous text preprocessing. """
    # Ensure a dash appears between non and the word it modifies.
    text = _non.sub(r"non-\1", text)
    # Ensure planeswalker ability costs use minus signs.
    text = _pw.sub("-", text)
    # Replace "’" with "'"
    text = text.replace("’", "'")
    return text


def preprocess_typeline(type_line: str) -> str:
    """ Type line processing. """
    # Lowercase every word
    type_line = preprocess_capitals(type_line)
    # Replace "’" with "'"
    type_line = type_line.replace("’", "'")
    return type_line


def preprocess_rulestext(oracle_text: str, names) -> str:
    # A planeswalker's name appearing in rules text is usually its type, not its short name
    lines = [preprocess_capitals(preprocess_names(preprocess_reminder(line), names))
        for line in oracle_text.split("\n")]
    return preprocess_misc("\n".join(lines))


def preprocess_face(card_face: CardFace):
    """ Scans the rules texts of a card to replace any card names that
        appear with appropriate symbols, and eliminates reminder text. """
    card_face.types = preprocess_typeline(card_face.type_line)

    names = (card_face.name,)
    shortname = construct_shortname(card_face.name)
    if shortname and "planeswalker" not in card_face.types:
        names += (shortname,)

    card_face.rules_text = preprocess_rulestext(card_face.oracle_text, names)


## Main entry point for the preprocessing step ##
def preprocess_all(card: Card):
    for f in card.card_faces:
        preprocess_face(f)
