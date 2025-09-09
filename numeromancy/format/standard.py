""" Code for handling the Standard format """
from datetime import datetime

from .sets import _set_timeline, SETS, find_set, date_and_code
from .banlist import get_banlist


standard_cycle = [
    'ONS',
    '8ED',
    'MRD',
    'CHK',
    '9ED',
    'RAV',
    'TSP',
    '10E',
    'LRW',
    'ALA',
    'ZEN',
    'SOM',
    'ISD',
    'RTR',
    'THS',
    'KTK',
    'DTK',
    'BFZ',
    'SOI',
    'KLD',
    'AKH',
    'XLN',
    'GRN',
    'ELD',
    'ZNR',
    'MID',
    'DMU',
    'WOE',
    'DFT',
    'ECL',
]

two_group_standards = (
    'ZEN', 'SOM', 'ISD', 'RTR', 'THS', 'KTK', # Post M10, Pre three block structures
    'GRN', 'ELD', 'ZNR', 'MID', 'DMU', # Post block structures
)

def find_standard_sets(date_or_code: str|datetime) -> list[str]:
    date, code = date_and_code(date_or_code)
    rotation_group = SETS[code].group
    prev = 2 if rotation_group in two_group_standards else 3

    if code == 'FDN':
        # Foundation is in its own group, legal for about five years after release
        rotations = ['DMU', 'WOE', 'FDN']
    else:
        idx = standard_cycle.index(rotation_group)
        rotations = standard_cycle[idx-prev+1:idx+1]
        if date >= SETS['FDN'].date:
            rotations.insert(0, 'FDN')
        # Innistrad: Midnight Hunt rotated out on release of Bloomburrow
        if date >= SETS['BLB'].date:
            try:
                rotations.remove('MID')
            except ValueError:
                pass
        # Likewise, Dominaria United rotated out on release of Edge of Eternities
        if date >= SETS['EOE'].date:
            try:
                rotations.remove('DMU')
            except ValueError:
                pass
    sets = [k for k in SETS if SETS[k].group in rotations and SETS[k].date <= date]
    return sets


def get_standard_banlist(date: str|datetime) -> set[str]:
    date, code = date_and_code(date)
    standard_sets = find_standard_sets(date)
    first_set = standard_sets[0]
    cutoff_date = SETS[first_set].date
    return get_banlist("standard", date, date_start=cutoff_date)
