parser grammar cardTypes;

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

/* Common object properties, such as types, colors, and statuses. */

adj_list : a=adjective ( COMMA ( ( b+=adjective | c+=noun ) COMMA )+ )?
           conj ( d=adjective | e=noun ) // Currently only Soldevi Adnate?
         ;

noun_list : noun ( COMMA ( noun COMMA )+ )? conj noun ;

// Adjectives

adjective : NON? ( supertype | color | colorSpec | status ) ;

color : WHITE | BLUE | BLACK | RED | GREEN ;
colorSpec : COLORED | COLORLESS | MONOCOLORED | MULTICOLORED ;
status : TAPPED
       | UNTAPPED
       | EXILED
       | KICKED
       | SUSPENDED
       | ATTACKING
       | BLOCKING
       | BLOCKED
       | UNBLOCKED
       | FACE_UP
       | FACE_DOWN
       | FLIPPED
       | REVEALED
       | MONSTROUS
       ;

// Nouns

noun : NON? ( card_type | obj_subtype | obj_type ) ;

/* Types, supertypes, subtypes, and other miscellaneous types. */

// For use parsing a full typeline.
typeline : supertypes? card_types ( MDASH subtypes )? ;

supertypes : supertype+ ;

supertype : BASIC | LEGENDARY | SNOW | WORLD | ONGOING ;

// Card types

cardTypes : cardType+ ;

cardType : permanentType | spellType | tribalType ;

permanentType : CREATURE | ARTIFACT | ENCHANTMENT | LAND | PLANESWALKER ;

spellType : INSTANT | SORCERY ;

tribalType : TRIBAL ;

// subtypes
subtypes : subtype+ ;

subtype : OBJ_SUBTYPE
        | AURA
        | BOLAS
        | DRAGONS
        | EGG
        | FUNGUS
        | MINE
        | PHYREXIA
        | TOWER
        | TRAP
        | TREASURE
        | WILL
        ;

// Object types

objectType : CARD | PERMANENT | SPELL | ABILITY | SOURCE | TOKEN ;

/* Power/toughness */

// This rule is used for printed p/t, p/t setting abilities,
// and p/t modifying abilities.

pt : ptPart SLASH ptPart ;

ptMod : ptPartSigned SLASH ptPartSigned ;

ptPartSigned : ( PLUS_SYM | MINUS_SYM ) ( NUMBER_SYM | VAR_SYM ) ;

ptPart : NUMBER_SYM
       | VAR_SYM
       | STAR_SYM
       | NUMBER_SYM ( PLUS_SYM | MINUS_SYM ) STAR_SYM
       ;
