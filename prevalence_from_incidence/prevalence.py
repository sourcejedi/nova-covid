#!/usr/bin/python3

# Configuration variable - choose the recovery model.

# Use recovery vector reverse-engineered from comparing data files.
# Or use a gamma distribution model, like the "hotspots" paper.
# See code below for parameters and comments.
USE_GAMMA_MODEL=False


# This script can now reproduce ZOE prevalence estimates
# from the ZOE incidence estimates.
#
# Notes:
#
# 1. ZOE prevalence_history_*.csv does not include values for
#    "England", only the sub-regions of England.
#
#    In incidence estimates published before 2021-07-17 ("method v4"),
#    "England" does not equal the sum of the English regions.
#
# 2. For files before prevalence_history_20220131.csv (2022-01-31),
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
# 3. The earliest data file available to reproduce is
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
# 4. Using incidence_20210205.csv will not reproduce the exact output.
#    In incidence_*.csv files around this date, the central estimate
#    is rounded to the nearest whole number.  I believe exact
#    reproduction is possible by multiplying the "100k_mid" collumn by
#    population (taken from the "incidence table.csv" published the same
#    day).
#
#    On the other hand, it provides dates earlier than those included
#    in prevalence_history.  The earlier dates are also graphed in the
#    "hotspot" paper, showing very similar results.
#
# 5. The recovery vector used to obtain these results (below) is
#    clearly different from the recovery curve in Figure 2 of the
#    "hotspot" paper.  I have asked the authors if they can explain this.
#
# 6. Some rows in the prevalence_history series show unexpected
#    zeroes, i.e. completely outside the trend.  I do not reproduce
#    these zeroes.  This seems to be a limitation of the official
#    files.


import csv
import math
import sys


RECOVERY_STR = """0
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

def init_recovery():
    global RECOVERY, RECOVERY_LEN
    
    if not USE_GAMMA_MODEL:
        # Recovery model, extracted by taking advantage of zeroes
        # in Northern Ireland region of *_history_20210510.csv.

        RECOVERY = RECOVERY_STR.split('\n')
        RECOVERY = [1 - float(s) for s in RECOVERY]
        RECOVERY_LEN = len(RECOVERY)

    else: # USE_GAMMA_MODEL
        from scipy.stats import gamma

        RECOVERY_LEN = 30
        RECOVERY = []

        # Values shown in original study.
        # These don't exactly match the data files
        gamma = gamma(a=2.595, scale=4.48)

        # Attempt to match current data files.
        # stdev of the error is reduced to about 0.5%
        #
        #gamma = gamma(a=4.5, scale=3.012)

        # x = days to recover
        for x in range(0, RECOVERY_LEN):
            y_cum = gamma.cdf(x)
            RECOVERY.append(1 - y_cum)


# Iterator of (date, incidence)
# date = ISO date
# incidence = absolute incidence, i.e. number of new occurences
#
def iter_incidence(infile, region=None):
    csv_in = csv.DictReader(infile)
    for row in csv_in:
        if region is None:
            if 'region' in row.keys():
                sys.exit("Please pass a region to select")
        else: # region is not None
            if 'region' not in row.keys():
                sys.exit(f"Input file does not have a region column, but you requested the specific region '{region}'")
            # Skip rows which do not match the region
            if row['region'] != region:
                continue

        date = row['date']
        incidence = float(row.get('pop_mid') or row.get('covid_in_pop'))
        yield (date, incidence)

# Iterator of (date, incidence, prevalence)
def iter_prevalence(incidences):
    window = []
    for i in range(RECOVERY_LEN - 1):
        (date, incidence) = next(incidences)
        window.append(incidence)

    for (date, incidence) in incidences:
        window.append(incidence)

        prevalence = 0
        for i in range(0, RECOVERY_LEN):
            prevalence += window[RECOVERY_LEN-1-i] * RECOVERY[i]
        yield(date, incidence, prevalence)
        del window[0]

def write_prevalence(file_in, file_out, region=None):
    csv_out = csv.writer(file_out)
    incidences = iter_incidence(file_in, region)
    prevalences = iter_prevalence(incidences)
    csv_out.writerows(prevalences)

region = None
if len(sys.argv) > 1 and sys.argv[1] == '--use-gamma':
    USE_GAMMA_MODEL=True
    del sys.argv[1]
if len(sys.argv) == 2:
    region = sys.argv[1]
if len(sys.argv) > 2:
    sys.exit("Usage: prevalence.py [--use-gamma] [REGION] < input.csv > output.csv")

init_recovery()
write_prevalence(sys.stdin, sys.stdout, region)
