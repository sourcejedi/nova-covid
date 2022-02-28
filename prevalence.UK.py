#!/usr/bin/python3
import sys
import csv
from pathlib import Path

def uk(input_file, output_file):
    uk = dict()

    head = next(input_file)
    head = head.rstrip()
    heads = head.split(',', 3)
    assert heads[:3] == ['date', 'region', 'active_cases']

    for line in input_file:
        line = line.rstrip()
        (date, region, active_cases) = line.split(',', 3)[:3]
        if region == 'UK':
            sys.exit('Already shows UK prevalence')
        if region == 'England':
            # Safety check. Don't double-count.
            sys.exit('Found row for England. Only expected English regions')

        uk[date] = uk.get(date, 0) + float(active_cases)

    writer = csv.writer(output_file)
    writer.writerow(['date', 'active_cases'])
    dates = sorted(uk.keys())
    for date in dates:
        writer.writerow([date, uk[date]])

outdir = Path('out/prevalence_history.UK/')
outdir.mkdir(parents=True, exist_ok=True)

indir = Path('download/prevalence_history/')
paths = list(indir.glob('*.csv'))
for path in paths:
    filename = path.name
    with (path.open() as csvfile_in,
         (outdir / filename).open('w') as csvfile_out):
        uk(csvfile_in, csvfile_out)
