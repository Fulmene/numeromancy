from datetime import datetime

from numeromancy.card import Card, get_card

date_format = '%d/%m/%Y'

type BanlistTimeline = list[tuple[str, list[str], list[str]]]
# date, banned cards, unbanned cards

# TODO Use actual effective date instead of first day of the month
_standard_banlist_timeline: BanlistTimeline = [
    ("01/01/1995", ["Balance"], []),  # Standard
    ("01/02/1996", ["Mind Twist"], []),  # Standard
    ("01/10/1996", [], ["Strip Mine"]),  # Standard (unban)
    ("01/12/1998", ["Tolarian Academy", "Windfall"], []),  # Standard
    ("01/03/1999", ["Dream Halls", "Earthcraft", "Fluctuator", "Lotus Petal", "Recurring Nightmare", "Time Spiral", "Memory Jar"], []),  # Standard
    ("01/06/1999", ["Mind Over Matter"], []),  # Standard
    ("01/06/2004", ["Skullclamp"], []),  # Standard
    ("01/03/2005", ["Arcbound Ravager", "Disciple of the Vault", "Darksteel Citadel", "Ancient Den", "Great Furnace", "Seat of the Synod", "Tree of Tales", "Vault of Whispers"], []),  # Standard
    ("01/06/2011", ["Jace, the Mind Sculptor", "Stoneforge Mystic"], []),
    ("01/01/2017", ["Emrakul, the Promised End", "Smuggler's Copter", "Reflector Mage"], []),  # Standard
    ("01/04/2017", ["Felidar Guardian"], []),  # Standard
    ("01/01/2018", ["Attune with Aether", "Rogue Refiner", "Ramunap Ruins", "Rampaging Ferocidon"], []),  # Standard
    ("01/08/2018", [], ["Rampaging Ferocidon"]),  # Standard (unban)
    ("01/09/2019", ["Field of the Dead"], []),  # Standard
    ("01/10/2020", ["Omnath, Locus of Creation", "Lucky Clover", "Escape to the Wilds"], []),  # Standard
    ("01/09/2020", ["Uro, Titan of Nature's Wrath"], []),  # Standard
    ("01/06/2020", ["Agent of Treachery", "Fires of Invention"], []),  # Standard
    ("01/08/2020", ["Cauldron Familiar", "Growth Spiral", "Teferi, Time Raveler", "Wilderness Reclamation"], []),  # Standard
    ("01/01/2022", ["Alrund's Epiphany", "Divide by Zero", "Faceless Haven"], []),  # Standard
    ("01/10/2022", ["The Meathook Massacre"], []),  # Standard
    ("01/05/2023", ["Fable of the Mirror-Breaker", "Invoke Despair", "Reckoner Bankbuster"], []),  # Standard
    ("01/06/2025", ["Cori-Steel Cutter", "Abuelo's Awakening", "Monstrous Rage", "Heartfire Hero", "Up the Beanstalk", "Hopeless Nightmare", "This Town Ain't Big Enough"], []),  # Standard
]

_pioneer_banlist_timeline: BanlistTimeline = [
    # Pioneer
    ("01/10/2019", [], ["Bloodstained Mire", "Flooded Strand", "Polluted Delta", "Windswept Heath", "Wooded Foothills"]),  # Fetch lands preemptive ban
    ("01/11/2019", ["Felidar Guardian", "Leyline of Abundance", "Oath of Nissa"], []),  # Pioneer
    ("01/12/2019", ["Field of the Dead", "Once Upon a Time", "Smuggler's Copter", "Oko, Thief of Crowns", "Nexus of Fate"], []),  # Pioneer
    ("01/08/2020", ["Inverter of Truth", "Kethis, the Hidden Hand", "Underworld Breach", "Walking Ballista"], []),  # Pioneer
    ("01/07/2020", [], ["Oath of Nissa"]),  # Pioneer (unban)
    ("01/02/2021", ["Balustrade Spy", "Teferi, Time Raveler", "Undercity Informer", "Uro, Titan of Nature's Wrath", "Wilderness Reclamation"], []),  # Pioneer
    ("01/03/2022", ["Lurrus of the Dream-Den"], []),  # Pioneer
    ("01/06/2022", ["Expressive Iteration", "Winota, Joiner of Forces"], []),  # Pioneer
    ("01/12/2023", ["Karn, the Great Creator", "Geological Appraiser"], ["Smuggler's Copter"]),  # Pioneer (ban and unban)
    ("01/12/2024", ["Jegantha, the Wellspring"], []),  # Pioneer
    ("01/08/2024", ["Amalia Benavides Aguirre", "Sorin, Imperious Bloodlord"], []),  # Pioneer
]

