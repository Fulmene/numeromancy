parser grammar keywords;

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

/* Keywords, in the official Magic parlance. */

/* For the purposes of this file, there are three types of keywords:
 *
 * Keyword actions, which are verbs used in sentences (aside from some
 *   ubiquitous keyword actions used elsewhere in this grammar).
 * Listable keywords, which are usually placed at the top of the card in a
 *   list, though they don't have to be (e.g. when reminder text is included).
 * Standalone keywords, which must go on their own line.
 *
 * These appear generally in a form containing some fixed text
 * relating to the keyword and 0-2 arguments, each of which is either
 * an integer, a cost, or a quality.
 *
 * For example:
 *   Suspend (number) -- (cost)
 *   (quality)cycling
 *   Protection from (quality)
 *   (quality)walk
 *
 * Keywords may also appear in a fixed short form for when abilities grant
 * keyword abilities, remove keyword abilities, or make reference to objects
 * having keyword abilities.
 */

keywordLine : keywordAbility ( ( COMMA | SEMICOLON ) keywordAbility )* ;

keywordAbility : keywordAbilityNoArgs
               | keywordAbilityInt
               | keywordAbilityCost
               | keywordAbilityIntCost
               | keywordAbilityQuality
               | keywordAbilityQualityCost
               ;

keywordAbilityNoArgs : keywordNoArgs;

keywordAbilityInt : keywordInt keywordArgInt;

keywordAbilityCost : keywordCost keywordArgCost;

keywordAbilityIntCost : keywordIntCost KeywordArgInt keywordArgCost;

keywordAbilityQuality : keywordAbilityEnchant
                      | keywordAbilityHexproof
                      | keywordAbilityProtection
                      | keywordAbilityAffinity
                      | keywordAbilityBandsWithOther
                      | keywordAbilityChampion
                      | keywordAbilityLandwalk
                      | keywordAbilityOffering
                      ;

keywordAbilityQualityCost : keywordAbilityEquipQuality
                          | keywordAbilitySplice
                          | keywordAbilityTypecyling
                          ;

/* Special case keywords. */

keywordAbilityEnchant : ENCHANT keywordArgQuality ;

keywordAbilityHexproof : HEXPROOF
                         ( FROM keywordArgQuality
                             ( ( COMMA ( FROM keywordArgQuality COMMA )+ )?
                                 AND FROM keywordArgQuality )? )? ;

keywordAbilityProtection : PROTECTION FROM keywordArgQuality
                           ( ( COMMA ( FROM keywordArgQuality COMMA )+ )?
                               AND FROM keywordArgQuality )? ;

keywordAbilityAffinity : AFFINITY FOR keywordArgQuality ;

keywordAbilityBandsWithOther : BAND WITH OTHER keywordArgQuality ;

keywordAbilityChampion : CHAMPION A keywordArgQuality ;

keywordAbilityLandwalk : keywordArgQuality WALK
                       | keywordArgQuality LANDWALK
                       ;

keywordAbilityOffering : keywordArgQuality OFFERING ;

keywordAbilityEquipQuality : EQUIP keywordArgQuality keywordArgCost ;

keywordAbilitySplice : SPLICE ONTO keywordArgQuality keywordArgCost ;

keywordAbilityTypecyling : keywordArgQuality CYCLING keywordArgCost ;

/* Argument rules. */

keywordArgInt : NUMBER_SYM
              | VAR_SYM ( COMMA varDef)? ;
              | MDASH SUNBURST
              ;

// Costs can include standard cost items, plus some new ones:
// "Gain control of a land you don't control"
// "Put [creatures] onto the battlefield under an opponent's control."
// "Add [mana] to your mana pool."
// "Flip a coin."
// "An opponent gains [life]."
// "Draw a card."
// in general many actions can be keyword costs like this. These are all
// cumulative upkeep costs; the gain life one appears in splice as well.
// The general idea is that it's a drawback, or in the case of cumulative
// upkeep, finite or dangerous.
// eg. "gain a poison counter" could work.
// TODO: Add these new cost items.
keywordArgCost : MDASH? cost;

// TODO: better distinguish quality args.
//       (eg. typecycling takes only simple_properties,
//            protection takes this, and enchant takes properties)

// Quality can include generic properties as well as other special qualities
// as in "protection from everything" or "protection from all colors".
// More than that, it can include adjectives on their own.
keywordArgQuality : subsets ;
