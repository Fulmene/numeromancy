parser grammar costs;

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

/* Costs and payments */

// TODO: "as an additional cost" items: "you may", "choose" type/number.

// The OR case here is where the player has the option to choose
// either of the methods to pay for the ability,
// eg. 3, TAP or U, TAP.

cost : costList ( conj costList )?
     | loyaltyCost
     ;

// The AND case here is usually for costs where a latter item
// references a preceding item,
// eg. remove n quest counters from SELF and sacrifice it.
// This sometimes makes it seem like MTG doesn't use the oxford comma
// in separating cost items, but does in separating subsets as part of
// a cost item. More simply, MTG doesn't normally use 'and' in cost lists
// eg: "{2}{u}, {t}, discard a card, sacrifice a land".

costList : costItem ( COMMA costItem )*
         | costItem AND costItem ;

costItem : TAP_SYM
         | UNTAP_SYM
         | mana
         //| repeatableCostItem forEach?
         ;

repeatableCostItem : PAY mana
                   | discard
                   | exile
                   | move_cards
                   | pay_mana_cost
                   //| pay_energy
                   //| pay_life
                   | put_counters
                   | remove_counters
                   | reveal
                   | sacrifice
                   | tap
                   | unattach
                   | untap
                   ;

// Loyalty

loyaltyCost : PLUS_SYM? ( NUMBER_SYM | VAR_SYM )
            | MINUS_SYM ( NUMBER_SYM | VAR_SYM )
            ;

// Mana symbols and mana costs

mana : manaSymbol+ ;

manaSymbol : MANA_SYM | VAR_MANA_SYM ;

// TODO these are just game actions

discard : DISCARD subset ( AT RANDOM )? ;

exile : EXILE subset ;

move_cards : ( PUT | RETURN ) subset ( TO | ON | INTO ) zoneSubset ;

pay_energy : PAY ( ANY AMOUNT OF ENERGY_SYM
                 //| A AMOUNT OF ENERGY_SYM EQUAL TO magic_number
                 | ENERGY_SYM+
                 );

//pay_life : PAY magic_life_number ;

pay_mana_cost : PAY refObjPoss MANA COST ;

put_counters : PUT counterSubset ON subset ;

remove_counters : REMOVE counterSubset FROM subset ;

reveal : REVEAL subset ;

sacrifice : SACRIFICE subset ;

tap : TAP subset ;

unattach : UNATTACH subset ;

untap : UNTAP subset ;
