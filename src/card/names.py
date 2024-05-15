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

"""card.name -- Name-related preprocessing"""

import re
from collections.abc import Iterable, Sequence

import logging
_logger = logging.getLogger(__name__)


nonwords = re.compile(r'\W', flags=re.UNICODE)
def construct_uname(name: str):
    """ Return name with 'NAME_' appended to the front, and every non-word
        character (as in \\W) replaced with an underscore. This is intended
        to be a unique mapping of the card name to one which contains only
        alphanumerics and underscores. """
    return "NAME_" + nonwords.sub(r'_', name)


_uname_from_name: dict[str, str] = {}
_name_from_uname: dict[str, str] = {}

def add_name(name):
    uname = construct_uname(name)
    _uname_from_name[name] = uname
    _name_from_uname[uname] = name

def clear_names():
    _uname_from_name.clear()
    _name_from_uname.clear()


# Handle any Legendary names we couldn't get with ", " or " the ", most of
# which have two words only, eg. Arcades Sabboth, or "of the".
# We wouldn't be able to guess these without also grabbing things like
# "Lady Caleria", "Sliver Overlord", "Phyrexian Tower", "Reaper King",
# "Patron of the Orochi", "Kodama of the North Tree", "Shield of Kaldra", etc.
# This list only includes cards that actually use a short name in its rules text.
shortname_extra = {
    "Axelrod Gunnarson"             : "Axelrod",
    "Catti-brie of Mithral Hall"    : "Catti-brie",
    "Darigaaz, the Igniter"         : "Darigaaz",
    "Darigaaz Reincarnated"         : "Darigaaz",
    "Drizzt Do'Urden"               : "Drizzt",
    "Hazezon Tamar"                 : "Hazezon",
    "Hivis of the Scale"            : "Hivis",
    "Rasputin Dreamweaver"          : "Rasputin",
    "Rubinia Soulsinger"            : "Rubinia",
    "Svyelun of Sea and Sky"        : "Svyelun",
}

def construct_shortname(name: str):
    if ', ' in name:
        return name[:name.index(', ')].strip()
    elif ' the ' in name:
        words = name[:name.index(' the ')].split()
        # if it's 'of' or 'from', for example, ignore
        if not words[-1].islower():
            return name[:name.index(' the ')].strip()
    return shortname_extra.get(name)


def preprocess_cardname(line: str, selfnames=(), parentnames=()):
    """ Checks only for matches against a card's name. """
    change = False
    for cardname in selfnames:
        if cardname in line:
            line, count = re.subn(r"\b{}(?!\w)".format(cardname),
                                  "SELF", line, flags=re.UNICODE)
            if count > 0:
                change = True
    for cardname in parentnames:
        if cardname in line:
            line, count = re.subn(r"\b{}(?!\w)".format(cardname),
                                  "PARENT", line, flags=re.UNICODE)
            if count > 0:
                change = True
    return line, change


def potential_names(text: str, cardnames: Iterable[str]):
    """ cardnames is a list of potential names, either SELF or PARENT,
        that should not be replaced with NAME_ tokens. """
    words = text.split()
    name = words[0]
    name2 = ''
    namelist = False
    if name[-1] in ':."':
        yield (name[:-1],)
    else:
        for i, w in enumerate(words[1:]):
            if w[0].isupper():
                name += name2 + ' ' + w
                name2 = ''
                if name[-1] in ':."':
                    break
            elif w in ['of', 'from', 'to', 'in', 'on', 'the', 'a']:
                name2 += ' ' + w
            elif w in ['and', 'or']:
                namelist = True
                name2 += ' ' + w
            else:
                break
        name = name.rstrip(',.:"')
        if ', ' in name:
            ns = name.split(', ', 1)
            if ns[0] == ns[1] and ns[0] in cardnames:
                yield (ns[0],)
                return
        yield (name,)
        if namelist:
            for sep in [' and ', ' or ']:
                names = name.split(sep)
                if len(names) > 1:
                    # pick each separator, join the rest,
                    # split those left of it on commas
                    # and iterate through joining them
                    # (but only from the left)
                    # eg. Example, This and That, Silly, and Serious or Not
                    # when "Example, This and That", "Silly", and
                    #      "Serious or Not" are the card names
                    for i in range(len(names) - 1, 0, -1):
                        left = sep.join(names[:i])
                        right = sep.join(names[i:])
                        lnames = left.split(', ')
                        if lnames[-1][-1] == ',':
                            lnames[-1] = lnames[-1][:-1]
                            # we saw ", and " for a 2-card list?
                            # the latter is probably SELF or PARENT
                            if len(lnames) == 1 and right in cardnames:
                                yield (lnames[0], )
                        if len(lnames) > 1:
                            yield tuple(lnames) + (right, )
                            if len(lnames) > 2:
                                for j in range(len(lnames) - 2, 1, -1):
                                    yield ((', '.join(lnames[:j]), )
                                           + tuple(lnames[j:])
                                           + (right, ))
                                # don't include right in this last case
                                # if it's SELF or PARENT
                                t = ((', '.join(lnames[:-1]), )
                                     + tuple(lnames[-1:]))
                                if right not in cardnames:
                                    t += (right, )
                                yield t
                        else:
                            yield (left, right)
        else:
            names = name.split(', ')
            while len(names) > 1:
                del names[-1]
                yield (', '.join(names),)


