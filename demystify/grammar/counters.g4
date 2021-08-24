parser grammar counters;

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

/* Rules related to counters. */

/* Counter subsets. */

counterSubset : counterGroup ( ( COMMA ( counterGroup COMMA )+ )? conj counterGroup )? ;

counterGroup : number baseCounter ;

baseCounterSet : baseCounter ( ( COMMA ( baseCounter COMMA )+ )? conj baseCounter )? ;

baseCounter : ( objCounter | pt )? COUNTER ;

objCounter : OBJ_COUNTER
           | DEATH
           | DEVOTION
           | ECHO
           | EGG
           | FEATHER
           | FUNGUS
           | FUSE
           | LEVEL
           | LOYALTY
           | MINE
           | POISON
           | TIME
           | TOWER
           | TRAP
           | TREASURE
           ;
