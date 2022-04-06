#!/usr/bin/python3

import csv
import math
from scipy.stats import gamma
import sys

# Recovery model (days)
RECOVERY_LEN=30
RECOVERY=[]

# Values shown in original study.
# These don't exactly match current data files
gamma = gamma(a=2.595, scale=4.48)

# Match current data files.
# stdev of the error is about 0.5%
#
# Both of these work.  Second one was trained on
# the data file which is longer & more recent &
# which provides fractional incidence.
#
#gamma = gamma(a=4.7, scale=2.88)
#gamma = gamma(a=4.5, scale=3.012)

# Fit to UK. Except you can't do that, oops.
# You need to do each region seperately.
#gamma = gamma(a=3.79, scale=3.50)


# x = days to recover
for x in range(0, RECOVERY_LEN):
    y_cum = gamma.cdf(x)
    RECOVERY.append(1-y_cum)


def prevalence(incidences):
    prevalences = []
    window = incidences[:RECOVERY_LEN-1]
    for i in range(RECOVERY_LEN-1, len(incidences)):
        incidence = incidences[i]
        window.append(incidence)
        
        prevalence = 0
        for j in range(0, RECOVERY_LEN):
            prevalence += window[RECOVERY_LEN-1-j] * RECOVERY[j]
        prevalences.append(prevalence)
        del window[0]
    return prevalences

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

def write_prevalence(infile, outfile):
    regions = sniff_regions(infile)
    for country in 'England', 'Wales', 'Scotland', 'Northern Ireland', 'UK':
        if country in regions:
            regions.remove(country)
            regions.append(country)

    dates = []
    incidences = {}
    for region in regions:
        incidences[region] = []

    reader = csv.DictReader(infile)
    prev_date = None
    for row in reader:
        date = row['date']
        if date != prev_date:
            prev_date = date
            dates.append(date)
        region = row['region']
        pop_mid = float(row.get('pop_mid') or row.get('covid_in_pop'))
        incidences[region].append(pop_mid)

    prevalences = {}
    for region in regions:
        prevalences[region] = prevalence(incidences[region])
    dates = dates[RECOVERY_LEN-1:]

    w = csv.writer(sys.stdout)
    w.writerow(['date'] + regions)
    i = 0
    for date in dates:
        w.writerow([date] + [prevalences[region][i] for region in regions])
        i += 1


if len(sys.argv) != 2:
    sys.exit("Usage: ./incidence.py input.csv > output.csv")

with open(sys.argv[1]) as infile:
    write_prevalence(infile, sys.stdout)
