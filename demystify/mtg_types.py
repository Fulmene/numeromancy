from typing import Literal, NamedTuple, Union

Color = Literal["white", "blue", "black", "red", "green"]

class ManaSymbol(NamedTuple):
    symbol: str
    hybrid_symbol: Union[str, None] = None

    @classmethod
    def from_str(cls, symbol_str: str):
        symbol_list = symbol_str.strip('{}').split('/')
        l = len(symbol_list)
        if l == 1:
            return cls(symbol_list[0])
        elif l == 2:
            return cls(symbol_list[0], hybrid_symbol=symbol_list[1])
        else:
            raise ValueError("Incorrect number of mana symbol parts")

    def __repr__(self):
        if self.hybrid_symbol is None:
            return '{%s}' % self.symbol
        else:
            return '{%s/%s}' % (self.symbol, self.hybrid_symbol)

Mana = list[ManaSymbol]


class Typeline(NamedTuple):
    cardTypes: list[str]
    supertypes: list[str] = []
    subtypes: list[str] = []

    def __repr__(self):
        sup = (' '.join(self.supertypes) + ' ') if len(self.supertypes) > 0 else ''
        typ = ' '.join(self.cardTypes)
        sub = (' -- ' + ' '.join(self.subtypes)) if len(self.subtypes) > 0 else ''
        return '%s%s%s' % (sup, typ, sub)

class KeywordAbility(NamedTuple):
    keyword: str
    arg_int: Union[str, None] = None
    arg_cost: Union[str, None] = None
    arg_quality: Union[str, None] = None
    arg_from: Union[list[str], None] = None

class Subset(NamedTuple):
    noun: str
    adj: list[str]
    descriptor: list[str]

class Sentence(NamedTuple):
    subj: str # Noun
    verb: str # Verb
    direct_obj: str | None = None # Noun
    indirect_obj: str | None = None

class Duration(NamedTuple):
    duration_end: str | None = None
    duration_span: str | None = None

class AtomicEffect(NamedTuple):
    effect: Sentence
    duration: Duration | None = None
    condition: Sentence | None = None

class Ability(NamedTuple):
    ability_type: Literal["static", "triggered", "activated"]
    effect: list[Sentence]
    cost: list[Union[Mana, Sentence]] = []
    trigger: Union[Sentence, None] = None
    keyword: Union[str, None] = None

KeywordLine = list[KeywordAbility]
Line = Union[KeywordLine, Ability]
RulesText = list[Line]

class ParsedCard(NamedTuple):
    mana_cost: Mana
    typeline: Typeline
    rules_text: RulesText
