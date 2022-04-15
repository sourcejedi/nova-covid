#!/usr/bin/env python3

import os
from pathlib import Path
import csv
from collections import OrderedDict
import math

SKIP_LAST_DAYS=3
COMPARE_LAST_DAYS=30

def jump(indir, prefix, outfile):
    writer = csv.writer(outfile)

    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()
    prefix_len = len(prefix)

    prev_values = None

    for path in paths:
        values = OrderedDict()
        name = path.name[prefix_len:-4]
        print(path)
        with path.open() as f:
            head = f.readline()
            assert head
            head = head.rstrip()
            assert head

            heads = head.split(',')
            date_field = 0
            if not heads[0]:
                date_field = 1
            assert heads[date_field] == 'date'

            region_field = heads.index('region')

            field_names = ['pop_mid', 'covid_in_pop', 'active_cases']
            for field_name in field_names:
                try:
                    mid_field = heads.index(field_name)
                    break
                except ValueError:
                    pass
            else:
                raise Exception(f'{path}: could not find one of {field_names}')

            prev_date = None
            value = 0
            for line in f:
                row = line.split(',')
                date = row[date_field]
                if date != prev_date:
                    if prev_date is not None:
                        values[date] = value
                        value = 0
                    prev_date = date
                region = row[region_field]
                #if region not in ['East of England', 'London', 'North West','South East', 'South West']:
                #    continue
                if region in ['UK', 'England', 'Wales', 'Scotland', 'Northern Ireland']:
                    continue
                pop_mid = float(row[mid_field])
                value += pop_mid
            values[date] = value

            if prev_values:
                last_dates = reversed(values.keys())
                i = COMPARE_LAST_DAYS
                j = SKIP_LAST_DAYS
                all_dev = 0
                for d in last_dates:
                    if j > 0:
                        j -= 1
                        continue
                    if d not in prev_values:
                        continue
                    dev = (values[d] - prev_values[d]) / prev_values[d]
                    dev = dev * dev
                    all_dev += dev
                    i -= 1
                    if i <= 0:
                        break
                all_dev = math.sqrt(all_dev / (COMPARE_LAST_DAYS-1))

                date = next(reversed(values.keys()))
                writer.writerow([date, all_dev])
            prev_values = values

outdir = Path('out/jump/')
outdir.mkdir(parents=True, exist_ok=True)

indir = Path('download/incidence/')
with open(outdir / 'incidence.csv', 'w') as outfile:
    jump(indir, 'incidence_', outfile)

indir = Path('download/incidence_history/')
with open(outdir / 'incidence_history.csv', 'w') as outfile:
    jump(indir, 'incidence_history_', outfile)

indir = Path('download/prevalence_history/')
with open(outdir / 'prevalence_history.csv', 'w') as outfile:
    jump(indir, 'prevalence_history_', outfile)
