#!/usr/bin/env python3

# Performance log:
#  1. Switching from csv module parsing to crude split() was a small gain
#    (less than 25%) 
#  2. More performance was gained by looping in python,
#    instead of using bash to run the python script hundreds of times.
#  3. However if the order is reversed, the loop seems to save about
#     half of the time, and the cruder parsing seems to save half again.

# Limitations:
#
# Summing English regions is not what ZOE were doing for incidence?
# But they are by now (ZOE v5), and it's what ZOE were doing for their
# published prevalence.
# See p_from_incidence_history.UK_20210518.ods
#
# prevalence_history_20210512.csv and later are re-weighted by vaccination.
# incidence_history_20210512.csv and later are *not* re-weighted by vaccination.
# (the latter could be useful with reference to incidence table.csv).
#
# incidence_20210507.csv and later are re-weighted by vaccination,
# as if the code for this was updated one day earlier than incidence_history
# and the public announcement.

import csv
from pathlib import Path

def england(input_file, output_file):
    england = dict()

    head = next(input_file)
    head = head.rstrip()
    heads = head.split(',', 3)
    assert heads[:3] == ['date', 'region', 'active_cases']

    for line in input_file:
        line = line.rstrip()
        (date, region, active_cases) = line.split(',', 3)[:3]
        if region == 'England':
            sys.exit('Already shows England prevalence')
        if region in ['Wales', 'Scotland', 'Northern Ireland']:
            continue
        # English regions
        england[date] = england.get(date, 0) + float(active_cases)

    writer = csv.writer(output_file)
    writer.writerow(['date', 'active_cases'])
    dates = sorted(england.keys())
    for date in dates:
        writer.writerow([date, england[date]])

outdir = Path('out/prevalence_history.England_weighted/')
outdir.mkdir(parents=True, exist_ok=True)

indir = Path('download/prevalence_history/')
paths = list(indir.glob('*.csv'))
for path in paths:
    filename = path.name
    with (path.open() as csvfile_in,
         (outdir / filename).open('w') as csvfile_out):
        england(csvfile_in, csvfile_out)
