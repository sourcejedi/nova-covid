#!/usr/bin/python3

# Configuration variable - choose the recovery model.

# Use recovery vector reverse-engineered from comparing data files.
# Or...
USE_GAMMA_MODEL=False

# ...Use a gamma distribution model, like the paper.
# See code below for parameters and comments.
#USE_GAMMA_MODEL=True


# This script can now reproduce ZOE prevalence estimates
# from the ZOE incidence estimates.
#
# Limitations apply:
#
# 1. I changed the output format.  Each region is in its own column.
#
# 2. ZOE prevalence_history_*.csv does not include values for
#    "England", only the sub-regions of England.
#
#    In incidence estimates published before 2021-07-17 ("method v4"),
#    "England" does not equal the sum of the English regions.
#
# 3. For files before prevalence_history_20220131.csv (2022-01-31),
#    we cannot reproduce the following regions:
#    North East, Yorkshire and The Humber, East Midlands, West Midlands.
#    The official prevalences are much less smooth than for other
#    regions.  However, we can reproduce the sums North East +
#    Yorkshire and The Humber, and East Midlands + West Midlands.
#
#    Hence, we can still reproduce the sum of the English regions.
#
#    I believe regions were combined and then apportioned using
#    symptom-based prevalence ("P_A" in the Lancet paper).
#
# 4. The earliest data file available to reproduce is
#    prevalence_history_20210209.csv.
#
#     * Using incidence_history_20210209.csv will not reproduce the first
#       31 days of prevalence_history_20210209.csv, because it does not go
#       back far enough.
#
#     * Using incidence_history_20210209.csv will not reproduce the last
#       2 days of prevalence_history_20210209.csv, because it does not go
#       far enough.
#
# 5. Using incidence_20210205.csv will not reproduce the exact output.
#    In incidence_*.csv files around this date, the central estimate
#    is rounded to the nearest whole number.  I believe exact
#    reproduction is possible by multiplying the "100k_mid" collumn by
#    population (taken from the "incidence table.csv" published the same
#    day).
#
#    On the other hand, it provides dates earlier than those included
#    in prevalence_history.  The earlier dates are also graphed in the
#    Lancet paper, showing very similar results.
#
# 6. The recovery vector used to obtain these results (below) is
#    clearly different from the recovery curve in Figure 2 of the
#    Lancet paper.  I have asked the authors if they can explain this.
#
# 7. Some rows in the prevalence_history series show unexpected
#    zeroes, i.e. completely outside the trend.  I do not reproduce
#    these zeroes.  This seems to be a limitation of the official
#    files.


import csv
import math
from scipy.stats import gamma
import sys


RECOVERY = """0
0
0
0
0
0
0
0.107361446459658
0.195182211241508
0.261609298669212
0.354483688022909
0.435622438093099
0.522264023808184
0.575327081812568
0.618507496209782
0.671289797293501
0.725195126059856
0.772867651187606
0.802459430624964
0.832725026671902
0.855297883092825
0.876635409062832
0.888595653882872
0.902521197147509
0.913751473973833
0.932337582121397
0.938121174686953
0.951204447189625
0.953113594250103
0.961143242180908"""

if not USE_GAMMA_MODEL:
    # Recovery model, extracted by taking advantage of zeroes
    # in Northern Ireland, *_history_20210510.csv.
    #
    # stdev of error is lowered to less than 0.05%,
    # except there are some visible anomalies
    # that my analysis fails to measure.

    RECOVERY = RECOVERY.split('\n')
    RECOVERY = [1 - float(s) for s in RECOVERY]
    RECOVERY_LEN = len(RECOVERY)

else: # USE_GAMMA_MODEL
    RECOVERY_LEN = 30
    RECOVERY = []

    # Values shown in original study.
    # These don't exactly match the data files
    gamma = gamma(a=2.595, scale=4.48)

    # Attempt to match current data files.
    # stdev of the error is about 0.5%
    #
    #gamma = gamma(a=4.5, scale=3.012)

    # x = days to recover
    for x in range(0, RECOVERY_LEN):
        y_cum = gamma.cdf(x)
        RECOVERY.append(1 - y_cum)


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
    sys.exit("Usage: prevalence.py input.csv > output.csv")

with open(sys.argv[1]) as infile:
    write_prevalence(infile, sys.stdout)
