#!/bin/env python3

import csv
from pathlib import Path

def std_form(input_file, output_file):
    head = next(input_file)
    head = head.rstrip()
    heads = head.split(',')
    
    date_field = heads.index('date')
    try:
        covid_in_pop_field = heads.index('covid_in_pop')
        covid_in_pop_lo_field = heads.index('covid_in_pop_lo')
        covid_in_pop_up_field = heads.index('covid_in_pop_up')
    except ValueError:
        covid_in_pop_field = heads.index('pop_mid')
        covid_in_pop_lo_field = heads.index('pop_low')
        covid_in_pop_up_field = heads.index('pop_up')
        
    max_fields = max(date_field,
                     covid_in_pop_field,
                     covid_in_pop_lo_field,
                     covid_in_pop_up_field)

    writer = csv.writer(output_file)
    writer.writerow(['date', 'covid_in_pop', 'covid_in_pop_lo', 'covid_in_pop_up'])
    
    for line in input_file:
        line = line.rstrip()
        
        # using maxsplit actually makes this 50% *slower* ?!
        #line = line.split(',', max_fields)
        line = line.split(',')
        
        writer.writerow([line[date_field],
                         line[covid_in_pop_field],
                         line[covid_in_pop_lo_field],
                         line[covid_in_pop_up_field]])


outdir = Path('out/incidence.std_form/')
outdir.mkdir(parents=True, exist_ok=True)

indir = Path('download/incidence/')
paths = list(indir.glob('*.csv'))
for path in paths:
    filename = path.name
    with (path.open() as csvfile_in,
         (outdir / filename).open('w') as csvfile_out):
        std_form(csvfile_in, csvfile_out)
