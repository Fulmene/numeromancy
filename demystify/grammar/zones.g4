parser grammar zones;

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

/* Zones. */

zoneSubset : playerPoss zoneList
           | number OF? playerPoss? zoneList
           | zoneList
           | specificZone
           ;

// This currently allows for only 1-3 zones, since there are at most
// three possible zones in such a list.
zoneList : pileZone ( ( COMMA pileZone COMMA )? conj pileZone )? ;

// These zones are player-specific so must be generally prefaced with
// player_poss or number. If not, it is usually for constructs such as
// "graveyards" where there is an implicit "all".
pileZone : GRAVEYARD
         | HAND
         | LIBRARY
         ;

// specific zones
specificZone : THE BATTLEFIELD
             | THE STACK
             | THE ( TOP | BOTTOM ) OF playerPoss LIBRARY
             | EXILE
             ;

zoneDescriptor : IN playerPoss pileZone
               | player OWN IN EXILE
               | ON THE specificZone
               ;

// While exile is a zone, cards in it are referred to as exiled cards,
// and not cards in exile, hence no zone rules are necessary for it.
// This is true except that cards may be moved "from exile".

// TODO: Command zone?
