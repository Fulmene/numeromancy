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

ability : (abilityWord MDASH)? abilityText ;

abilityText : spellEffect                                   // Static ability
            | cost COLON spellEffect activateCondition?     // Activated ability
            | (WHEN|AT) trigger COMMA spellEffect           // Triggered ability
            ;

activateCondition : ACTIVATE ONLY actCond PERIOD ;

actCond : AS A SORCERY
        | ONCE EACH TURN
        ;

grantedAbilityList : grantedAbility ( ( COMMA ( grantedAbility COMMA )+ )? conj grantedAbility )? ;

grantedAbility : keywordAbility
               | DQUOTE ability DQUOTE
               | SQUOTE ability SQUOTE
               ;

/* Spell effects */

spellEffect : sentence+ ;

sentence : atomicEffect ( ( COMMA atomicEffect )* COMMA (THEN|conj) atomicEffect )? ( COMMA varDef )? PERIOD;

atomicEffect : gameAction duration? fullCondition? ;
              // | duration COMMA gameAction -> ^(gameAction duration);

fullCondition : IF subset condition
              | UNLESS subset condition
              ;

gameAction : ( subset MAY? )? keywordActionList ;

keywordActionList : keywordAction ( ( COMMA ( keywordAction COMMA )+ )? conj keywordAction )? ;

keywordAction : verb=(ATTACH|UNATTACH) subset c=TO subset                               #keywordActionTwoSubsets
              | verb=CAST subset                                                        #keywordActionSubset
              | verb=COUNTER subset                                                     #keywordActionSubset
              | verb=CREATE token                                                       #keywordActionToken
              | verb=DISCARD subset                                                     #keywordActionSubset
              | verb=DRAW number CARD                                                   #keywordActionNumber
              | verb=DEAL number DAMAGE TO subset
                    ( ( COMMA ( number DAMAGE TO subset COMMA )+ )?
                    conj number DAMAGE TO subset )?                                     #keywordActionDamage
              | verb=DESTROY subset                                                     #keywordActionSubset
              // TODO | DOUBLE
              // TODO | EXCHANGE
              | verb=EXILE subset                                                       #keywordActionSubset
              | verb=FIGHT subset                                                       #keywordActionSubset
              | verb=MILL number CARD                                                   #keywordActionNumber
              | verb=PLAY subset                                                        #keywordActionSubset
              | verb=REGENERATE subset                                                  #keywordActionSubset
              | verb=REVEAL subset                                                      #keywordActionSubset
              | verb=SACRIFICE subset                                                   #keywordActionSubset
              | verb=SCRY number                                                        #keywordActionNumber
              | verb=SEARCH zoneSubset FOR subset                                       #keywordActionZone
              | verb=SHUFFLE                                                            #keywordActionIntransitive
              | verb=(TAP|UNTAP) subset                                                 #keywordActionSubset
              | verb=FATESEAL number                                                    #keywordActionNumber
              | verb=CLASH WITH subset                                                  #keywordActionSubset
              | verb=PROLIFERATE                                                        #keywordActionIntransitive
              | verb=TRANSFORM subset                                                   #keywordActionSubset
              | verb=DETAIN subset                                                      #keywordActionSubset
              | verb=POPULATE                                                           #keywordActionIntransitive
              | verb=MONSTROSITY number                                                 #keywordActionNumber
              | verb=BOLSTER number                                                     #keywordActionNumber
              | verb=MANIFEST subset                                                    #keywordActionSubset
              | verb=SUPPORT number                                                     #keywordActionNumber
              | verb=INVESTIGATE                                                        #keywordActionIntransitive
              | verb=MELD THEM INTO name=REFBYNAME                                      #keywordActionName
              | verb=GOAD subset                                                        #keywordActionSubset
              | verb=EXERT subset                                                       #keywordActionSubset
              | verb=EXPLORE                                                            #keywordActionIntransitive
              | verb=SURVEIL number                                                     #keywordActionNumber
              | verb=ADAPT number                                                       #keywordActionNumber
              | verb=AMASS number                                                       #keywordActionNumber
              | verb=LEARN                                                              #keywordActionIntransitive

              | GAIN verb=CONTROL OF subset                                             #keywordActionSubset
              | verb=(GAIN|LOSE) number LIFE                                            #keywordActionNumber
              | verb=(GAIN|HAVE) grantedAbilityList                                     #keywordActionAbility
              | verb=GET ptMod                                                          #keywordActionPT
              | verb=PUT counterSubset ON subset
                    ( ( COMMA ( counterSubset ON subset COMMA )+ )?
                    conj counterSubset ON subset )?                                     #keywordActionPutCounter
              | verb=PAY mana                                                           #keywordActionMana
              | verb=ADD mana                                                           #keywordActionMana
              | verb=(IS|BECOME) NOT? subset
                     (IN ADDITION TO refObjPoss OTHER propertyType)?                    #keywordActionBecome
              | verb=CHOOSE subset c=FROM subset                                        #keywordActionTwoSubsets
              | verb=PUT subset ONTO zoneSubset statusList?                             #keywordActionZone
              | verb=RETURN subset TO zoneSubset statusList?                            #keywordActionZone
              | verb=SHUFFLE subset INTO zoneSubset                                     #keywordActionZone
              | verb=(WIN|LOSE) THE GAME                                                #keywordActionIntransitive

              | verb=ENTER zoneSubset statusList? #aaa
              ;

/*
 // effect with condition

atomicEffect : subset DEAL number DAMAGE TO subset
             | gameAction
             | playerSubset player_action
             | player_action -> ^(YOU player_action)
             | staticAbility duration?
             ;

// Keyword actions that require a playerSubset as a subject. If the playerSubset is omitted, the default playerSubset is YOU.
player_action : SACRIFICE subset
             | GAIN number LIFE
             //| CREATE token
             | RETURN subset (FROM zone_subset)? TO player_poss HAND // possession?
             | PUT counterSubset ON subset
             | SHUFFLE subset INTO zone_subset
             // | GET A EMBLEM WITH '"' rulesText '"'
             | PAY mana
             | PUT subset (FROM zone_subset)? (INTO|ONTO|ON) zone_subset
             | ADD mana
             | DRAW number CARD
             | DISCARD number CARD
             | GAIN CONTROL OF subset
             | SEARCH zone_subset FOR subset
             | SCRY number
             | MILL number CARD
             | HAVE gameAction
             ;

// Other game actions
gameAction : DESTROY subset
           | EXILE subset
           | TAP subset
           | UNTAP subset
           | COUNTER subset
           | END THE TURN
           | subset BECOME subset // or become something else
           | subset FIGHT subset
           | subset PHASE OUT
           ;

staticAbility : condition (
                      spellMod
                    | permanentMod
                    | replacementEffect
                )
              ;

spellMod : AS A ADDITIONAL COST TO CAST subset COMMA cost PERIOD // -> COST_ADDITIONAL subset cost
         //| subset COST cost (MORE|LESS) TO CAST (FOR EACH number)? PERIOD -> COST_ADD|COST_REDUCTION subset cost number
         //| YOU MAY PAY cost RATHER THAN PAY subset MANA COST PERIOD -> COST_ALTERNATE subset cost
         ;

permanentMod : subset (GET pt) AND ((GAIN|HAVE) keywords) // TODO change this to ability
             //| subset CANT actions
             //| subset DO NOT UNTAP DURING player_poss UNTAP STEP
             ;

replacementEffect : IF subset WOULD gameAction COMMA gameAction INSTEAD PERIOD
                  ;
*/
