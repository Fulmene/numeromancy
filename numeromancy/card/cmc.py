def convert(symbol: str) -> int:
    parts = symbol.split('/')
    return max(int(p) if p.isdigit() else 1 for p in parts)

def cmc(mana_cost: str) -> int:
    # Mana costs will be in the format {A}{B}{C}
    symbols = mana_cost[1:-1].split('}{')
    return sum(convert(s) for s in symbols)
