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
gamma = gamma(a=4.7, scale=2.88)

# Fit to UK. Except you can't do that, oops.
# You need to do each region seperately.
#gamma = gamma(a=3.79, scale=3.50)




# Work notes

#gamma = gamma(a=2.595, scale=4.48)

#gamma = gamma(a=3.795, scale=3.48)
#gamma = gamma(a=3.85, scale=3.52)
#gamma = gamma(a=3.85, scale=3.48)
#gamma = gamma(a=3.795, scale=3.52)

#gamma = gamma(a=3.75, scale=3.52)
#gamma = gamma(a=3.75, scale=3.56)
#gamma = gamma(a=3.70, scale=3.56)
#gamma = gamma(a=3.65, scale=3.60)
#gamma = gamma(a=3.65, scale=3.65)

#gamma = gamma(a=3.8, scale=3.56) # worse
#gamma = gamma(a=3.8, scale=3.52) # not as good

#gamma = gamma(a=3.75, scale=3.52)
#gamma = gamma(a=3.75, scale=3.54)
#gamma = gamma(a=3.77, scale=3.52)
#gamma = gamma(a=3.77, scale=3.50)
#gamma = gamma(a=3.79, scale=3.50) # pretty good!
#gamma = gamma(a=3.81, scale=3.50)
#gamma = gamma(a=3.79, scale=3.52)
#gamma = gamma(a=3.72, scale=3.54)
#gamma = gamma(a=3.72, scale=3.52)
#gamma = gamma(a=3.70, scale=3.52)
#gamma = gamma(a=3.71, scale=3.52)
#gamma = gamma(a=3.71, scale=3.54)
#gamma = gamma(a=3.71, scale=3.56)
#gamma = gamma(a=3.71, scale=3.58)
#gamma = gamma(a=3.75, scale=3.54)
#gamma = gamma(a=3.73, scale=3.54)
#gamma = gamma(a=3.74, scale=3.54)
#gamma = gamma(a=3.78, scale=3.50)
#gamma = gamma(a=3.78, scale=3.51)
#gamma = gamma(a=3.79, scale=3.51)
#gamma = gamma(a=3.80, scale=3.51)
#gamma = gamma(a=3.81, scale=3.51)
#gamma = gamma(a=3.84, scale=3.52)
#gamma = gamma(a=3.86, scale=3.52)
#gamma = gamma(a=3.85, scale=3.53)
#gamma = gamma(a=3.84, scale=3.54)
#gamma = gamma(a=3.87, scale=3.50)
#gamma = gamma(a=3.79, scale=3.54)
#gamma = gamma(a=3.87, scale=3.52)
#gamma = gamma(a=3.79, scale=3.58)

# London
#gamma = gamma(a=3.79, scale=3.50)
#gamma = gamma(a=3.85, scale=3.50)
#gamma = gamma(a=3.79, scale=3.90)
#gamma = gamma(a=3.79, scale=3.70)
#gamma = gamma(a=3.75, scale=3.80)
#gamma = gamma(a=3.75, scale=3.75)
#gamma = gamma(a=3.75, scale=3.70)
#gamma = gamma(a=3.9, scale=3.50)
#gamma = gamma(a=3.85, scale=3.60)
#gamma = gamma(a=3.85, scale=3.55)
#gamma = gamma(a=3.85, scale=3.54)
#gamma = gamma(a=3.79, scale=3.55)
#gamma = gamma(a=3.82, scale=3.55)
#gamma = gamma(a=3.82, scale=3.56)
#gamma = gamma(a=3.80, scale=3.58)
#gamma = gamma(a=3.83, scale=3.57)
#gamma = gamma(a=3.83, scale=3.565)
#gamma = gamma(a=3.83, scale=3.555)
#gamma = gamma(a=3.84, scale=3.545)
#gamma = gamma(a=3.85, scale=3.537)
#gamma = gamma(a=3.86, scale=3.528)
#gamma = gamma(a=3.88, scale=3.508)
#gamma = gamma(a=3.98, scale=3.408)
#gamma = gamma(a=4.1, scale=3.3)

#gamma = gamma(a=4.4, scale=3.0)
#gamma = gamma(a=4.4, scale=3.15)
#gamma = gamma(a=4.4, scale=3.1)
#gamma = gamma(a=4.2, scale=3.2)
#gamma = gamma(a=4.3, scale=3.12)
#gamma = gamma(a=4.3, scale=3.2)
#gamma = gamma(a=4.3, scale=3.14)
#gamma = gamma(a=4.3, scale=3.15) #g
#gamma = gamma(a=4.3, scale=3.16)
#gamma = gamma(a=4.2, scale=3.18)
#gamma = gamma(a=4.2, scale=3.19)
#gamma = gamma(a=4.2, scale=3.29)
#gamma = gamma(a=4.2, scale=3.20)
#gamma = gamma(a=4.2, scale=3.23) #g
#gamma = gamma(a=4.4, scale=3.09)
#gamma = gamma(a=4.4, scale=3.08) #g
#gamma = gamma(a=4.8, scale=2.5)
#gamma = gamma(a=4.8, scale=2.8)
#gamma = gamma(a=4.8, scale=2.81)
#gamma = gamma(a=4.8, scale=2.82) #g
#gamma = gamma(a=5.2, scale=2.55) #b
#gamma = gamma(a=4.9, scale=2.7) #b
#gamma = gamma(a=4.7, scale=2.93)
#gamma = gamma(a=4.7, scale=2.83)
#gamma = gamma(a=4.7, scale=2.88) #g g
#gamma = gamma(a=4.55, scale=2.80)
#gamma = gamma(a=4.55, scale=2.83)
#gamma = gamma(a=4.55, scale=2.98) #g
#gamma = gamma(a=4.6, scale=2.93)
#gamma = gamma(a=4.6, scale=2.95) #g
#gamma = gamma(a=4.5, scale=3.0)
#gamma = gamma(a=4.5, scale=3.03)
#gamma = gamma(a=4.5, scale=3.015) #g
#gamma = gamma(a=4.8, scale=2.819)
#gamma = gamma(a=4.6, scale=2.945)

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
