#!/usr/bin/env python3

import os
from pathlib import Path
import csv
from collections import OrderedDict
import math

SKIP_LAST_DAYS=3
COMPARE_LAST_DAYS=18*3

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
                # Highlight splits, in prevalence_history
                #if region not in ['North East', 'East Midlands', 'London']:
                #    continue
                # Ignore splits, in incidence
                #if region not in ['East of England', 'London', 'North West','South East', 'South West']:
                #    continue
                if region in ['UK', 'England', 'Wales', 'Scotland', 'Northern Ireland']:
                    continue
                pop_mid = float(row[mid_field])
                value += pop_mid
            values[date] = value

            if prev_values:                
                def dates_to_compare():
                    last_dates = reversed(values.keys())

                    date = next(last_dates)
                    while date not in prev_values:
                        date = next(last_dates)

                    for _ in range(SKIP_LAST_DAYS):
                        date = next(last_dates)
                        assert date in prev_values

                    for _ in range(COMPARE_LAST_DAYS):
                        if date not in prev_values:
                            return # ran out of days in previous series
                        yield date
                        try:
                            date = next(last_dates)
                        except StopIteration:
                            return # ran out of days in current series
                
                def changes():
                    for d in dates_to_compare():
                        yield (values[d] - prev_values[d]) / prev_values[d]
                changes = list(changes())

                # change = Original metric
                sum_squares = 0
                for c in changes:
                    sum_squares += c * c
                change = math.sqrt(sum_squares / (len(changes) - 1))

                # change2 = Compensate for 18-day cyclic pattern,
                # visible in many but not all recent comparisons.
                # The pattern sums to zero,
                # so the simplest approach is to average it away.
                sum_squares = 0
                rolling_sum = sum(changes[:17])

                # change3 = Try to highlight the 18-day cyclic pattern.
                # This doesn't work very well.
                devs=[0]*18

                for i in range(17, len(changes)):
                    rolling_sum += changes[i]
                    mean = rolling_sum / 18
                    sum_squares += mean * mean
                    rolling_sum -= changes[i-17]

                    dev = changes[i-18//2] - mean
                    devs[i % 18] += dev

                change2 = math.sqrt(sum_squares / (len(changes) - 17 - 1))

                devs = [dev * dev for dev in devs]
                change3 = math.sqrt(sum(devs) / (len(devs) - 1))

                date = next(reversed(values.keys()))
                writer.writerow([date, change, change2, change3])
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
