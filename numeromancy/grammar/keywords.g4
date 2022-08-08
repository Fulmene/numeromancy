parser grammar keywords;

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

/* Raw keyword definitions, for references within other abilities. */

keywords : keyword ( ( COMMA ( keyword COMMA )+ )? conj keyword )? ;

keyword : keywordNoArgs
        | keywordInt
        | keywordCost
        | keywordIntCost
        | keywordQuality
        | keywordQualityCost
        ;

// The lists of raw_keyword_(.*) below are for the generic keyword rules
// keyword_\1 in keywords.g. Each keyword should appear in at most one of
// these lists. For keywords that have a particular type of argument, use
// the raw_keyword_with_\1 rules above.

// core first, then expert.
keywordNoArgs : DEATHTOUCH
              | DEFENDER
              | DOUBLE_STRIKE
              | FIRST_STRIKE
              | FLASH
              | FLYING
              | HASTE
              | HEXPROOF
              | INDESTRUCTIBLE
              | INTIMIDATE
              | LIFELINK
              | MENACE
              | REACH
              | SHROUD
              | TRAMPLE
              | VIGILANCE
              | AFTERMATH
              | ASCEND
              | BANDING
              | BATTLE_CRY
              | CASCADE
              | CHANGELING
              | CIPHER
              | CONSPIRE
              | CONVOKE
              | DELVE
              | DETHRONE
              | DEVOID
              | EPIC
              | EVOLVE
              | EXALTED
              | EXPLOIT
              | EXTORT
              | FEAR
              | FLANKING
              | FUSE
              | GRAVESTORM
              | HAUNT
              | HIDEAWAY
              | HORSEMANSHIP
              | IMPROVISE
              | INFECT
              | INGEST
              | LIVING_WEAPON
              | MELEE
              | MYRIAD
              | PARTNER
              | PERSIST
              | PHASING
              | PROVOKE
              | PROWESS
              | REBOUND
              | RETRACE
              | SHADOW
              | SKULK
              | SOULBOND
              | SPLIT_SECOND
              | STORM
              | SUNBURST
              | SUSPEND
              | TOTEM_ARMOR
              | UNDAUNTED
              | UNDYING
              | UNLEASH
              | VANISHING
              | WITHER
              ;

keywordInt : ABSORB
           | AFFLICT
           | AMPLIFY
           | ANNIHILATOR
           | BLOODTHIRST
           | BUSHIDO
           | CREW
           | DEVOUR
           | DREDGE
           | FABRICATE
           | FADING
           | FRENZY
           | GRAFT
           | MODULAR
           | POISONOUS
           | RAMPAGE
           | RENOWN
           | RIPPLE
           | SOULSHIFT
           | TRIBUTE
           | VANISHING
           ;

keywordCost : AURA_SWAP
            | BESTOW
            | BUYBACK
            | CUMULATIVE_UPKEEP
            | CYCLING
            | DASH
            | ECHO
            | EMBALM
            | EMERGE
            | ENTWINE
            | EQUIP
            | ESCALATE
            | ETERNALIZE
            | EVOKE
            | FLASHBACK
            | FORTIFY
            | KICKER
            | LEVEL_UP
            | MADNESS
            | MEGAMORPH
            | MIRACLE
            | MORPH
            | MULTIKICKER
            | NINJUTSU
            | OUTLAST
            | OVERLOAD
            | PROWL 
            | RECOVER
            | REPLICATE
            | SCAVENGE
            | SPECTACLE
            | SURGE
            | TRANSFIGURE
            | TRANSMUTE
            | UNEARTH
            ;

keywordIntCost : AWAKEN
               | REINFORCE
               | SUSPEND
               ;

keywordQuality : ENCHANT
               | AFFINITY
               | BAND
               | CHAMPION
               | LANDWALK
               | OFFERING
               ;

keywordFrom : HEXPROOF
            | PROTECTION
            ;

keywordQualityCost : EQUIP
                   | CYCLING
                   | SPLICE
                   ;
