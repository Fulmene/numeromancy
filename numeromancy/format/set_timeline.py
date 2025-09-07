from datetime import datetime
from bisect import bisect_right

date_format = '%d/%m/%Y'

set_timeline = [
    ('30/9/2016', 'KLD', "standard"),
    ('20/1/2017', 'AER', "standard"),
    ('28/4/2017', 'AKH', "standard"),
    ('14/7/2017', 'HOU', "standard"),
    ('29/9/2017', 'XLN', "standard"),
    ('19/1/2018', 'RIX', "standard"),
    ('27/4/2018', 'DOM', "standard"),
    ('13/7/2018', 'M19', "standard"),
    ('5/10/2018', 'GRN', "standard"),
    ('25/1/2019', 'RNA', "standard"),
    ('3/5/2019', 'WAR', "standard"),
    ('12/7/2019', 'M20', "standard"),
    ('4/10/2019', 'ELD', "standard"),
    ('24/1/2020', 'TBD', "standard"),
    ('24/4/2020', 'IKR', "standard"), # The actual release was delayed to May 15, but we'll use the official legality date for this
    ('3/7/2020', 'M21', "standard"),
    ('25/9/2020', 'ZNR', "standard"),
    ('5/2/2021', 'KLD', "standard"),
    ('23/4/2021', 'STX', "standard"),
    ('23/7/2021', 'AFR', "standard"),
    ('24/9/2021', 'MID', "standard"),
    ('19/11/2021', 'VOW', "standard"),
    ('18/2/2022', 'NEO', "standard"),
    ('29/4/2022', 'SNC', "standard"),
    ('9/9/2022', 'DMU', "standard"),
    ('18/11/2022', 'BRO', "standard"),
    ('10/2/2023', 'ONE', "standard"),
    ('12/5/2023', 'MOM', "standard"),
    ('8/9/2023', 'WOE', "standard"),
    ('17/11/2023', 'LCI', "standard"),
    ('9/2/2024', 'MKM', "standard"),
    ('19/4/2024', 'OTJ', "standard"),
    ('2/8/2024', 'BLB', "standard"),
    ('27/9/2024', 'DSK', "standard"),
    ('15/11/2024', 'FDN', "standard"),
    ('14/2/2025', 'DFT', "standard"),
    ('11/4/2025', 'TDM', "standard"),
    ('13/6/2025', 'FIN', "standard"),
    ('1/8/2025', 'EOE', "standard"),
]
set_timeline = [(datetime.strptime(date, date_format), st.lower(), f) for date, st, f in set_timeline]


def find_set(date):
    date = datetime.strptime(date, date_format)
    idx = bisect_right(set_timeline, date, key=lambda x: x[0]) - 1
    return set_timeline[idx][1]
