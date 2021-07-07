lexer grammar Symbols;

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

/* Symbols and punctuation */

// These four are the only things in rules text exempt from being lowercased.
SELF : 'SELF';

PARENT : 'PARENT';

REFBYNAME : 'NAME_' ( 'A'..'Z' | 'a'..'z' | '_' | '\u00c6' | '\u00e6' )+;

// Chop off brackets for the symbols whose text we'll need later.
// Unfortunately we have to do our checking against hybrid alternatives
// elsewhere.

MANA_SYM
    : '{' ( WUBRGC | DIGIT_SYM | SNOW_SYM ) ( '/' WUBRGCP )? '}'
      { setText(_text[1:-1].upper()) };

// Appearance in rules text
PHYREXIA_SYM : '{p}' { setText('P') };

VAR_MANA_SYM : '{' ('x'..'z') '}' { setText(_text[1:-1].upper()) };

TAP_SYM : '{t}' { setText('T') };

UNTAP_SYM : '{q}' { setText('Q') };

VAR_SYM : 'x'..'z' { setText(_text.upper()) };

ENERGY_SYM : '{e}' { setText('E') };

// Level up
LEVEL_SYM : '{level ' ( NUMBER_SYM '-' NUMBER_SYM | NUMBER_SYM '+' ) '}'
            { setText(_text[6:-1].strip()) };

NUMBER_SYM : DIGIT_SYM;

MDASH : ( '\u2014' | '--' );

BULLET : '\u2022';

APOS_S : '\'s' ;

WS : ( ' ' | '\t' | '\n' ) -> skip ;

fragment SNOW_SYM : 's';

fragment WUBRGC : ('w'|'u'|'b'|'r'|'g'|'c');

fragment WUBRGCP : ( WUBRGC | 'p' );

fragment DIGIT_SYM : ('1'..'9' '0'..'9') | ('0'..'9');
