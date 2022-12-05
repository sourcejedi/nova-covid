#!/usr/bin/python3
# Based on prevalence_from_incidence/prevalence.py
# Now calculates for all regions and all available input files.
#
# Relevant documentation:
#  * Extended comments at the top of the original script.
#  * More recent exceptions defined in the code here: check_p_from_i.py
#  * Comments in jump.txt

import csv
import math
import sys
from pathlib import Path

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
    
    # Recovery model, extracted by taking advantage of zeroes
    # in Northern Ireland region of *_history_20210510.csv.

    RECOVERY = RECOVERY_STR.split('\n')
    RECOVERY = [1 - float(s) for s in RECOVERY]
    RECOVERY_LEN = len(RECOVERY)

# date = ISO date
# incidence = absolute incidence, i.e. number of new occurences
#
def read_incidence(infile):
    regions = {}
    dates = []
    
    csv_in = csv.DictReader(infile)
    for row in csv_in:
        region = row['region']
        date = row['date']
        incidence = float(row.get('pop_mid') or row.get('covid_in_pop'))
        v = regions.get(region, None)
        if v is None:
            v = []
            regions[region] = v
        v.append(incidence)
        if len(v) > len(dates):
            dates.append(date)
        else:
            assert date == dates[-1]
    return (dates, regions)

def calc_prevalence(incidences):
    window = []
    for i in range(RECOVERY_LEN - 1):
        incidence = next(incidences)
        window.append(incidence)

    for incidence in incidences:
        window.append(incidence)

        prevalence = 0
        for i in range(0, RECOVERY_LEN):
            prevalence += window[RECOVERY_LEN-1-i] * RECOVERY[i]
        yield prevalence
        del window[0]

def write_prevalence(file_in, file_out):
    prevalences = {}
    (dates, incidences) = read_incidence(file_in)
    for region in incidences:
        prevalences[region] = list(calc_prevalence(iter(incidences[region])))
    regions = sorted(incidences.keys())

    csv_out = csv.writer(file_out)
    csv_out.writerow(['date', 'region', 'active_cases'])
    eaten = RECOVERY_LEN - 1
    for i in range(len(dates) - eaten):
        for region in regions:
            csv_out.writerow([dates[i+eaten], region, prevalences[region][i]])


init_recovery()

outdir = Path('out/prevalence_from_incidence_/')
outdir.mkdir(parents=True, exist_ok=True)

indir = Path('download/incidence/')
prefix = 'incidence_'
paths = list(indir.glob(prefix + '*.csv'))
paths.sort()
for path in paths:
    filename = path.name[len(prefix):]
    out_path = outdir / filename
    if out_path.exists():
        continue
    print (path.name)
    with (path.open() as csvfile_in,
          out_path.open('w') as csvfile_out):
        write_prevalence(csvfile_in, csvfile_out)


outdir = Path('out/prevalence_from_incidence_history_/')
outdir.mkdir(parents=True, exist_ok=True)

indir = Path('download/incidence_history/')
prefix = 'incidence_history_'
paths = list(indir.glob(prefix + '*.csv'))
paths.sort()
for path in paths:
    filename = path.name[len(prefix):]
    out_path = outdir / filename
    if out_path.exists():
        continue
    print (path.name)
    with (path.open() as csvfile_in,
          out_path.open('w') as csvfile_out):
        write_prevalence(csvfile_in, csvfile_out)