_modern_banlist_timeline: BanlistTimeline = [
    # Modern
    ("01/08/2011", ["Ancestral Vision", "Ancient Den", "Bitterblossom", "Chrome Mox", "Dark Depths", "Dread Return", "Glimpse of Nature", "Golgari Grave-Troll", "Great Furnace", "Hypergenesis", "Jace, the Mind Sculptor", "Mental Misstep", "Seat of the Synod", "Sensei's Divining Top", "Skullclamp", "Stoneforge Mystic", "Sword of the Meek", "Tree of Tales", "Umezawa's Jitte", "Valakut, the Molten Pinnacle", "Vault of Whispers"], []),  # Modern intro banlist
    ("01/12/2011", ["Punishing Fire", "Wild Nacatl"], []),  # Modern
    ("01/01/2013", ["Bloodbraid Elf", "Seething Song"], []),  # Modern
    ("01/05/2013", ["Second Sunrise"], []),  # Modern
    ("01/02/2014", ["Deathrite Shaman"], ["Bitterblossom", "Wild Nacatl"]),  # Modern (ban and unbans)
    ("01/01/2015", ["Dig Through Time", "Treasure Cruise", "Birthing Pod"], ["Golgari Grave-Troll"]),  # Modern
    ("01/01/2016", ["Splinter Twin", "Summer Bloom"], []),  # Modern
    ("01/04/2016", ["Eye of Ugin"], ["Ancestral Vision", "Sword of the Meek"]),  # Modern (ban and unbans)
    ("01/01/2017", ["Gitaxian Probe", "Golgari Grave-Troll"], []),  # Modern
    ("01/02/2018", [], ["Jace, the Mind Sculptor", "Bloodbraid Elf"]),  # Modern unbans
    ("01/01/2019", ["Krark-Clan Ironworks"], []),  # Modern
    ("01/08/2019", ["Hogaak, Arisen Necropolis", "Faithless Looting"], ["Stoneforge Mystic"]),  # Modern (bans and unban)
    ("01/01/2020", ["Oko, Thief of Crowns", "Mox Opal", "Mycosynth Lattice"], []),  # Modern
    ("01/03/2020", ["Once Upon a Time"], []),  # Modern
    ("01/07/2020", ["Arcum's Astrolabe"], []),  # Modern
    ("01/02/2021", ["Field of the Dead", "Mystic Sanctuary", "Simian Spirit Guide", "Tibalt's Trickery", "Uro, Titan of Nature's Wrath"], []),  # Modern
    ("01/03/2022", ["Lurrus of the Dream-Den"], []),  # Modern
    ("01/08/2022", ["Yorion, Sky Nomad"], []),  # Modern
    ("01/08/2023", [], ["Preordain"]),  # Modern unban
    ("01/12/2023", ["Fury", "Up the Beanstalk"], []),  # Modern
    ("01/03/2024", ["Violent Outburst"], []),  # Modern
    ("01/08/2024", ["Grief"], []),  # Modern
    ("01/12/2024", ["Amped Raptor", "Jegantha, the Wellspring", "The One Ring"], ["Faithless Looting", "Green Sun's Zenith", "Mox Opal", "Splinter Twin"]),  # Modern (bans and unbans)
    ("01/03/2025", ["Underworld Breach"], []),  # Modern
]

BANLIST_TIMELINE = {
    'standard': _standard_banlist_timeline,
    'pioneer': _pioneer_banlist_timeline,
    'modern': _modern_banlist_timeline,
}

def get_banlist(timeline: BanlistTimeline, date_until: str) -> set[Card]:
    banned_cards = []
    datetime_until = datetime.strptime(date_until, date_format)
    for date, banned, unbanned in timeline:
        if datetime.strptime(date, date_format) > datetime_until:
            break
        banned_cards = [c for c in banned_cards + banned if c not in unbanned]
    return set(get_card(c) for c in banned_cards)
