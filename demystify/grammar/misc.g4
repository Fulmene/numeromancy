parser grammar misc;

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

/* Miscellaneous rules. */

// TODO Nuke this file and move everything to their respective domains

/* Special references to related objects. */

// TODO: target
refObject : SELF
          | PARENT
          | IT
          | THEM
          // planeswalker pronouns
          | HIM
          | HER
          // We probably don't actually need to remember what the
          // nouns were here, but keep them in for now.
          | ( ENCHANTED | EQUIPPED | FORTIFIED ) noun+
          | thisRef
          | thatRef
          ;

refObjPoss : SELF APOS_S
           | PARENT APOS_S
           | ITS
           | THEIR
           // planeswalker pronouns
           | HIS
           | HER
           | ( ENCHANTED | EQUIPPED | FORTIFIED ) noun+ poss
           | thisRef poss
           | thatRef poss
           ;

// eg. this creature, this permanent, this spell.
thisRef : THIS ( cardType | objectType ) ;

thatRef : (THAT | THOSE) ( cardType | objectType | subtype ) ;

/* Others */

conj : AND | OR | AND_OR ;

damage : ( NON? COMBAT )? DAMAGE ;

// Unfortunately we can't have the lexer rule match just a single quote
// in some cases but not others, so we use a parser rule to handle this.
// Note that the lexer will never match S_APOS since S will be part of
// the preceding token, so APOS_S | SQUOTE is all that's necessary.
poss : APOS_S | SQUOTE ;

// Similarly, APOS_S sometimes means "is".
is_ : IS | APOS_S ;
