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

ability : spellEffect                  // Static ability
        | cost COLON spellEffect       // Activated ability
        | trigger COMMA spellEffect    // Triggered ability
        ;

/* Spell effects */

spellEffect : (atomicEffect PERIOD)+;

atomicEffect : gameAction duration? fullCondition? ;
              // | duration COMMA gameAction -> ^(gameAction duration);

fullCondition : IF subsetList condition
               | UNLESS subsetList condition
               ;

gameAction : ( subsetList MAY? )? keywordAction ;
            //| game_object_action

//player_action : ( playerSubset MAY? )? player_keywordAction ;
//game_object_action : subsetList game_object_keywordAction ;

keywordAction : verb=(ATTACH|UNATTACH) subsetList conj=TO subsetList                        #keywordActionTwoSubsets
              | verb=CAST subsetList                                                        #keywordActionSubset
              | verb=COUNTER subsetList                                                     #keywordActionSubset
              // TODO | CREATE token
              | verb=DISCARD subsetList                                                     #keywordActionSubset
              | verb=DRAW number CARD                                                       #keywordActionNumber
              | verb=DEAL number DAMAGE TO subsetList                                       #keywordActionDamage
              | verb=DESTROY subsetList                                                     #keywordActionSubset
              // TODO | DOUBLE
              // TODO | EXCHANGE
              | verb=EXILE subsetList                                                       #keywordActionSubset
              | verb=FIGHT subsetList                                                       #keywordActionSubset
              | verb=MILL number CARD                                                       #keywordActionNumber
              | verb=PLAY subsetList                                                        #keywordActionSubset
              | verb=REGENERATE subsetList                                                  #keywordActionSubset
              | verb=REVEAL subsetList                                                      #keywordActionSubset
              | verb=SACRIFICE subsetList                                                   #keywordActionSubset
              | verb=SCRY number                                                            #keywordActionNumber
              // TODO | SEARCH
              // TODO | SHUFFLE
              | verb=(TAP|UNTAP) subsetList                                                 #keywordActionSubset
              | verb=FATESEAL number                                                        #keywordActionNumber
              | verb=CLASH WITH subsetList                                                  #keywordActionSubset
              | verb=PROLIFERATE                                                            #keywordActionIntransitive
              | verb=TRANSFORM subsetList                                                   #keywordActionSubset
              | verb=DETAIN subsetList                                                      #keywordActionSubset
              | verb=POPULATE                                                               #keywordActionIntransitive
              | verb=MONSTROSITY number                                                     #keywordActionNumber
              | verb=BOLSTER number                                                         #keywordActionNumber
              | verb=MANIFEST subsetList                                                    #keywordActionSubset
              | verb=SUPPORT number                                                         #keywordActionNumber
              | verb=INVESTIGATE                                                            #keywordActionIntransitive
              | verb=MELD THEM INTO name=REFBYNAME                                          #keywordActionName
              | verb=GOAD subsetList                                                        #keywordActionSubset
              | verb=EXERT subsetList                                                       #keywordActionSubset
              | verb=EXPLORE                                                                #keywordActionIntransitive
              | verb=SURVEIL number                                                         #keywordActionNumber
              | verb=ADAPT number                                                           #keywordActionNumber
              | verb=AMASS number                                                           #keywordActionNumber
              | verb=LEARN                                                                  #keywordActionIntransitive

              | GAIN verb=CONTROL OF subsetList                                             #keywordActionSubset
              | verb=(GAIN|LOSE) number LIFE                                                #keywordActionNumber
              // TODO | GAIN ability
              | verb=GET ptMod                                                              #keywordActionPT
              | verb=PUT counterSubset ON subsetList                                        #keywordActionPutCounter
              | verb=PAY mana                                                               #keywordActionMana
              | verb=ADD mana                                                               #keywordActionMana
              | verb=(IS|BECOME) subsetList (IN ADDITION TO refObjPoss OTHER propertyType)? #keywordActionBecome
              | verb=CHOOSE subsetList conj=FROM subsetList                                 #keywordActionTwoSubsets
              // TODO | RETURN subsetList TO 
              | verb=(WIN|LOSE) THE GAME                                                    #keywordActionIntransitive
              ;

/*
 // effect with condition

atomicEffect : subsetList DEAL number DAMAGE TO subsetList
             | gameAction
             | playerSubset player_action
             | player_action -> ^(YOU player_action)
             | staticAbility duration?
             ;

// Keyword actions that require a playerSubset as a subject. If the playerSubset is omitted, the default playerSubset is YOU.
player_action : SACRIFICE subsetList
             | GAIN number LIFE
             //| CREATE token
             | RETURN subsetList (FROM zone_subset)? TO player_poss HAND // possession?
             | PUT counterSubset ON subsetList
             | SHUFFLE subsetList INTO zone_subset
             // | GET A EMBLEM WITH '"' rulesText '"'
             | PAY mana
             | PUT subsetList (FROM zone_subset)? (INTO|ONTO|ON) zone_subset
             | ADD mana
             | DRAW number CARD
             | DISCARD number CARD
             | GAIN CONTROL OF subsetList
             | SEARCH zone_subset FOR subsetList
             | SCRY number
             | MILL number CARD
             | HAVE gameAction
             ;

// Other game actions
gameAction : DESTROY subsetList
           | EXILE subsetList
           | TAP subsetList
           | UNTAP subsetList
           | COUNTER subsetList
           | END THE TURN
           | subsetList BECOME subsetList // or become something else
           | subset FIGHT subset
           | subset PHASE OUT
           ;

staticAbility : condition (
                      spellMod
                    | permanentMod
                    | replacementEffect
                )
              ;

spellMod : AS A ADDITIONAL COST TO CAST subsetList COMMA cost PERIOD // -> COST_ADDITIONAL subsetList cost
         //| subsetList COST cost (MORE|LESS) TO CAST (FOR EACH number)? PERIOD -> COST_ADD|COST_REDUCTION subsetList cost number
         //| YOU MAY PAY cost RATHER THAN PAY subsetList MANA COST PERIOD -> COST_ALTERNATE subsetList cost
         ;

permanentMod : subsetList (GET pt) AND ((GAIN|HAVE) keywords) // TODO change this to ability
             //| subsetList CANT actions
             //| subsetList DO NOT UNTAP DURING player_poss UNTAP STEP
             ;

replacementEffect : IF subsetList WOULD gameAction COMMA gameAction INSTEAD PERIOD
                  ;
*/
