parser grammar events;

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

/* Events and conditions. */

triggers : trigger ( OR trigger )? triggerDescriptor?;

// Although it doesn't look great, it was necessary to factor 'subset' out
// of the event and condition rules. It's a bad idea to leave it unfactored
// since ANTLR will run itself out of memory (presumably trying to generate
// lookahead tables).
trigger : subset
          ( event ( OR event )?
          | condition
          )
        | nonSubsetEvent
        | non_subset_condition
        ;

trigger : event ( COMMA IF condition )?
        | condition
        ;

// An event is something that happens, usually an object taking an action
// or having an action done to it.

event : zone_transfer
      | cause_transfer
      | phases_in_out
      | state_change
      | cost_paid
      | attack_with_stuff
      | cast_spell
      | clash_happens
      | coin_flip
      | counter_spell
      | cycle_card
      | deal_damage
      | dealt_damage
      | dies_damaged
      | discard_card
      | draw_card
      | EXPLORE  // intransitive verb
      | gain_life
      | kick_stuff
      | lose_control
      | lose_life
      | lose_the_game
      | play_stuff
      | sacrifice_stuff
      | shuffle_library
      | tap_stuff
      | is_tapped
      ;

/* Events. */

zone_transfer : ( ENTER | ( is_ ( PUT ( INTO | ONTO ) | RETURNED TO ) ) ) zoneSubset ( FROM ( zoneSubset | ANYWHERE ) )?
              | LEAVE zoneSubset
              | DIE
              ;

cause_transfer : PUT subset ( INTO | ONTO ) zoneSubset ( FROM ( zoneSubset | ANYWHERE ) )? ;

phases_in_out : PHASE ( IN | OUT );

state_change : BECOME ( BLOCKED BY subset
                      | status
                      | THE TARGET OF subset
                      | UNATTACHED FROM subset
                      )
             | ATTACK ( subset | ALONE )? ( AND IS NOT BLOCKED )?
             | BLOCK ( subset | ALONE )?
             | is_ TURNED status
             ;

cost_paid : poss costProp IS NOT? PAID
          | ( DO NOT )? PAY ( A | subset poss ) costProp
          ;

attack_with_stuff : ATTACK WITH subset ;

// TODO: Collect alike verbs together into one rule?
cast_spell : CAST subset ;

clash_happens : CLASH AND ( WIN | LOSE )
              | CLASH
              ;

coin_flip : FLIP A COIN
          | ( LOSE | WIN ) A COIN FLIP
          ;

counter_spell : COUNTER subset ;

cycle_card : CYCLE subset
           | CYCLE OR DISCARD subset ;

deal_damage : DEAL number? damage ( TO subset )? ;

dealt_damage : is_ DEALT number? damage ( BY subset )? ;

dies_damaged : DEALT damage BY subset THIS TURN DIE ;

discard_card : DISCARD subset ;

draw_card : DRAW A CARD ;

gain_life : GAIN number? LIFE ;

kick_stuff : KICK subset ;

lose_control : LOSE CONTROL OF subset ;

lose_life : LOSE number? LIFE ;

lose_the_game : LOSE THE GAME ;

play_stuff : PLAY subset ;

sacrifice_stuff : SACRIFICE subset ;

shuffle_library : SHUFFLE playerPoss LIBRARY ;

tap_stuff : TAP subset ( FOR MANA )? ;

is_tapped : is_ TAPPED FOR MANA ;

// A condition is a true-or-false statement about the game state. These
// types of triggered abilities (sometimes called "state triggers") will
// trigger any time that statement is true and it isn't already on the stack.
// Since otherwise this would lead to a mandatory loop, the effects of these
// triggered conditions usually serve to end the game or change the relevant
// state (e.g. 'when SELF has flying, sacrifice it').

condition : has_status
          | has_ability
          | has_cards
          | have_life
          //| HAVE has_counters
          | int_prop_is
          | control_stuff
          | is_somewhere
          ;

/* Conditions. */

has_status : HAVE THE CITYS_BLESSING;

has_ability : HAVE keyword ;

has_cards : HAVE number CARD IN HAND ;

have_life : HAVE number LIFE ;

int_prop_is : poss intProp IS number ;

control_stuff : CONTROL subset ;

is_somewhere : is_ ( IN | ON ) ;

// Some triggers do not start with subset, eg. "there are",
// "a counter is" or "the chosen color is".
nonSubsetEvent : counter_changed
                 | damage_dealt
                 ;

non_subset_condition : there_are
                     | there_counters
                     ;

/* Non-subset events. */

counter_changed : ( THE ordinalWord | number )
                  baseCounter is_
                  ( REMOVED FROM subset
                  | PUT ON subset
                  );

damage_dealt : number? damage is_ DEALT TO subset ;

/* Non-subset conditions. */

there_are : THERE is_ number subset ;

there_counters : THERE is_ counterSubset ON subset ;

// A trigger descriptor is an additional check that comes after the event
// triggers and conditions. Some of these may be (or include) conditions.
triggerDescriptor : while_condition
                  | during_turn
                  | during_step
                  | nth_time_per_turn
                  | THIS TURN
                  ;

while_condition : WHILE refObject ( condition | is_ status )
                | WHILE non_subset_condition
                ;

during_turn : DURING playerPoss TURN ;

// TODO: Other steps.
during_step : DURING COMBAT ;

nth_time_per_turn : FOR THE ordinalWord TIME THIS TURN ;
