parser grammar subsets;

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

/* Rules for describing subsets of objects. */

subsets : subset_list
        | mini_sub ( ( COMMA ( mini_sub COMMA )+ )? conj mini_sub )?
        ;

subset_list : subset ( options {greedy=true;}:
                       ( COMMA ( subset COMMA )+ )? conj subset )? ;

subset : number mini_sub ( ( COMMA ( mini_sub COMMA )+ )? conj mini_sub )?
       | number OTHER mini_sub
       | AMONG mini_sub
       | ANOTHER mini_sub
       | THE LAST mini_sub
       | full_zone
       | haunted_object
       | ref_object in_zones?
       | player_group
       ;

mini_sub : properties restriction* ;

// A full zone, for use as a subset
full_zone : player_poss ind_zone
          | THE ( TOP | BOTTOM ) number? properties OF player_poss ( LIBRARY | GRAVEYARD )
          ;

// Restrictions are very similar to descriptors, but can reference properties.
restriction : WITH has_counters
            | WITH int_prop_with_value
            | share_feature
            | WITH n_distinct_values
            | WITH total_int_prop
            | other_than
            | except_for
            | attached_to
            | chosen_prop
            | not_chosen_prop
            | from_expansion
            | linked_ref
            ;

// TODO: 'choose a creature type other than wall'. This may go elsewhere.
other_than : OTHER THAN
             ( ref_object
             | A? properties
             | zone_subset
             );

// TODO: "except for creatures the player hasn't controlled continuously
//        since the beginning of the turn".
// put in descriptors? putting "...hasn't controlled" in restriction would
// require except_for to not be in restriction.
except_for : COMMA? EXCEPT FOR ( ref_object | properties );

attached_to : ATTACHED TO ( ref_object | properties ) ;

chosen_prop : ( OF | WITH ) THE CHOSEN prop_type ;

not_chosen_prop : THAT IS NOT
                  ( chosen_prop
                  | OF A prop_type CHOSEN THIS WAY
                  | THE NAMED CARD
                  )
                ;

from_expansion : FROM THE expansion EXPANSION ;

expansion : ANTIQUITIES
          | ARABIAN_NIGHTS
          | HOMELANDS
          ;

linked_ref : CHAMPIONED WITH SELF
           | EXILED WITH SELF
           | PUT ONTO THE BATTLEFIELD WITH SELF
           ;

/* Special properties, usually led by 'with', 'that', or 'if it has' */

// Do we need to remember ref_object?
has_counters : counter_subset ON ref_object
             ;

share_feature : THAT SHARE A prop_type
              | WITH THE SAME prop_type
              ;

n_distinct_values : integer DIFFERENT prop_type;

total_int_prop : TOTAL int_prop_with_value ;

prop_with_value : int_prop_with_value ;

int_prop_with_value : CONVERTED MANA COST comparison
                    | integer LIFE
                    | LIFE comparison
                    | POWER comparison
                    | TOUGHNESS comparison;
