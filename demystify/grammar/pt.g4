parser grammar pt;

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

/* Power/toughness */

// This rule is used for printed p/t, p/t setting abilities,
// and p/t modifying abilities.

pt : ptPart SLASH ptPart ;

ptMod : ptPartSigned SLASH ptPartSigned ;

ptPart : NUMBER_SYM
       | VAR_SYM
       | STAR_SYM
       | NUMBER_SYM ( PLUS_SYM | MINUS_SYM ) STAR_SYM
       ;

ptPartSigned : ( PLUS_SYM | MINUS_SYM ) ( NUMBER_SYM | VAR_SYM ) ;
