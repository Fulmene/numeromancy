class CardFace:
    def __init__(self, scryfall_card_face):
        self.name = scryfall_card_face.get("name")
        self.mana_cost = scryfall_card_face.get("mana_cost") or ""

        # Mana value of some un-cards can be fractional,
        # but black-bordered Magic cards can only have integer MV
        # by rule 107.1
        self.cmc = int(scryfall_card_face.get("cmc"))
        self.colors = scryfall_card_face.get("colors")

        self.type_line = scryfall_card.get("type_line")
        self.supertypes, self.cardtypes, self.subtypes = parse_type_line(self.type_line)
        self.oracle_text = scryfall_card_face.get("oracle_text") or ""

        self.power = scryfall_card_face.get("power")
        self.toughness = scryfall_card_face.get("toughness")
        self.loyalty = scryfall_card_face.get("loyalty")
        self.defense = scryfall_card_face.get("defense")
