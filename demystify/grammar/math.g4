parser grammar math;

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

/* Mathematical constructs and calculations. */

/* Numbers and quantities. */

quantity : number ( ( ( COMMA number )+ COMMA )? conj number )?
         | number OR ( MORE_ | GREATER )
         | number OR ( LESS | FEWER )
         | EXACTLY number
         | NO? ( MORE_ | GREATER ) THAN number
         | UP TO number
         | AT LEAST number
         | ( ALL | EACH | EVERY )
         | ANY number?
         | ANY AMOUNT OF
         | A SINGLE?
         | A ordinalWord
         | ANOTHER
         | NO
         ;

number : NUMBER_SYM | VAR_SYM | NUMBER_WORD | A ;

varDef : WHERE VAR_SYM IS quantity ;

/*
comparison : ( EQUAL TO OR )? ( MORE_ | GREATER ) THAN mtgNumber
           | ( FEWER | LESS ) THAN ( OR EQUAL TO )? mtgNumber
           | EQUAL TO mtgNumber
           | integer
           ;

mtgNumber : integer
          | object_count
          | max_among
          | that_ref poss int_prop
          ;

object_count : THE NUMBER OF 
               ( DIFFERENTLY NAMED properties
               | properties
               | base_counter_set ( ON ( properties | ref_object )
                                  | player_group HAS )
               );

// ref_object is usually plural in this case
max_among : THE ( HIGHEST | GREATEST ) int_prop
            AMONG ( properties | ref_object | player_group )
          ;

// TODO: for each basic land type among lands you control. (Draco)
for_each : FOR EACH
           ( properties
           | base_counter_set ( ON ( properties | ref_object )
                              | player_group HAS )
           );

multiplier : TWICE
           | NUMBER_WORD TIMES
           ;

divisor : HALF
        | ordinalWord
        ;
*/