def format_by_name(text: str, names: Sequence[str]) -> str:
    """ Replaces all of the card names in text by its uname counterpart. """
    words = text.split()
    for name in names:
        if name not in _uname_from_name:
            _logger.info(f"Found token name: {name}")
            _logger.debug(f"From card text {str}")
            add_name(name)
    if len(names) == 1:
        ll = names[0].count(' ') + 1
        namelist = _uname_from_name[names[0]]
    else:
        _logger.info("Multiple names being replaced: {}."
                    .format("; ".join(names)))
        s = [_uname_from_name[n] for n in names]
        ll = sum([name.count(' ') + 1
                  for name in names[:-1]])
        c = words[ll]
        # + 2 because we have to count the connector word 'and' or 'or'
        ll += names[-1].count(' ') + 2
        namelist = ', '.join(s[:-1]) + ', ' + c + ' ' + s[-1]
    if words[ll - 1][-1] in ',.:"':
        if words[ll - 1][-2] in ',.:':
            namelist += words[ll - 1][-2:]
        else:
            namelist += words[ll - 1][-1]
    if len(words) > ll:
        namelist += ' ' + ' '.join(words[ll:])
    return namelist


# Words and phrases that are followed by card name
name_ref = re.compile(r"named |name is still |card name (that hasn't been chosen )?from among "
                      r"|transforms into |meld them into |Partner with |[Cc]reate ")
abil = re.compile(r'"[^"]+"')
def preprocess_names(line, selfnames=(), parentnames=()):
    """ This requires that each card was instantiated as a Card and their names
        added to the all_names dicts as appropriate. """
    match = name_ref.search(line)
    change = False
    while match:
        # Examine the words after the name_ref indicator
        i, j = match.regs[0]
        text = line[j:]
        if text[0].isupper() and text[:2] != 'X ':
            good = []
            bad = []
            for names in potential_names(text, selfnames):
                if all((name in _uname_from_name for name in names)):
                    good += [names]
                else:
                    bad += [names]
            if len(good) > 1:
                _logger.warning("Multiple name splits possible: {}."
                                .format("; ".join(map(str, good))))
            res = good and good[0] or bad and bad[0] or None
            if res:
                _logger.debug("Selected name(s) at position {} "
                              "as: {}".format(j, "; ".join(res)))
                line = (line[:j] + format_by_name(text, res))
                if len(res) == 1 and '"' not in line[:i] and not parentnames:
                    # Check for abilities granted
                    t = abil.search(line[j:])
                    if t:
                        m, n = t.regs[0]
                        # Created tokens don't get shortnames
                        line = (line[:m + j]
                               + preprocess_names(t.group(), (res[0],), selfnames)
                               + line[n + j:])
                        j += n
                change = True
            else:
                _logger.warning("Unable to interpret name(s) "
                                "at position {}: {}."
                                .format(j, text.split()[0]))
        match = name_ref.search(line, j)
    # Check for abilities granted to things that aren't named tokens
    # Luckily we do not need to consider matching names in abilities
    # granted in abilities granted
    # (eg. get an emblem with "creatures have 'T: this creature...'"
    # although we could replace 'this creature' with SELF...)
    abil_change = False
    if not parentnames:
        # Granting abilities to oneself vs granting abilities to something
        # else: how do we determine it? So far, all granted abilities are
        # from a) self-granting, b) creating tokens, c) enchanting/equipping.
        # d) 'each' effects like Torrent of Lava or Slivers.
        parentwords = ('equipped', 'enchanted', 'fortified', 'create', 'each')
        i = 0
        t = abil.search(line[i:])
        parent = False
        if t:
            m, _ = t.regs[0]
            parent = True
            # Instead of a greedy reverse search for a related word
            # split the phrase on "," and " and " and search each segment.
            segments = preprocess_cardname(line[:m], selfnames)[0].split(', ')
            segments[-1:] = segments[-1].split(' and ')
            for segment in reversed(segments):
                for w in segment.split():
                    if w in parentwords:
                        break
                    elif w == 'SELF':
                        parent = False
                        break
                else:
                    continue
                break
        while t:
            m, n = t.regs[0]
            if parent:
                mid, change = preprocess_cardname(t.group(), (), selfnames)
            else:
                mid, change = preprocess_cardname(t.group(), selfnames)
            line = (line[:m + i] + mid + line[n + i:])
            abil_change = abil_change or change
            i += n
            t = abil.search(line[i:])
    # CARDNAME processing occurs after the "named" processing
    line, cardname_change = preprocess_cardname(line, selfnames, parentnames)
    if abil_change:
        _logger.debug("Detected cardnames in an ability granted by {}: {}"
                    .format(selfnames[0], line))
    if change or cardname_change:
        sname = selfnames and selfnames[0] or "?.token"
        _logger.debug("Now: {} | {}".format(sname, line))
    return line
