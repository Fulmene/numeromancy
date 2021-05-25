parser grammar effects;

// This file is part of Demystify.
// 
// Demystify: a Magic: The Gathering parser
// Copyright (C) 2021 Ada Joule
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

/* Spell effects */

spell_effect : sentence+;

sentence : atomic_effect PERIOD!;

atomic_effect : game_action duration? full_condition? -> ^(EFFECT game_action duration? full_condition?);
              // | duration COMMA game_action -> ^(game_action duration);

full_condition : IF subsets condition -> ^(IF subsets condition)
               | UNLESS subsets condition -> ^(UNLESS subsets condition)
               ;

game_action : ( subsets MAY? )? keyword_action -> ^(ACTION subsets? MAY? keyword_action);
            //| game_object_action

//player_action : ( player_subset MAY? )? player_keyword_action ;
//game_object_action : subsets game_object_keyword_action ;

keyword_action : (ATTACH|UNATTACH) subsets TO subsets
               | CAST subsets
               | COUNTER subsets
               // TODO | CREATE token
               | DISCARD subsets
               | DRAW number CARD
               | DEAL number DAMAGE TO subsets -> ^(DAMAGE number subsets)
               | DESTROY subsets
               // TODO | DOUBLE
               // TODO | EXCHANGE
               | EXILE subsets
               | FIGHT subsets
               | MILL number CARD
               | PLAY subsets
               | REGENERATE subsets
               | REVEAL subsets
               | SACRIFICE subsets
               | SCRY number
               // TODO | SEARCH
               // TODO | SHUFFLE
               | (TAP|UNTAP) subsets
               | FATESEAL number
               | CLASH WITH player_subset
               | PROLIFERATE
               | TRANSFORM subsets
               | DETAIN subsets
               | POPULATE
               | MONSTROSITY number
               | BOLSTER number
               | MANIFEST subsets
               | SUPPORT number
               | INVESTIGATE
               | MELD subsets INTO subsets // Would this need to be more specific?
               | GOAD subsets
               | EXERT subsets
               | EXPLORE
               | SURVEIL number
               | ADAPT number
               | AMASS number
               | LEARN

               | GAIN CONTROL OF subsets
               | (GAIN|LOSE) number LIFE
               // TODO | GAIN ability
               | GET pt
               | PUT counter_subset ON subsets
               | PAY mana
               | ADD mana
               | IS subsets // Nonbasic lands are mountains
               | BECOME subsets // TODO in addition
               | CHOOSE subsets FROM subsets // You choose a nonland card from it
               // TODO | RETURN subsets TO 
               | (WIN|LOSE) THE GAME
               ;

/*
 // effect with condition

atomicEffect : subsets DEAL number DAMAGE TO subsets
             | game_action
             | player_subset player_action
             | player_action -> ^(YOU player_action)
             | staticAbility duration?
             ;

// Keyword actions that require a player_subset as a subject. If the player_subset is omitted, the default player_subset is YOU.
player_action : SACRIFICE subsets
             | GAIN number LIFE
             //| CREATE token
             | RETURN subsets (FROM zone_subset)? TO player_poss HAND // possession?
             | PUT counter_subset ON subsets
             | SHUFFLE subsets INTO zone_subset
             // | GET A EMBLEM WITH '"' rulesText '"'
             | PAY mana
             | PUT subsets (FROM zone_subset)? (INTO|ONTO|ON) zone_subset
             | ADD mana
             | DRAW number CARD
             | DISCARD number CARD
             | GAIN CONTROL OF subsets
             | SEARCH zone_subset FOR subsets
             | SCRY number
             | MILL number CARD
             | HAVE game_action
             ;

// Other game actions
game_action : DESTROY subsets
           | EXILE subsets
           | TAP subsets
           | UNTAP subsets
           | COUNTER subsets
           | END THE TURN
           | subsets BECOME subsets // or become something else
           | subset FIGHT subset
           | subset PHASE OUT
           ;

staticAbility : condition (
                      spellMod
                    | permanentMod
                    | replacementEffect
                )
              ;

spellMod : AS A ADDITIONAL COST TO CAST subsets COMMA cost PERIOD // -> COST_ADDITIONAL subsets cost
         //| subsets COST cost (MORE|LESS) TO CAST (FOR EACH number)? PERIOD -> COST_ADD|COST_REDUCTION subsets cost number
         //| YOU MAY PAY cost RATHER THAN PAY subsets MANA COST PERIOD -> COST_ALTERNATE subsets cost
         ;

permanentMod : subsets (GET pt) AND ((GAIN|HAVE) keywords) // TODO change this to ability
             //| subsets CANT actions
             //| subsets DO NOT UNTAP DURING player_poss UNTAP STEP
             ;

replacementEffect : IF subsets WOULD game_action COMMA game_action INSTEAD PERIOD
                  ;
*/
