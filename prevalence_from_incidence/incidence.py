#!/usr/bin/python3

import csv
import math
from scipy.stats import gamma
import sys

def iter_rows(infile):
    inc_reader = csv.DictReader(infile)
    for row in inc_reader:
        yield row

# { ISO date, absolute incidence i.e. number of new occurences }
def iter_incidence(infile, region):
    for row in iter_rows(infile):
        if region is None and 'region' in row.keys():
            sys.exit("Please pass a region to select")
        if 'region' in row.keys() and row['region'] != region:
            continue
            
        pop_mid = float(row.get('pop_mid') or row.get('covid_in_pop'))
        #assert pop_mid == int(pop_mid)
        #pop_mid = int(pop_mid)

        yield {'date': row['date'], 'incidence_mid': pop_mid}


# Recovery model (days)
RECOVERY_LEN=30
RECOVERY=[]

# Values shown in original study.
# These don't exactly match current data files
#gamma = gamma(a=2.595, scale=4.48)

# Match current data files.
# stdev of the error is about 0.5%
#
# Both of these work.  Second one was trained on
# the data file which is longer & more recent &
# which provides fractional incidence.
#
#gamma = gamma(a=4.7, scale=2.88)
gamma = gamma(a=4.5, scale=3.012)

# Fit to UK. Except you can't do that, oops.
# You need to do each region seperately.
#gamma = gamma(a=3.79, scale=3.50)


# x = days to recover
y_cum = 0
for x in range(0, RECOVERY_LEN):
    y = gamma.pdf(x)
    y_cum = gamma.cdf(x)
    #print (y,y_cum)
    RECOVERY.append(1-y_cum)

def prevalence(infile, region):
    incidences = list(iter_incidence(infile, region))
    dates = list(map(lambda r: r['date'], incidences))
    incidences = list(map(lambda r: r['incidence_mid'], incidences))
    
    window = incidences[:RECOVERY_LEN-1]
    for i in range(RECOVERY_LEN-1, len(incidences)):
        incidence = incidences[i]
        window.append(incidence)
        
        prevalence = 0
        for j in range(0, RECOVERY_LEN):
            prevalence += window[RECOVERY_LEN-1-j] * RECOVERY[j]
        yield (dates[i], incidence, prevalence)
        del window[0]
        

region = None
if len(sys.argv) == 2:
    region = sys.argv[1]
if len(sys.argv) > 2:
    sys.exit("Usage: ./incidence.py [REGION] < input.csv > output.csv")

w = csv.writer(sys.stdout)
w.writerows(prevalence(sys.stdin, region))
