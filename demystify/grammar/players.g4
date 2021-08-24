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

playerSubsets : playerSubset ( ( ( COMMA playerSubset )+ COMMA)? conj playerSubset )? ;

playerSubset : ( quantity OF )? playerPoss ( OPPONENT )
             | quantity player
             | refPlayer
             ;

playerPoss : refPlayerPoss ( player poss )? ;

refPlayerPoss : THEIR
              | YOUR
              | refPlayer poss
              ;

refPlayer : refObjPoss ( OWNER | CONTROLLER )
          | ( THAT | THOSE ) player
          | ( CHOSEN | ENCHANTED ) player
          | DEFENDING PLAYER
          | YOU
          ;

// Player types

playerType : PLAYER | OPPONENT | CONTROLLER | OWNER | BIDDER ;

player : OPPONENT
       | PLAYER
       ;
