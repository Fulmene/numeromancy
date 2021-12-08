parser grammar properties;

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

/* Rules for describing object properties. */

/*
 * We divide properties into three categories:
 * - adjectives
 * - nouns
 * - descriptors
 *
 * Nouns are the only required part of a set of subset properties
 * (except for the cases where an ability talks about having or being a
 *  property).
 * An adjective is any property that can't be used alone in a subset that
 * precede any nouns. For example, colors and tap status.
 * Descriptors are properties that can't be used alone in a subset that follow
 * any nouns. For example, "under your control" and "named X".
 *
 * Some of these items can be written as lists of two or more items joined
 * with a conjunction. However, only one "level" of a subset can be a list:
 * either adjectives (which can include nouns), nouns, a combination of
 * both adjectives and nouns, or all three together; the type of list is
 * generally determinable from the first item in the list.
 *
 * When a list occurs in either adjectives or nouns, the list is treated
 * as its own set of properties, joined with the other two categories.
 * The object must match each category for the object to match the whole set
 * of properties. For example, in "white or blue creature", "white or blue"
 * is an adjective list, and creature is a noun. An object must match "white
 * or blue" and "creature" to match this properties set.
 *
 * Note that the conjunction is likely to be misleading based on usage here.
 * Both "sacrifice a white or blue creature" and "white and blue creatures
 * have flying" reference a set of creatures with color(s) white and/or blue.
 * To be granted flying from the latter ability, a creature must be at least
 * one of white and blue; it does not have to be both. In other words, an
 * "and" in such a situation can be considered equivalent to "union". However,
 * "sacrifice a white and blue creature" uses it as "intersection"; here the
 * creature sacrificed must be both white and blue. Context is important.
 * In some cases, the text may instead read "a creature that's both white and
 * blue".
 */

// Property of cards or objects

property_ : adjectiveList? noun descriptorList?
          | nounList descriptorList?
          ;

// Adjectives

adjective : NON? ( supertype | cardType | subtype | objectType | typeSpec | color | colorSpec | status ) ;

adjectiveList : adjective+
              | adjective ( COMMA adjective )+
              | adjective ( ( COMMA adjective )+ COMMA )? conj adjective
              ;

// Nouns

noun : cardType | subtype | objectType ;

nounList : noun ( ( COMMA noun )+ COMMA )? conj noun ;

// Descriptors

descriptorList : descriptor ;

descriptor : nameDescriptor
           | playerDescriptor
           | zoneDescriptor
           | keywordDescriptor
           | THAT is_
             ( statusDescriptor
             | BOTH adjective AND adjective
             //| NOT ( desc_status | in_zones | ON spec_zone )
             )
           ;

nameDescriptor : NOT? NAMED REFBYNAME ;

playerDescriptor : playerSubset ( DO NOT )? ( CONTROL | OWN | CAST | BOTH? OWN conj CONTROL ) ;

zoneDescriptor : ( IN | FROM ) zoneSubset ;

keywordDescriptor : ( WITH | WITHOUT ) keywords ;

statusDescriptor : THAT is_ status ;

status : TAPPED
       | UNTAPPED
       | ENCHANTED
       | EQUIPPED
       | FORTIFIED
       | HAUNTED
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

// Card properties

color : WHITE | BLUE | BLACK | RED | GREEN ;
colorSpec : COLORED | COLORLESS | MONOCOLORED | MULTICOLORED ;

supertype : BASIC | LEGENDARY | SNOW | WORLD | ONGOING ;

cardType : permanentType | spellType | tribalType ;
permanentType : CREATURE | ARTIFACT | ENCHANTMENT | LAND | PLANESWALKER ;
spellType : INSTANT | SORCERY ;
tribalType : TRIBAL ;

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

typeSpec : HISTORIC ;

objectType : CARD | PERMANENT | SPELL | ABILITY | SOURCE | TOKEN ;

// Property names

propertyTypes : propertyType ( ( COMMA ( propertyType COMMA )+ )? conj propertyType )? ;

propertyType : COLOR
             | NAME
             | cardType TYPE
             | CARD? TYPE
             | intProp
             | costProp
             ;

intProp : MANA_VALUE
        | LIFE TOTAL?
        | POWER
        | TOUGHNESS
        ;

costProp : MANA COST
         | ( keywordCost | keywordIntCost | keywordQualityCost ) COST?
         ;
