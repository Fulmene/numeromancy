from mtg_types import Ability, KeywordAbility
from parse import parse_ability
from visitor import demystify_visitor

def to_ability(kw_ability: KeywordAbility) -> list[Ability]:
    text_list = []
    if kw_ability.keyword == "flying":
        text_list = [ "SELF cannot be blocked by creatures without flying or reach." ]
    elif kw_ability.keyword == "vigilance":
        text_list = [ "SELF doesn't tap when it attacks." ]
    return list(map(demystify_visitor.visit, map(parse_ability, text_list)))
