grammar Demystify;

// This file is part of Demystify.
// 
// Demystify: a Magic: The Gathering parser
// Copyright (C) 2012 Benjamin S Wolf
// 
// Demystify is free software; you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation; either version 3 of the License,
// or (at your option) any later version.
// 
// Demystify is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with Demystify.  If not, see <http://www.gnu.org/licenses/>.

/* Top-level grammar for Demystify. */

options {
    language = Python3;
}

// Order is absurdly relevant. eg. subsets invokes rules in zones,
// hence zones must be imported after so that antlr can correctly
// generate lookahead code for it. This is mostly necessary for rules with
// optional or repeated parts, where LL(1) can't correctly predict which rule
// to use to parse the next tokens. See the graph output from deps.py.
// Note further that rules in *this* file are handled as if imported last.
import Words, effects, duration, math, events, keywordAbilities, subsets, costs, properties, counters, zones, players, misc, keywords, pt, macro;

tokens {
    ADD_COUNTERS,
    ATTACHED_TO,
    CMC,
    COINFLIP,
    CONDITION,
    COUNTER_GROUP,
    COUNTER_SET,
    ENERGY,
    EVENT,
    GEQ,
    GT,
    HAS_COUNTERS,
    INT,
    KEYWORDS,
    LEQ,
    LINKED,
    LT,
    MAX,
    MOVE_TO,
    MULT,
    NONCOMBAT,
    NTH,
    PAY_COST,
    PAY_LIFE,
    PAY_PER,
    PER,
    PLAYER_GROUP,
    POSS,
    PROPERTIES,
    PT,
    REMOVE_COUNTERS,
    SUBSET,
    SUBTYPES,
    SUPERTYPES,
    TYPELINE,
    TYPES,
    VAR,
    ZONE_SET
}

cardManaCost : mana;

typeline : supertype* cardType+ ( MDASH subtype+ )? ;

rulesText : line+ ;

line : keywordLine
     | ability
     ;

// Literals used in parsing rules don't have to be declared,
// but for reference they are:
// ,:;."'+-*/

COMMA : ',';
COLON : ':';
SEMICOLON : ';';
PERIOD : '.';
DQUOTE : '"';
SQUOTE : '\'';
PLUS_SYM : '+';
MINUS_SYM : '-';
STAR_SYM : '*';
SLASH : '/';
LBRACKET : '[';
RBRACKET : ']';
