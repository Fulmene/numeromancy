parser grammar players;

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

/* Players, controllers, and owners. */

player_subset : player_group ( conj player_group )? ;

// TODO: objects can have controllers and/or owners
// TODO: Handle 'that player' etc refs differently?
player_group : ( number OF )? player_poss ( OPPONENT | TEAMMATE )
             | number player_base
             | THAT player_base
             | ( CHOSEN | ENCHANTED )? player_base
             | ( ACTIVE | DEFENDING ) PLAYER
             | ANOTHER PLAYER
             | YOU
             | ref_player
             ;

player_poss : YOUR
            | ( THAT | THOSE ) player_base poss
            | player_base poss
            | ref_player_poss ( player_base poss )?
            ;

ref_player_poss : HIS OR HER
                | THEIR
                | ref_player poss
                ;

ref_player : ref_obj_poss ( OWNER | CONTROLLER )
           ;

player_base : OPPONENT
            | TEAMMATE
            | PLAYER
            ;
