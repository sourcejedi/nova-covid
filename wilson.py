#!/usr/bin/env python3

import csv
from pathlib import Path

# https://www.mikulskibartosz.name/wilson-score-in-python-example/
from math import sqrt
def wilson(p, n, z = 1.96):
    denominator = 1 + z**2/n
    centre_adjusted_probability = p + z*z / (2*n)
    adjusted_standard_deviation = sqrt((p*(1 - p) + z*z / (4*n)) / n)

    lower_bound = (centre_adjusted_probability - z*adjusted_standard_deviation) / denominator
    upper_bound = (centre_adjusted_probability + z*adjusted_standard_deviation) / denominator
    return (lower_bound, upper_bound)

def run(indir, outfile):
    writer = csv.writer(outfile)
    writer.writerow(['date', 'region', 'est. daily cases',
                     'lower lim. -%',
                     'upper lim. +%',
                     'wilson interval -%',
                     'wilson interval +%'])

    prefix = 'incidence table_'
    prefix_len = len(prefix)
    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()
    for path in paths:
            name = path.name[prefix_len:-4]

            # hack. this thing is about methods v1 to v3
            # and the initial incidence tables for v4 were broken anyway
            # so lets just cut it off there
            if name >= '20210721':
                break

            date = '-'.join([name[:-4], name[-4:-2], name[-2:]])
            with path.open() as f:
                read = csv.DictReader(f)
                def get_region(row):
                    return row.get('region') or row.get('nhser19nm')

                for row in read:
                    region = get_region(row)
                    cases = int(row.get('est. daily\ncases'))
                    cases_lo = int(row.get('est. daily\ncases\n95% lower lim.'))
                    cases_up = int(row.get('est. daily\ncases\n95% upper lim.'))

                    tests = row.get('# total tests')
                    if tests == 'N/A':
                        continue
                    tests = int(tests)
                    positives = int(row.get('# +ve tests'))
                    p = positives/tests
                    (p_lo,p_up) = wilson(p, tests)

                    def percent(mid, lim):
                        return str(((lim/mid)-1)*100)+'%'
                    #print(date+' '+region+' '+str(p))
                    #percent(p, p_lo)
                    if p == 0:
                        continue
                    writer.writerow([date, region, cases,
                                     percent(cases, cases_lo),
                                     percent(cases, cases_up),
                                     percent(p, p_lo),
                                     percent(p, p_up)])

outdir = Path('out/')
outdir.mkdir(parents=True, exist_ok=True)

indir = Path('download-sample/incidence table/')
with open(outdir / 'wilson.csv', 'w') as outfile:
    run(indir, outfile)
