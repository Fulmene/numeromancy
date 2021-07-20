from grammar.DemystifyListener import DemystifyListener

class ParsedCard:
    def __init__(self, mana_cost, typeline, rules_text):
        self.mana_cost = mana_cost
        self.typeline = typeline
        self.rules_text = rules_text
