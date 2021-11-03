from typing import Literal, NamedTuple, Union


Color = Literal["white", "blue", "black", "red", "green"]

ColorSymbol = Literal['w', 'u', 'b', 'r', 'g', 'c', 'p']
VarSymbol = Literal['x', 'y', 'z']
SymbolStr = Union[ColorSymbol, VarSymbol, int]

class ManaSymbol(NamedTuple):
    symbol: SymbolStr
    hybrid_symbol: Union[SymbolStr, None] = None

    @classmethod
    def from_str(cls, symbol_str: str):
        symbol_list = symbol_str.split('/')
        l = len(symbol_list)
        if l == 1:
            return cls(symbol_list[0])
        elif l == 2:
            return cls(symbol_list[0], hybrid_symbol=symbol_list[1])
        else:
            raise ValueError("Incorrect number of mana symbol parts")

Mana = list[ManaSymbol]


Supertype = Literal["basic", "legendary", "snow"]
CardType = Literal["creature", "artifact", "enchantment", "planeswalker", "land", "instant", "sorcery"]
Subtype = str

class Typeline(NamedTuple):
    cardTypes: list[CardType]
    supertypes: list[Supertype] = []
    subtypes: list[Subtype] = []


class Sentence(NamedTuple):
    subj: str
    verb: str
    obj:  str

class Ability(NamedTuple):
    ability_type: Literal["static", "triggered", "activated", "keyword"]
    effect: list[Sentence]
    cost: list[Mana or Sentence]
    trigger: Sentence
    keyword: str

class RulesText(NamedTuple):
    abilities: list[Ability]

class ParsedCard(NamedTuple):
    mana_cost: Mana
    typeline: Typeline
    rules_text: RulesText
