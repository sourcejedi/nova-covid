#!/usr/bin/env python3
import csv
from pathlib import Path

def sniff_regions(infile):
    regions = []
    read = csv.DictReader(infile)
    row = next(read, None)
    assert row
    date = row.get('date')
    assert(date)
    start = date
    while date == start:
        region = row.get('region')
        assert region
        assert region not in regions
        regions.append(region)
        row = next(read, None)
        assert row
        date = row.get('date')
    regions.sort()
    infile.seek(0)
    return regions

def newly_sick_table(infile, outfile):
    regions = sniff_regions(infile)
    for country in 'England', 'Wales', 'Scotland', 'Northern Ireland', 'UK':
        if country in regions:
            regions.remove(country)
            regions.append(country) 

    dates = []
    values = {}
    for region in regions:
        values[region] = []
    
    reader = csv.DictReader(infile)
    prev_date = None
    for row in reader:
        date = row['date']
        if date != prev_date:
            prev_date = date
            dates.append(date)
        region = row['region']
        value = float(row.get('perc_users'))
        values[region].append(value)

    w = csv.writer(outfile)
    w.writerow(['date'] + regions)
    i = 0
    for date in dates:
        w.writerow([date] + [values[region][i] for region in regions])
        i += 1

indir = Path('download/newly_sick_table/')
paths = list(indir.glob('*.csv'))
paths.sort()
assert(paths)
with (paths[-1].open() as csvfile_in,
      open('out/latest_newly_sick_table.csv', 'w') as csvfile_out):
    newly_sick_table(csvfile_in, csvfile_out)
