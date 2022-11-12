#!/usr/bin/env python3
#
# This takes a minute or so on first run.
# Successive runs are quicker, as we only check new files.

import csv
import datetime
import errno
import os
import numpy as np
from pathlib import Path

def read_prevalence(infile):
    regions = {}
    dates = []

    csv_in = csv.DictReader(infile)
    for row in csv_in:
        region = row['region']
        date = row['date']
        incidence = float(row.get('active_cases'))
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


def check_prevalence_from_incidence(official_file, check_file,
                                    check_path, datename, tolerance):
    (_, official_regions) = read_prevalence(official_file)
    (check_dates, check_regions) = read_prevalence(check_file)

    # The split regions didn't match, and official prevalences looked much
    # less smooth than other regions).  I expect the split was determined
    # using symptom-based prevalence ("P_A" in the hotspots paper).
    if datename < '20220131':
        def unsplit(regions):
            north_east = np.array(regions.pop('North East'))
            yorks = np.array(regions.pop('Yorkshire and The Humber'))
            regions['North East and Yorkshire'] = north_east + yorks

            east_mid = np.array(regions.pop('East Midlands'))
            west_mid = np.array(regions.pop('West Midlands'))
            regions['Midlands'] = east_mid + west_mid

        unsplit(official_regions)
        unsplit(check_regions)

    # Before 202111217, official incidence estimates waited 4 days to get
    # test results, but prevalence estimates only waited 2 days.
    if datename < '20211217':
        skip = 2
    else:
        skip = 0

    mindev = float('inf')
    maxdev = 0
    totdev = 0
    n = 0
    for region in official_regions:
        official_prevalence = official_regions[region]
        check_prevalence = check_regions[region]

        # we don't bother with nominal dates, just compare from the end

        l = min(len(official_prevalence), len(check_prevalence))
        for i in range(-1, -1 - (l - skip), -1):
            if official_prevalence[i - skip]:
                diff = abs(official_prevalence[i - skip] - check_prevalence[i])
                if diff > tolerance:
                    print ('CHECK FAILED', (check_path, check_dates[i],
                           region, check_prevalence[i], official_prevalence[i - skip]))
                    return False
    return True


# Skip already-checked files
os.makedirs('out', exist_ok=True)
try:
    with open('out/check.txt') as check_file:
        checked = set((line.rstrip() for line in check_file.readlines()))
except OSError as e:
    if e.errno != errno.ENOENT:
        raise
    checked = set()

checkdir = Path('out/prevalence_from_incidence_/')

# Iterate on prevalence_history, because prevalence_history_DATE.csv
# goes back further than incidence_DATE.csv
indir = Path('download/prevalence_history/')
prefix = 'prevalence_history_'
paths = list(indir.glob(prefix + '*.csv'))
paths.sort()
paths.reverse()
for path in paths:
    datename = path.name[len(prefix):-4]

    # Doesn't match on these dates.
    #
    # On 20220708, there was a weird pattern in incidence which was
    # removed after a short time.  Maybe prevalence wasn't regenerated.
    #
    # 20220725 is when the data files start being updated before 9 AM.
    # Perhaps there was some teething problem.
    if datename in ['20220725', '20220708']:
       continue

    # offset between dates in filenames
    if datename < '20211217':
        offset = -4
    else:
        offset = -2

    date = [int(d) for d in [datename[:-4], datename[-4:-2], datename[-2:]]]
    date = datetime.date(*date)
    date = date + datetime.timedelta(days=offset)
    date = f'{date.year:04}{date.month:02}{date.day:02}'

    # incidence was rounded to nearest whole number
    if date >= '20200903' and date < '20210717':
        tolerance = 15
    else:
        tolerance = 1e-8

    # incidence csv changed method one day before prevalence csv
    # so they do not match.
    if date == '20210507':
        continue

    check_name = date + '.csv'
    check_path = checkdir / check_name
    if str(check_path) in checked:
        continue

    with (path.open() as official_file,
          check_path.open() as check_file):
        if check_prevalence_from_incidence(official_file, check_file,
                                           str(check_path), datename, tolerance):
            checked.add(str(check_path))


checkdir = Path('out/prevalence_from_incidence_history_/')

indir = Path('download/prevalence_history/')
prefix = 'prevalence_history_'
paths = list(indir.glob(prefix + '*.csv'))
paths.sort()
paths.reverse()
for path in paths:
    if str(path) in checked:
        continue

    datename = path.name[len(prefix):-4]

    # incidence history csv changed method one day after prevalence csv
    # so they do not match.
    if datename == '20210721':
        continue

    # incidence history csv was not changed for method v3
    if datename >= '20210512' and datename < '20210721':
        continue

    check_name = f'{datename}.csv'
    check_path = checkdir / check_name
    with (path.open() as official_file,
          check_path.open() as check_file):
        if check_prevalence_from_incidence(official_file, check_file,
                                           str(check_path), datename, 1e-8):
            checked.add(str(check_path))

with open('out/check.txt', 'w') as check_file:
    for c in sorted(checked):
        check_file.write(c)
        check_file.write('\n')
