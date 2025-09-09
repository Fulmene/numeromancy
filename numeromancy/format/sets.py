from datetime import datetime
from bisect import bisect_right
from typing import NamedTuple, Literal

date_format = '%d/%m/%Y'

class SetEntry(NamedTuple):
    date: datetime
    format: Literal["standard", "modern"]
    group: str

_set_timeline = [
    # These parts were copied from Deepseek
    ("ONS", "07/10/2002", "standard", "ONS"),
    ("LGN", "03/02/2003", "standard", "ONS"),
    ("SCG", "26/05/2003", "standard", "ONS"),
    ("8ED", "28/07/2003", "standard", "8ED"),
    ("MRD", "02/10/2003", "standard", "MRD"),
    ("DST", "06/02/2004", "standard", "MRD"),
    ("5DN", "04/06/2004", "standard", "MRD"),
    ("CHK", "01/10/2004", "standard", "CHK"),
    ("BOK", "04/02/2005", "standard", "CHK"),
    ("SOK", "03/06/2005", "standard", "CHK"),
    ("9ED", "29/07/2005", "standard", "9ED"),
    ("RAV", "07/10/2005", "standard", "RAV"),
    ("GPT", "03/02/2006", "standard", "RAV"),
    ("DIS", "05/05/2006", "standard", "RAV"),
    ("TSP", "06/10/2006", "standard", "TSP"),
    ("PLC", "02/02/2007", "standard", "TSP"),
    ("FUT", "04/05/2007", "standard", "TSP"),
    ("10E", "13/07/2007", "standard", "10E"),
    ("LRW", "12/10/2007", "standard", "LRW"),
    ("MOR", "01/02/2008", "standard", "LRW"),
    ("SHM", "02/05/2008", "standard", "LRW"),
    ("EVE", "25/07/2008", "standard", "LRW"),
    ("ALA", "03/10/2008", "standard", "ALA"),
    ("CON", "30/01/2009", "standard", "ALA"),
    ("ARB", "30/04/2009", "standard", "ALA"),
    ("M10", "17/07/2009", "standard", "ALA"),
    ("ZEN", "02/10/2009", "standard", "ZEN"),
    ("WWK", "05/02/2010", "standard", "ZEN"),
    ("ROE", "23/04/2010", "standard", "ZEN"),
    ("M11", "16/07/2010", "standard", "ZEN"),
    ("SOM", "01/10/2010", "standard", "SOM"),
    ("MBS", "04/02/2011", "standard", "SOM"),
    ("NPH", "13/05/2011", "standard", "SOM"),
    ("M12", "15/07/2011", "standard", "SOM"),
    ("ISD", "30/09/2011", "standard", "ISD"),
    ("DKA", "03/02/2012", "standard", "ISD"),
    ("AVR", "04/05/2012", "standard", "ISD"),
    ("M13", "13/07/2012", "standard", "ISD"),
    ("RTR", "05/10/2012", "standard", "RTR"),
    ("GTC", "01/02/2013", "standard", "RTR"),
    ("DGM", "03/05/2013", "standard", "RTR"),
    ("M14", "19/07/2013", "standard", "RTR"),
    ("THS", "27/09/2013", "standard", "THS"),
    ("BNG", "07/02/2014", "standard", "THS"),
    ("JOU", "02/05/2014", "standard", "THS"),
    ("M15", "18/07/2014", "standard", "THS"),
    ("KTK", "26/09/2014", "standard", "KTK"),
    ("FRF", "23/01/2015", "standard", "KTK"),
    ("DTK", "27/03/2015", "standard", "DTK"),
    ("ORI", "17/07/2015", "standard", "DTK"),
    ("BFZ", "02/10/2015", "standard", "BFZ"),
    ("OGW", "22/01/2016", "standard", "BFZ"),
    ("SOI", "08/04/2016", "standard", "SOI"),
    ("EMN", "22/07/2016", "standard", "SOI"),

    # These parts were typed by hand and verified
    ('KLD', '30/9/2016', "standard", "KLD"),
    ('AER', '20/1/2017', "standard", "KLD"),
    ('AKH', '28/4/2017', "standard", "AKH"),
    ('HOU', '14/7/2017', "standard", "AKH"),
    ('XLN', '29/9/2017', "standard", "XLN"),
    ('RIX', '19/1/2018', "standard", "XLN"),
    ('DOM', '27/4/2018', "standard", "XLN"),
    ('M19', '13/7/2018', "standard", "XLN"),
    ('GRN', '5/10/2018', "standard", "GRN"),
    ('RNA', '25/1/2019', "standard", "GRN"),
    ('WAR', '3/5/2019', "standard", "GRN"),
    ('MH1', '14/6/2019', "modern", "modern"), # Modern Horizon
    ('M20', '12/7/2019', "standard", "GRN"),
    ('ELD', '4/10/2019', "standard", "ELD"),
    ('TBD', '24/1/2020', "standard", "ELD"),
    ('IKR', '24/4/2020', "standard", "ELD"),
    ('M21', '3/7/2020', "standard", "ELD"),
    ('ZNR', '25/9/2020', "standard", "ZNR"),
    ('KHM', '5/2/2021', "standard", "ZNR"),
    ('STX', '23/4/2021', "standard", "ZNR"),
    ('MH2', '18/6/2021', "modern", "modern"), # Modern Horizon 2
    ('AFR', '23/7/2021', "standard", "ZNR"),
    ('MID', '24/9/2021', "standard", "MID"),
    ('VOW', '19/11/2021', "standard", "MID"),
    ('NEO', '18/2/2022', "standard", "MID"),
    ('SNC', '29/4/2022', "standard", "MID"),
    ('DMU', '9/9/2022', "standard", "DMU"),
    ('BRO', '18/11/2022', "standard", "DMU"),
    ('ONE', '10/2/2023', "standard", "DMU"),
    ('MOM', '21/4/2023', "standard", "DMU"),
    ('MAT', '12/5/2023', "standard", "DMU"),
    ("LTR", "23/06/2023", "modern", "modern"), # The Lords of the Rings
    ('WOE', '8/9/2023', "standard", "WOE"),
    ('LCI', '17/11/2023', "standard", "WOE"),
    ('MKM', '9/2/2024', "standard", "WOE"),
    ('OTJ', '19/4/2024', "standard", "WOE"),
    ('MH3', '14/6/2024', "modern", "modern"), # Modern Horizon 3
    ('ACR', '5/7/2024', "modern", "modern"), # Assassin's Creed
    ('BLB', '2/8/2024', "standard", "WOE"),
    ('DSK', '27/9/2024', "standard", "WOE"),
    ('FDN', '15/11/2024', "standard", "FDN"), # Foundation
    ('DFT', '14/2/2025', "standard", "DFT"),
    ('TDM', '11/4/2025', "standard", "DFT"),
    ('FIN', '13/6/2025', "standard", "DFT"),
    ('EOE', '1/8/2025', "standard", "DFT"),
]
_set_timeline = [(st, datetime.strptime(date, date_format), f, prev_st) for st, date, f, prev_st in _set_timeline]
SETS = {st: SetEntry(date, f, prev_st) for st, date, f, prev_st in _set_timeline}


def find_set(date: datetime):
    # if not isinstance(date, datetime):
    #     date = datetime.strptime(date, date_format)
    idx = bisect_right(_set_timeline, date, key=lambda x: x[1]) - 1
    return _set_timeline[idx][0]


def date_and_code(date_or_code: str|datetime) -> tuple[datetime, str]:
    if isinstance(date_or_code, datetime):
        date = date_or_code
        code = find_set(date)
    else:
        try:
            date = datetime.strptime(date_or_code, date_format)
            code = find_set(date)
        except ValueError:
            code = date_or_code.upper()
            date = SETS[code].date
    return date, code


def get_modern_sets(date_or_code):
    eightedition_date = SETS['8ED'].date
    date, code = date_and_code(date_or_code)
    return [k for k in SETS if SETS[k].format in ('standard', 'modern') and eightedition_date <= SETS[k].date and SETS[k].date <= date]


def get_pioneer_sets(date_or_code):
    rtr_date = SETS['RTR'].date
    date, code = date_and_code(date_or_code)
    return [k for k in SETS if SETS[k].format == 'standard' and rtr_date <= SETS[k].date and SETS[k].date <= date]
