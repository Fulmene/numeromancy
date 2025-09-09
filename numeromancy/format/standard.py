""" Code for handling the Standard format """
from datetime import datetime

from .sets import set_timeline, set_dict, find_set, date_and_code
from .banlist import get_banlist


standard_cycle = [
    'ONS',
    'MRD',
    'CHK',
    'RAV',
    'TSP',
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
# This will become the norm in the future
three_standards = ('DSK', 'WOE', 'DTK', 'BFZ', 'SOI', 'KLD', 'AKH', 'XLN')

def find_standard_sets(date_or_code: str|datetime) -> list[str]:
    date, code = date_and_code(date_or_code)
    rotation_group = set_dict[code].group
    prev = 3 if rotation_group in three_standards else 2

    # TODO Old core sets (8th Edition etc) are rotated out a the release of the next core set
    if code == 'FDN':
        rotations = ['DMU', 'WOE', 'FDN']
    else:
        idx = standard_cycle.index(rotation_group)
        rotations = standard_cycle[idx-prev+1:idx+1]
        if rotation_group in ('DFT', 'ECL'):
            rotations.insert(0, 'FDN')
        # Dominaria United rotated out on release of Edge of Eternities
        if date >= set_dict['EOE'].date:
            try:
                rotations.remove('DMU')
            except ValueError:
                pass
    sets = [k for k in set_dict if set_dict[k].group in rotations and set_dict[k].date <= date]
    return sets


def get_standard_banlist(date: str|datetime) -> set[str]:
    date, code = date_and_code(date)
    standard_sets = find_standard_sets(date)
    first_set = standard_sets[0]
    cutoff_date = set_dict[first_set].date
    return get_banlist("standard", date, date_start=cutoff_date)
